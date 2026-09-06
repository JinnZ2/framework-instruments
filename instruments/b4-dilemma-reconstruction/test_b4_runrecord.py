#!/usr/bin/env python3
"""B4 run-record wiring: every entry point writes a row; void and error rows too."""

import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
import runrecord  # noqa: E402
import items  # noqa: E402
import requirements  # noqa: E402
import reconstruct  # noqa: E402
import nullshuffle  # noqa: E402
import grade  # noqa: E402
import report  # noqa: E402

ITEM = {"item_id": "i1", "source": "s", "text_verbatim": "t", "branches_stated": 2, "arm": "documented"}


def req(rid, status, n=1):
    return {"item_id": "i1", "reconstructor_id": rid, "req_id": f"{rid}-{n}", "requirement_text": "must hold",
            "status": status, "settling_test": "measure it", "layer": "physical"}


class TestB4RunRecord(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.cwd = os.getcwd()
        os.chdir(self.tmp)

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

    def test_items_ok_void_error(self):
        runrecord.write_jsonl("items.jsonl", [ITEM])
        self.assertEqual(items.main(["items.py", "items.jsonl", "out.jsonl"]), 0)
        self.assertEqual((self.last()["script"], self.last()["status"], self.last()["counts"]), ("b4/items.py", "ok", {"rows": 1}))
        runrecord.write_jsonl("mixed.jsonl", [ITEM, dict(ITEM, item_id="i2", arm="hypothetical")])
        self.assertEqual(items.main(["items.py", "mixed.jsonl", "out2.jsonl"]), 2)
        self.assertEqual(self.last()["status"], "void")
        self.assertFalse(os.path.exists("out2.jsonl"))
        with open("bad.jsonl", "w") as fh:
            fh.write("{not json\n")
        self.assertEqual(items.main(["items.py", "bad.jsonl", "out3.jsonl"]), 1)
        self.assertEqual(self.last()["status"], "error")

    def test_requirements_void_on_two_state_grading(self):
        runrecord.write_jsonl("reqs.jsonl", [req("r1", "true"), req("r2", "false")])
        self.assertEqual(requirements.main(["requirements.py", "reqs.jsonl", "out.jsonl"]), 2)
        self.assertEqual(self.last()["status"], "void")
        runrecord.write_jsonl("reqs.jsonl", [req("r1", "true"), req("r2", "undifferentiated")])
        self.assertEqual(requirements.main(["requirements.py", "reqs.jsonl", "out.jsonl"]), 0)
        self.assertEqual(self.last()["status"], "ok")

    def test_nullshuffle_records_seed(self):
        runrecord.write_jsonl("reqs.jsonl", [req("r1", "true"), req("r1", "partial", 2),
                                              dict(req("r2", "true"), item_id="i2"), dict(req("r2", "partial", 2), item_id="i2")])
        self.assertEqual(nullshuffle.main(["nullshuffle.py", "reqs.jsonl", "9", "shuf.jsonl"]), 0)
        rec = self.last()
        self.assertEqual((rec["script"], rec["seed"], rec["status"]), ("b4/nullshuffle.py", 9, "ok"))

    def test_grade_and_reconstruct_and_report_void(self):
        runrecord.write_jsonl("reqs.jsonl", [req("r1", "true"), req("r1", "unknown", 2)])
        self.assertEqual(grade.main(["grade.py", "reqs.jsonl", "grades.jsonl"]), 0)
        self.assertEqual(self.last()["status"], "ok")
        runrecord.write_jsonl("items.jsonl", [ITEM])
        runrecord.write_jsonl("recons.jsonl", [{"reconstructor_id": "r1"}])
        self.assertEqual(reconstruct.main(["reconstruct.py", "items.jsonl", "recons.jsonl", "prompts"]), 0)
        self.assertEqual(self.last()["counts"], {"prompt_files": 1})
        runrecord.write_jsonl("agree.jsonl", [])
        code = report.cli(["report.py", "items.jsonl", "reqs.jsonl", "grades.jsonl", "agree.jsonl",
                           "missing_shuffled.jsonl", "calib.jsonl", "report.md"])
        self.assertEqual(code, 2)
        rec = self.last()
        self.assertEqual((rec["script"], rec["status"]), ("b4/report.py", "void"))
        self.assertIsNone(rec["input_files"][4]["sha256"])

    def test_no_forbidden_field_in_run_records(self):
        runrecord.write_jsonl("items.jsonl", [ITEM])
        items.main(["items.py", "items.jsonl", "out.jsonl"])
        for _, row in runrecord.read_jsonl("runs.jsonl"):
            for f in ("label", "category", "type", "interpretation"):
                self.assertNotIn(f, row)


if __name__ == "__main__":
    unittest.main()
