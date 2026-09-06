#!/usr/bin/env python3
"""B2.5 test_b2.py — stdlib unittest.

Tests:
- lock.py refuses release with no commit.
- conditions.py never leaks withheld fields.
- A/D divergence detected on fixture.
- Agreement math on 3-auditor fixture.
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import b2_conditions as conditions
import b2_lock as lock
import b2_agree as agree


class TestB2(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.orig_commits = lock.COMMITS_FILE
        lock.COMMITS_FILE = os.path.join(self.tmp, "commits.jsonl")

    def tearDown(self):
        lock.COMMITS_FILE = self.orig_commits
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

    def test_lock_refuses_without_commit(self):
        """lock.py release refuses if no commit exists."""
        cases = [{"case_id": "c1", "statement": "s", "key_posed": "p",
                  "key_target": "t", "key_why": "w"}]
        cases_path = self._write("cases.jsonl", cases)
        with self.assertRaises(SystemExit):
            lock.release("R1", "c1", cases_path)

    def test_no_leakage(self):
        """conditions.py never leaks withheld fields into presented_text."""
        cases = [{
            "case_id": "c1",
            "statement": "The statement.",
            "key_posed": "posed_key",
            "key_target": "target_key",
            "key_why": "because"
        }]
        cases_path = self._write("cases.jsonl", cases)
        out_path = os.path.join(self.tmp, "pres.jsonl")
        conditions.emit(cases_path, out_path)
        with open(out_path) as fh:
            rows = [json.loads(line) for line in fh]
        for r in rows:
            # Assert schema is exactly three fields
            self.assertEqual(set(r.keys()), {"case_id", "condition", "presented_text"})
            # For condition A, key fields must not appear
            if r["condition"] == "A":
                self.assertNotIn("posed_key", r["presented_text"])
                self.assertNotIn("target_key", r["presented_text"])
                self.assertNotIn("because", r["presented_text"])

    def test_a_d_divergence_detected(self):
        """A/D divergence is detected when responses differ."""
        responses = [
            {"case_id": "c1", "condition": "A", "reader_id": "R1", "posed": "X", "target": "Y"},
            {"case_id": "c1", "condition": "D", "reader_id": "R1", "posed": "Z", "target": "Y"},
        ]
        resp_path = self._write("responses.jsonl", responses)
        out_path = os.path.join(self.tmp, "agree.jsonl")
        agree.main(resp_path, out_path)
        with open(out_path) as fh:
            rows = [json.loads(line) for line in fh]
        a_vs_d = [r for r in rows if r["type"] == "a_vs_d"]
        self.assertEqual(len(a_vs_d), 1)
        self.assertFalse(a_vs_d[0]["match"])

    def test_three_auditor_agreement(self):
        """Hand-checked 3-auditor fixture."""
        responses = [
            {"case_id": "c1", "condition": "A", "reader_id": "R1", "posed": "X", "target": "Y"},
            {"case_id": "c1", "condition": "A", "reader_id": "R2", "posed": "X", "target": "Y"},
            {"case_id": "c1", "condition": "A", "reader_id": "R3", "posed": "Z", "target": "Y"},
        ]
        resp_path = self._write("responses.jsonl", responses)
        out_path = os.path.join(self.tmp, "agree.jsonl")
        agree.main(resp_path, out_path)
        with open(out_path) as fh:
            rows = [json.loads(line) for line in fh]
        agr = [r for r in rows if r["type"] == "agreement"][0]
        self.assertEqual(agr["auditor_count"], 3)
        # R1/R2 agree on both; R1/R3 disagree on posed; R2/R3 disagree on posed
        posed_matches = sum(1 for p in agr["posed_agreements"] if p["agreement"] == 1.0)
        self.assertEqual(posed_matches, 1)  # only R1/R2
        target_matches = sum(1 for p in agr["target_agreements"] if p["agreement"] == 1.0)
        self.assertEqual(target_matches, 3)  # all agree on target


if __name__ == "__main__":
    unittest.main()
