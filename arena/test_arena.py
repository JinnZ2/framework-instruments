#!/usr/bin/env python3
"""Arena tests: grading refusal, schema, masking chains, one real probe, undecidable claim."""

import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "instruments"))
import runrecord  # noqa: E402
import report  # noqa: E402
import path_probe  # noqa: E402

SPEC = {"specimen_id": "S1", "package": "p", "defect_text": "d", "surface_signal": "test green",
        "actual_path": "a", "intended_path": "b", "detector_exercised": False, "masked_by": None,
        "found_by": "f", "grade": "false", "absent_behaviour": False, "settled_by": None}


class TestArena(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.cwd = os.getcwd()
        os.chdir(self.tmp)

    def tearDown(self):
        os.chdir(self.cwd)
        for f in os.listdir(self.tmp):
            os.remove(os.path.join(self.tmp, f))
        os.rmdir(self.tmp)

    def last(self):
        return [r for _, r in runrecord.read_jsonl("runs.jsonl")][-1]

    def test_two_state_grading_is_void(self):
        runrecord.write_jsonl("s.jsonl", [SPEC, dict(SPEC, specimen_id="S2", grade="true")])
        runrecord.write_jsonl("p.jsonl", [])
        self.assertEqual(report.main(["report.py", "s.jsonl", "p.jsonl", "r.md"]), 2)
        self.assertEqual(self.last()["status"], "void")
        self.assertFalse(os.path.exists("r.md"))
        runrecord.write_jsonl("s.jsonl", [SPEC, dict(SPEC, specimen_id="S2", grade="undifferentiated", settled_by="probe it")])
        self.assertEqual(report.main(["report.py", "s.jsonl", "p.jsonl", "r.md"]), 0)
        with open("r.md") as fh:
            text = fh.read()
        heads = [l for l in text.splitlines() if l.startswith("## ")]
        self.assertEqual([h[:5] for h in heads], ["## 1.", "## 2.", "## 3.", "## 4.", "## 5.", "## 6."])
        self.assertIn("**2** specimens have `detector_exercised: false`", text)
        self.assertIn("S2: probe it", text)

    def test_schema_and_masking_chain(self):
        bad = dict(SPEC, grade="green")
        runrecord.write_jsonl("s.jsonl", [bad])
        self.assertEqual(report.main(["report.py", "s.jsonl", "p.jsonl", "r.md"]), 1)
        self.assertIn("line 1", self.last()["notes"])
        runrecord.write_jsonl("s.jsonl", [SPEC, dict(SPEC, specimen_id="S2", masked_by="S9")])
        self.assertEqual(report.main(["report.py", "s.jsonl", "p.jsonl", "r.md"]), 1)
        self.assertIn("not a specimen", self.last()["notes"])
        chainset = [SPEC, dict(SPEC, specimen_id="S2", masked_by="S1", grade="partial"),
                    dict(SPEC, specimen_id="S3", masked_by="S2", grade="undifferentiated", absent_behaviour=True)]
        runrecord.write_jsonl("s.jsonl", chainset)
        report.main(["report.py", "s.jsonl", "p.jsonl", "r.md"])
        with open("r.md") as fh:
            text = fh.read()
        self.assertIn("S3 <- masked by S2 <- masked by S1", text)
        self.assertIn("2 masked specimens; 2 distinct upstream maskers", text)
        self.assertIn("Absent behaviour (1;", text)

    def test_shipped_specimens_load_and_report(self):
        code = report.main(["report.py", os.path.join(HERE, "specimens.jsonl"), "none.jsonl", "r.md"])
        self.assertEqual(code, 0)
        rec = self.last()
        self.assertEqual(rec["status"], "ok")
        self.assertIn("probe_results missing", rec["notes"])
        self.assertGreater(rec["counts"]["detector_not_exercised"], 0)

    def test_probe_exercised_and_undecidable(self):
        claims = [{"test": "test_b2.TestB2.test_release_refused_without_commit",
                   "module": "instruments/b2-audit-isolation/b2_lock.py", "guard": "c is None", "branch": "if"},
                  {"test": "test_b2.TestB2.test_release_refused_without_commit",
                   "module": "instruments/b2-audit-isolation/b2_lock.py", "guard": "no_such_guard", "branch": "if"}]
        runrecord.write_jsonl("c.jsonl", claims)
        self.assertEqual(path_probe.main(["path_probe.py", "c.jsonl", "3", "out.jsonl"]), 0)
        rows = {r["guard"]: r for _, r in runrecord.read_jsonl("out.jsonl")}
        self.assertIs(rows["c is None"]["still_passes"], False)
        self.assertTrue(rows["c is None"]["baseline_passes"])
        self.assertIsNone(rows["no_such_guard"]["still_passes"])
        self.assertEqual(rows["no_such_guard"]["guard_matches"], 0)
        self.assertTrue(all(r["seed"] == 3 for r in rows.values()))
        self.assertEqual(self.last()["counts"], {"claims": 2, "still_passes_true": 0, "still_passes_false": 1, "undecidable": 1})

    def test_probe_detects_an_unexercised_branch(self):
        claims = [{"test": "test_b1.TestB1.test_permutation_preserves_count_and_multiset",
                   "module": "instruments/b1-runner-up-trace/b1_permute.py", "guard": "len(positions) < 2", "branch": "if"}]
        runrecord.write_jsonl("c.jsonl", claims)
        path_probe.main(["path_probe.py", "c.jsonl", "1", "out.jsonl"])
        row = [r for _, r in runrecord.read_jsonl("out.jsonl")][0]
        self.assertIs(row["still_passes"], True)
        self.assertEqual(row["specimen"]["grade"], "false")
        self.assertFalse(row["specimen"]["detector_exercised"])


if __name__ == "__main__":
    unittest.main()
