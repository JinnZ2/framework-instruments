#!/usr/bin/env python3
"""Status-path floor: every script's empty and error paths through the run record,
plus the B4 ok paths the per-package suites reach only through library calls."""

import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
for d in ("b1-runner-up-trace", "b2-audit-isolation", "b3-split-authorship", "b4-dilemma-reconstruction"):
    sys.path.insert(0, os.path.join(HERE, d))
sys.path.insert(0, HERE)
import runrecord  # noqa: E402
import b1_schema, b1_score, b1_permute, b1_summarise, b1_report  # noqa: E402,E401
import b2_conditions, b2_order, b2_lock, b2_agree  # noqa: E402,E401
import b3_split, b3_join, b3_arms  # noqa: E402,E401
import items, requirements, reconstruct, agree, agreement, nullshuffle, calibrate, grade, report  # noqa: E402,E401

E, BAD = "empty.jsonl", "bad.jsonl"
# (module, entry, argv after the script name, expected status)
EMPTY = [
    (b1_schema, "main", ["b1_schema.py", E, E]), (b1_score, "main", ["b1_score.py", E, E, "o.jsonl"]),
    (b1_permute, "main", ["b1_permute.py", E, "1", "o.jsonl"]), (b1_report, "main", ["b1_report.py", E, E, "r.md"]),
    (b2_conditions, "main", ["b2_conditions.py", E, "pres"]), (b2_order, "main", ["b2_order.py", "0", "1", "o.jsonl"]),
    (b2_agree, "main", ["b2_agree.py", E, E, "a.jsonl", "c.jsonl"]),
    (b3_split, "main", ["b3_split.py", "case", E, "brief.txt", "out"]), (b3_split, "main", ["b3_split.py", "key", E, "out"]),
    (b3_join, "main", ["b3_join.py", E, E, "split", "o.jsonl"]), (b3_arms, "main", ["b3_arms.py", E, "single", "o.jsonl"]),
    (reconstruct, "main", ["reconstruct.py", E, E, "out"]),
    (agree, "main", ["agree.py", E, E, "o.jsonl"]), (agreement, "cli", ["agreement.py", E, E, "src", "o.jsonl"]),
    (calibrate, "main", ["calibrate.py", E, E, E, "o.jsonl"]),
    (grade, "main", ["grade.py", E, "o.jsonl"]),
]
ERROR = [
    (b1_permute, "main", ["b1_permute.py", BAD, "1", "o.jsonl"]), (b1_summarise, "main", ["b1_summarise.py", BAD, "o.jsonl"]),
    (b1_report, "main", ["b1_report.py", BAD, E, "r.md"]), (b2_order, "main", ["b2_order.py", "-1", "1", "o.jsonl"]),
    (b2_lock, "main", ["b2_lock.py", "commit", "commits.jsonl", "R2", "c1", "missing.txt"]),
    (b2_lock, "main", ["b2_lock.py", "release", "commits.jsonl", BAD, "R1", "c1", "k.jsonl"]),
    (b2_conditions, "main", ["b2_conditions.py", BAD, "pres"]),
    (items, "main", ["items.py", BAD, "o.jsonl"]), (requirements, "main", ["requirements.py", BAD, "o.jsonl"]),
    (reconstruct, "main", ["reconstruct.py", BAD, E, "out"]), (agree, "main", ["agree.py", BAD, E, "o.jsonl"]),
    (agreement, "cli", ["agreement.py", BAD, E, "src", "o.jsonl"]), (nullshuffle, "main", ["nullshuffle.py", BAD, "1", "o.jsonl"]),
    (calibrate, "main", ["calibrate.py", BAD, E, E, "o.jsonl"]), (grade, "main", ["grade.py", BAD, "o.jsonl"]),
    (report, "cli", ["report.py", BAD, E, E, E, E, E, "r.md"]),
]


def req(item, rid, n, status="true", st="measure X"):
    return {"item_id": item, "reconstructor_id": rid, "req_id": f"{rid}-{n}", "requirement_text": f"text {rid} {n}",
            "status": status, "settling_test": st, "layer": "physical"}


