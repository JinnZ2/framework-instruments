#!/usr/bin/env python3
"""B3.4 test_b3.py — stdlib unittest, fixtures in-file, every main() through the run record."""

import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
import runrecord  # noqa: E402
import b3_split as split  # noqa: E402
import b3_join as join  # noqa: E402
import b3_arms as arms  # noqa: E402

FORBIDDEN = ("label", "category", "type", "interpretation")
STATEMENTS = [{"case_id": "c1", "statement": "The bridge rating assumes a static load."},
              {"case_id": "c2", "statement": "Water boils lower at altitude."}]
KEYS = [{"case_id": "c1", "key_posed": "MIS", "key_target": "static load", "key_why": "traffic is dynamic"},
        {"case_id": "c3", "key_posed": "WELL", "key_target": "none", "key_why": "complete"}]


class TestB3(unittest.TestCase):
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

    def last_record(self):
        return [r for _, r in runrecord.read_jsonl("runs.jsonl")][-1]

    def test_role_key_input_is_statements_only(self):
        runrecord.write_jsonl("statements.jsonl", [dict(STATEMENTS[0], context="how it was written")])
        self.assertEqual(split.main(["b3_split.py", "key", "statements.jsonl", "out"]), 1)
        rec = self.last_record()
        self.assertEqual(rec["status"], "error")
        self.assertIn("statements.jsonl line 1: unexpected field context", rec["notes"])
        self.assertFalse(os.path.exists(os.path.join("out", "role_key_prompt.txt")))
        runrecord.write_jsonl("statements.jsonl", STATEMENTS)
        self.assertEqual(split.main(["b3_split.py", "key", "statements.jsonl", "out"]), 0)
        with open(os.path.join("out", "role_key_prompt.txt")) as fh:
            text = fh.read()
        self.assertIn("static load", text)
        self.assertNotIn("BRIEF", text)          # no generation context
        self.assertNotIn("statement writer", text)  # not asked to author statements

    def test_role_case_never_told_about_a_key(self):
        runrecord.write_jsonl("ids.jsonl", [{"case_id": "c1"}, {"case_id": "c2"}])
        with open("brief.txt", "w") as fh:
            fh.write("Engineering claims about load and temperature.\n")
        self.assertEqual(split.main(["b3_split.py", "case", "ids.jsonl", "brief.txt", "out"]), 0)
        with open(os.path.join("out", "role_case_prompt.txt")) as fh:
            text = fh.read()
        self.assertNotRegex(text.lower(), r"\bkeys?\b")
        self.assertIn("c2", text)
        with open("brief.txt", "w") as fh:
            fh.write("Write cases; an answer key will be written afterwards.\n")
        self.assertEqual(split.main(["b3_split.py", "case", "ids.jsonl", "brief.txt", "out2"]), 1)
        self.assertIn("mentions a key", self.last_record()["notes"])
        runrecord.write_jsonl("ids_bad.jsonl", [{"case_id": "c1", "topic": "leak"}])
        self.assertEqual(split.main(["b3_split.py", "case", "ids_bad.jsonl", "brief.txt", "out3"]), 1)

    def test_join_counts_drops_in_run_record(self):
        runrecord.write_jsonl("statements.jsonl", STATEMENTS)
        runrecord.write_jsonl("keys.jsonl", KEYS)
        self.assertEqual(join.main(["b3_join.py", "statements.jsonl", "keys.jsonl", "split", "cases.jsonl"]), 0)
        rows = [r for _, r in runrecord.read_jsonl("cases.jsonl")]
        self.assertEqual([r["case_id"] for r in rows], ["c1"])
        self.assertEqual(rows[0]["arm"], "split")
        rec = self.last_record()
        self.assertEqual(rec["counts"], {"joined": 1, "dropped_no_key": 1, "dropped_no_statement": 1})
        self.assertIn("c2", rec["notes"])
        self.assertIn("c3", rec["notes"])

    def test_join_refuses_key_rows_carrying_a_statement(self):
        runrecord.write_jsonl("statements.jsonl", STATEMENTS)
        runrecord.write_jsonl("keys.jsonl", [dict(KEYS[0], statement="echoed")])
        self.assertEqual(join.main(["b3_join.py", "statements.jsonl", "keys.jsonl", "split", "cases.jsonl"]), 1)
        self.assertIn("keys.jsonl line 1: unexpected field statement", self.last_record()["notes"])
        self.assertEqual(join.main(["b3_join.py", "statements.jsonl", "keys.jsonl", "mixed", "cases.jsonl"]), 1)
        self.assertIn("arm must be one of", self.last_record()["notes"])

    def test_arms_never_mixed_in_one_file(self):
        base = {"statement": "s", "key_posed": "MIS", "key_target": "t", "key_why": "w"}
        runrecord.write_jsonl("mixed.jsonl", [dict(base, case_id="c1", arm="single"), dict(base, case_id="c2", arm="split")])
        self.assertEqual(arms.main(["b3_arms.py", "mixed.jsonl", "single", "out.jsonl"]), 1)
        self.assertFalse(os.path.exists("out.jsonl"))
        self.assertIn("line 2: arm 'split' in a file declared 'single'", self.last_record()["notes"])
        runrecord.write_jsonl("plain.jsonl", [dict(base, case_id="c1"), dict(base, case_id="c2", arm="single")])
        self.assertEqual(arms.main(["b3_arms.py", "plain.jsonl", "single", "out.jsonl"]), 0)
        rows = [r for _, r in runrecord.read_jsonl("out.jsonl")]
        self.assertEqual({r["arm"] for r in rows}, {"single"})
        self.assertEqual(self.last_record()["counts"], {"rows": 2, "stamped": 1})

    def test_no_forbidden_field_in_any_output(self):
        runrecord.write_jsonl("statements.jsonl", STATEMENTS)
        runrecord.write_jsonl("keys.jsonl", KEYS)
        join.main(["b3_join.py", "statements.jsonl", "keys.jsonl", "split", "cases.jsonl"])
        arms.main(["b3_arms.py", "cases.jsonl", "split", "armed.jsonl"])
        for name in ("cases.jsonl", "armed.jsonl", "runs.jsonl"):
            for n, row in runrecord.read_jsonl(name):
                for f in FORBIDDEN:
                    self.assertNotIn(f, row, f"{name} line {n} carries {f}")


if __name__ == "__main__":
    unittest.main()
