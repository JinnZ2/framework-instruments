#!/usr/bin/env python3
"""Tests for the shared run record. Failure rows come from the same path as success rows."""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import runrecord  # noqa: E402

FIELDS = ["run_id", "utc", "script", "args_hash", "seed", "input_files",
          "output_file", "status", "counts", "notes"]


class TestRunRecord(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.cwd = os.getcwd()
        os.chdir(self.tmp)

    def tearDown(self):
        os.chdir(self.cwd)
        for name in os.listdir(self.tmp):
            os.remove(os.path.join(self.tmp, name))
        os.rmdir(self.tmp)

    def rows(self):
        return [r for _, r in runrecord.read_jsonl("runs.jsonl")]

    def test_success_row_has_every_field(self):
        with open("in.jsonl", "w") as fh:
            fh.write('{"a": 1}\n')
        code = runrecord.run("s.py", ["in.jsonl", "out.jsonl"], 7, ["in.jsonl"], "out.jsonl",
                             lambda: ("ok", {"rows": 1}, ""))
        self.assertEqual(code, 0)
        row = self.rows()[0]
        self.assertEqual(list(row.keys()), FIELDS)
        self.assertEqual(row["seed"], 7)
        self.assertEqual(row["input_files"][0]["name"], "in.jsonl")
        self.assertEqual(len(row["input_files"][0]["sha256"]), 64)
        self.assertEqual(row["output_file"], "out.jsonl")

    def test_exception_becomes_error_row(self):
        def body():
            raise ValueError("x.jsonl line 3: missing field i")
        code = runrecord.run("s.py", [], None, ["missing.jsonl"], None, body)
        self.assertEqual(code, 1)
        row = self.rows()[0]
        self.assertEqual(row["status"], "error")
        self.assertIn("line 3", row["notes"])
        self.assertIsNone(row["input_files"][0]["sha256"])  # absent input is None, not a hash

    def test_void_and_empty_are_rows_with_exit_codes(self):
        self.assertEqual(runrecord.run("s.py", [], None, [], None, lambda: ("void", {}, "no commit")), 2)
        self.assertEqual(runrecord.run("s.py", [], None, [], None, lambda: ("empty", {}, "")), 0)
        self.assertEqual([r["status"] for r in self.rows()], ["void", "empty"])

    def test_unknown_status_is_recorded_as_error(self):
        code = runrecord.run("s.py", [], None, [], None, lambda: ("fine", {}, ""))
        self.assertEqual(code, 1)
        self.assertEqual(self.rows()[0]["status"], "error")

    def test_read_jsonl_rejects_with_line_number(self):
        with open("bad.jsonl", "w") as fh:
            fh.write('{"a": 1}\n\nnot json\n')
        with self.assertRaises(ValueError) as ctx:
            list(runrecord.read_jsonl("bad.jsonl"))
        self.assertIn("line 3", str(ctx.exception))

    def test_list_output_paths(self):
        runrecord.record("s.py", [], None, [], ["a.jsonl", "b.jsonl"], "ok", {}, "")
        self.assertEqual(self.rows()[0]["output_file"], ["a.jsonl", "b.jsonl"])


if __name__ == "__main__":
    unittest.main()