class TestStatusPaths(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.cwd = os.getcwd()
        os.chdir(self.tmp)
        runrecord.write_jsonl(E, [])
        with open(BAD, "w") as fh:
            fh.write("{not json\n")
        with open("brief.txt", "w") as fh:
            fh.write("brief\n")
        with open("commits.jsonl", "w") as fh:
            fh.write('{"reader_id": "R1", "case_id": "c1", "sha256": "%s", "response_text": "x"}\n' % runrecord.sha256_text("x"))

    def tearDown(self):
        os.chdir(self.cwd)
        for root, dirs, files in os.walk(self.tmp, topdown=False):
            for f in files:
                os.remove(os.path.join(root, f))
            for d in dirs:
                os.rmdir(os.path.join(root, d))
        os.rmdir(self.tmp)

    def last(self):
        return [r for _, r in runrecord.read_jsonl("runs.jsonl")][-1]

    def test_empty_inputs_record_empty(self):
        for mod, entry, argv in EMPTY:
            self.assertEqual(getattr(mod, entry)(argv), 0, argv)
            self.assertEqual(self.last()["status"], "empty", argv)

    def test_items_empty_is_recorded_as_error_by_its_own_logic(self):
        # B4 defect left in place (logic not rewritten): items.validate prints arms.pop()
        # on an empty set, so an empty input lands on the error row, never on empty.
        # A repair turns this red, which is the point of pinning it.
        self.assertEqual(items.main(["items.py", E, "o.jsonl"]), 1)
        self.assertEqual(self.last()["status"], "error")
        self.assertIn("KeyError", self.last()["notes"])
        # nullshuffle refuses fewer than two items (a derangement needs two), so its
        # empty path is an error row by its own rule as well.
        self.assertEqual(nullshuffle.main(["nullshuffle.py", E, "1", "o.jsonl"]), 1)
        self.assertEqual(self.last()["status"], "error")

    def test_requirements_empty_is_void_by_its_own_rule(self):
        self.assertEqual(requirements.main(["requirements.py", E, "o.jsonl"]), 2)
        self.assertEqual(self.last()["status"], "void")  # an empty status set is a subset of {true, false}

    def test_malformed_inputs_record_error(self):
        for mod, entry, argv in ERROR:
            self.assertEqual(getattr(mod, entry)(argv), 1, argv)
            self.assertEqual(self.last()["status"], "error", argv)

    def test_b4_ok_paths_through_main(self):
        item = {"item_id": "i1", "source": "s", "text_verbatim": "t", "branches_stated": 2, "arm": "documented"}
        runrecord.write_jsonl("items.jsonl", [item])
        reqs = [req("i1", "r1", 1), req("i1", "r1", 2, "partial", "count Y"), req("i1", "r2", 1), req("i1", "r2", 2, "unknown", "count Y"),
                req("i2", "r1", 3), req("i2", "r2", 3)]  # two items: the shuffle null is a derangement across items
        runrecord.write_jsonl("reqs.jsonl", reqs)
        runrecord.write_jsonl("matches.jsonl", [{"item_id": "i1", "req_a": "r1-1", "req_b": "r2-1", "matched": True}])
        runrecord.write_jsonl("factors.jsonl", [{"item_id": "i1", "factor_id": "f1", "factor_text": "measure X"}])
        self.assertEqual(agree.main(["agree.py", "reqs.jsonl", "matches.jsonl", "agr.jsonl"]), 0)
        self.assertEqual(self.last()["status"], "ok")
        self.assertEqual(agreement.cli(["agreement.py", "reqs.jsonl", "matches.jsonl", "hand", "agr2.jsonl"]), 0)
        self.assertEqual((self.last()["status"], self.last()["notes"]), ("ok", "match_source=hand"))
        self.assertEqual(calibrate.main(["calibrate.py", "reqs.jsonl", "factors.jsonl", "items.jsonl", "cal.jsonl"]), 0)
        self.assertEqual(self.last()["status"], "ok")
        self.assertEqual(grade.main(["grade.py", "reqs.jsonl", "grades.jsonl"]), 0)
        self.assertEqual(nullshuffle.main(["nullshuffle.py", "reqs.jsonl", "4", "shuf.jsonl"]), 0)
        self.assertEqual(agree.main(["agree.py", "shuf.jsonl", "matches.jsonl", "agr_shuf.jsonl"]), 0)
        code = report.cli(["report.py", "items.jsonl", "reqs.jsonl", "grades.jsonl", "agr.jsonl", "agr_shuf.jsonl", "cal.jsonl", "r.md"])
        self.assertEqual(code, 0)
        self.assertEqual(self.last()["status"], "ok")
        self.assertTrue(os.path.exists("r.md"))


if __name__ == "__main__":
    unittest.main()
