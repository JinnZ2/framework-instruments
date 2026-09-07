#!/usr/bin/env python3
"""Tests for unfold_score.py: both response forms, absent-is-null, controls, status paths."""

import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
import runrecord  # noqa: E402
import unfold_score as us  # noqa: E402

CONTRACT = """Frame diagnosis: CORRUPT
Stipulated facts: [the gate exists; the town is downstream; the auxiliary spillway was tested]
Hidden assumptions: [only two gates exist]
Failure map:
EPI-01 | supported | two options stated, a third stipulated | none
INF-02 | contradicted | an auxiliary spillway is stated operable | test record
GOV-08 | unknown | no warning history is given | notice records
ZZZ-99 | maybe | not a pattern | not a state
Alternative space: [auxiliary spillway]
Reframed question: [why is the auxiliary spillway outside the question]
"""


class TestUnfoldScore(unittest.TestCase):
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

    def test_contract_form_counts_and_declared_control(self):
        with open("r.md", "w") as fh:
            fh.write(CONTRACT)
        self.assertEqual(us.main(["unfold_score.py", "r.md", "CORRUPT", "s.jsonl"]), 0)
        row = [r for _, r in runrecord.read_jsonl("s.jsonl")][0]
        self.assertEqual((row["form"], row["verdict"], row["matches_expected"]), ("contract", "CORRUPT", True))
        self.assertEqual((row["pattern_rows"], row["patterns_supported"], row["patterns_contradicted"], row["patterns_unknown"]), (4, 1, 1, 1))
        self.assertEqual((row["patterns_invalid_state"], row["patterns_unknown_id"]), (1, 1))
        self.assertEqual(row["list_items"]["Stipulated facts"], 3)
        self.assertEqual(row["list_items"]["Hidden assumptions"], 1)
        self.assertEqual(us.main(["unfold_score.py", "r.md", "LEGITIMATE", "s2.jsonl"]), 0)
        self.assertIs([r for _, r in runrecord.read_jsonl("s2.jsonl")][0]["matches_expected"], False)

    def test_example_form_and_absent_is_null(self):
        example = os.path.join(HERE, "examples", "ai-shutdown.md")
        self.assertEqual(us.main(["unfold_score.py", example, "-", "s.jsonl"]), 0)
        row = [r for _, r in runrecord.read_jsonl("s.jsonl")][0]
        self.assertEqual((row["form"], row["verdict"], row["expected_verdict"], row["matches_expected"]), ("example", "INCOMPLETE", None, None))
        self.assertEqual((row["patterns_supported"], row["patterns_contradicted"], row["patterns_unknown"]), (1, 0, 99))
        self.assertIsNone(row["list_items"])  # the example form has no contract lists; absent, not 0
        with open("prose.md", "w") as fh:
            fh.write("A response that mentions INF-01 in passing and gives no verdict line.\n")
        self.assertEqual(us.main(["unfold_score.py", "prose.md", "-", "s3.jsonl"]), 2)
        row = [r for _, r in runrecord.read_jsonl("s3.jsonl")][0]
        self.assertEqual((row["form"], row["verdict"], row["pattern_rows"]), (None, None, 0))
        self.assertEqual(self.last()["status"], "void")

    def test_status_paths(self):
        with open("e.md", "w") as fh:
            fh.write(" \n")
        self.assertEqual(us.main(["unfold_score.py", "e.md", "-", "s.jsonl"]), 0)
        self.assertEqual(self.last()["status"], "empty")
        self.assertEqual(us.main(["unfold_score.py", "missing.md", "-", "s.jsonl"]), 1)
        self.assertEqual(self.last()["status"], "error")
        with open("r.md", "w") as fh:
            fh.write(CONTRACT)
        self.assertEqual(us.main(["unfold_score.py", "r.md", "MAYBE", "s.jsonl"]), 1)
        self.assertIn("expected_verdict", self.last()["notes"])

    def test_controls_declare_distinct_verdicts_before_any_run(self):
        rows = [r for _, r in runrecord.read_jsonl(os.path.join(HERE, "controls", "controls.jsonl"))]
        self.assertEqual({r["expected_verdict"] for r in rows}, {"LEGITIMATE", "CORRUPT"})
        for r in rows:
            with open(os.path.join(HERE, "controls", r["file"]), encoding="utf-8") as fh:
                self.assertTrue(fh.read().startswith("Constructed control."))

    def test_no_forbidden_field(self):
        with open("r.md", "w") as fh:
            fh.write(CONTRACT)
        us.main(["unfold_score.py", "r.md", "-", "s.jsonl"])
        for _, row in runrecord.read_jsonl("s.jsonl"):
            for f in ("label", "category", "type", "interpretation"):
                self.assertNotIn(f, row)


if __name__ == "__main__":
    unittest.main()
