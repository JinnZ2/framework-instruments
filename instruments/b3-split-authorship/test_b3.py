#!/usr/bin/env python3
"""B3.4 test_b3.py — stdlib unittest.

Tests:
- ROLE KEY input contains no generation context and no self-authored statement.
- Arms never appear in the same output file.
- Join preserves case_id; drops are counted.
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import b3_split as split
import b3_join as join
import b3_arms as arms


class TestB3(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        for root, dirs, files in os.walk(self.tmp, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.tmp)

    def _write(self, name, rows):
        path = os.path.join(self.tmp, name)
        with open(path, "w") as fh:
            for r in rows:
                fh.write(json.dumps(r) + "\n")
        return path

    def test_role_key_no_extra_fields(self):
        """ROLE KEY input with extra fields triggers assertion."""
        bad_statements = [
            {"case_id": "c1", "statement": "s", "context": "bad"}
        ]
        path = self._write("bad_statements.jsonl", bad_statements)
        out_dir = os.path.join(self.tmp, "out")
        with self.assertRaises(AssertionError):
            split.emit_role_key_prompts(path, out_dir)

    def test_arms_reject_mixed(self):
        """Mixed arms are rejected."""
        cases = [
            {"case_id": "c1", "arm": "single"},
            {"case_id": "c2", "arm": "split"},
        ]
        path = self._write("mixed.jsonl", cases)
        out_path = os.path.join(self.tmp, "out.jsonl")
        with self.assertRaises(SystemExit):
            arms.validate(path, out_path)

    def test_join_counts_drops(self):
        """Join preserves case_id; mismatches are counted."""
        statements = [
            {"case_id": "c1", "statement": "s1"},
            {"case_id": "c2", "statement": "s2"},
        ]
        keys = [
            {"case_id": "c1", "key_posed": "p1", "key_target": "t1", "key_why": "w1"},
            {"case_id": "c3", "key_posed": "p3", "key_target": "t3", "key_why": "w3"},
        ]
        s_path = self._write("statements.jsonl", statements)
        k_path = self._write("keys.jsonl", keys)
        out_path = os.path.join(self.tmp, "cases.jsonl")
        dropped = join.join(s_path, k_path, out_path, "split")
        self.assertEqual(dropped, 2)  # c2 missing key, c3 missing statement
        with open(out_path) as fh:
            rows = [json.loads(line) for line in fh]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["case_id"], "c1")
        self.assertEqual(rows[0]["arm"], "split")


if __name__ == "__main__":
    unittest.main()
