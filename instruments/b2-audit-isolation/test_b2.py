#!/usr/bin/env python3
"""B2.5 test_b2.py — stdlib unittest, fixtures in-file, every main() through the run record."""

import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
import runrecord  # noqa: E402
import b2_conditions as conditions  # noqa: E402
import b2_order as order  # noqa: E402
import b2_lock as lock  # noqa: E402
import b2_agree as agree  # noqa: E402

FORBIDDEN = ("label", "category", "type", "interpretation")
CASES = [{"case_id": "c1", "statement": "The bridge rating assumes a static load.",
          "key_posed": "MIS", "key_target": "static load assumption", "key_why": "traffic is dynamic"},
         {"case_id": "c2", "statement": "Water boils at a lower temperature at altitude.",
          "key_posed": "WELL", "key_target": "none", "key_why": "the claim is complete", "arm": "split"}]


def resp(case, cond, reader, posed, target, sha=None):
    row = {"case_id": case, "condition": cond, "reader_id": reader, "posed": posed, "target": target}
    if sha:
        row["commit_sha256"] = sha
    return row


class TestB2(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.cwd = os.getcwd()
        os.chdir(self.tmp)
        runrecord.write_jsonl("cases.jsonl", CASES)

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

    def commit(self, reader="R1", case="c1", text="posed=MIS target=static load"):
        with open("resp.txt", "w") as fh:
            fh.write(text)
        return lock.main(["b2_lock.py", "commit", "commits.jsonl", reader, case, "resp.txt"])

    # --- lock -----------------------------------------------------------------
    def test_release_refused_without_commit(self):
        code = lock.main(["b2_lock.py", "release", "commits.jsonl", "cases.jsonl", "R1", "c1", "key.jsonl"])
        self.assertEqual(code, 2)
        self.assertFalse(os.path.exists("key.jsonl"))
        rec = self.last_record()
        self.assertEqual((rec["script"], rec["status"]), ("b2_lock.py release", "void"))
        self.assertIn("no commit", rec["notes"])

    def test_release_after_commit_and_integrity(self):
        self.assertEqual(self.commit(), 0)
        before = runrecord.sha256_file("commits.jsonl")
        self.assertEqual(lock.main(["b2_lock.py", "release", "commits.jsonl", "cases.jsonl", "R1", "c1", "key.jsonl"]), 0)
        self.assertEqual(runrecord.sha256_file("commits.jsonl"), before)  # release never writes commits
        key = [r for _, r in runrecord.read_jsonl("key.jsonl")][0]
        self.assertEqual(key["presented_text"], "MIS\nstatic load assumption\ntraffic is dynamic")
        self.assertNotIn("bridge", key["presented_text"])
        self.assertEqual(self.commit(), 2)  # a second commit for the same reader/case is refused
        self.assertIn("once", self.last_record()["notes"])
        # tamper with the stored text: release now refuses on the hash
        with open("commits.jsonl") as fh:
            text = fh.read().replace("posed=MIS", "posed=WELL")
        with open("commits.jsonl", "w") as fh:
            fh.write(text)
        self.assertEqual(lock.main(["b2_lock.py", "release", "commits.jsonl", "cases.jsonl", "R1", "c1", "key2.jsonl"]), 2)
        self.assertIn("hash", self.last_record()["notes"])
        self.assertFalse(os.path.exists("key2.jsonl"))

    # --- conditions -----------------------------------------------------------
    def test_conditions_never_leak_a_withheld_field(self):
        self.assertEqual(conditions.main(["b2_conditions.py", "cases.jsonl", "pres"]), 0)
        files = {c: [r for _, r in runrecord.read_jsonl(os.path.join("pres", f"condition_{c}.jsonl"))] for c in "ABCD"}
        by_id = {c["case_id"]: c for c in CASES}
        for cond, rows in files.items():
            self.assertEqual(len(rows), len(CASES))
            for r in rows:
                self.assertEqual(tuple(r), ("case_id", "condition", "presented_text"))
                self.assertEqual(r["condition"], cond)
                case, text = by_id[r["case_id"]], r["presented_text"]
                if cond in ("A", "D"):
                    self.assertEqual(text, case["statement"])
                    for f in ("key_posed", "key_target", "key_why"):
                        self.assertNotIn(case[f], text)
                if cond == "B":
                    self.assertNotIn(case["statement"], text)
                    for f in ("key_posed", "key_target", "key_why"):
                        self.assertIn(case[f], text)
                if cond == "C":
                    self.assertIn(case["statement"], text)
                    self.assertIn(case["key_why"], text)
                self.assertNotIn("split", text)  # the arm is never presented
        rec = self.last_record()
        self.assertEqual(rec["output_file"], [f"condition_{c}.jsonl" for c in "ABCD"])

    def test_condition_B_refused_when_key_quotes_statement(self):
        leaky = [dict(CASES[0], key_why="because " + CASES[0]["statement"])]
        runrecord.write_jsonl("leaky.jsonl", leaky)
        self.assertEqual(conditions.main(["b2_conditions.py", "leaky.jsonl", "pres"]), 1)
        rec = self.last_record()
        self.assertEqual(rec["status"], "error")
        self.assertIn("line 1", rec["notes"])
        self.assertFalse(os.path.exists(os.path.join("pres", "condition_B.jsonl")))

    # --- order ----------------------------------------------------------------
    def test_order_latin_square_and_shortfall(self):
        self.assertEqual(order.main(["b2_order.py", "8", "5", "assign.jsonl"]), 0)
        rows = [r for _, r in runrecord.read_jsonl("assign.jsonl")]
        self.assertEqual(len(rows), 8)
        for pos in range(4):
            for c in "ABCD":
                self.assertEqual(sum(1 for r in rows if r["order"][pos] == c), 2)
        self.assertTrue(all(r["seed"] == 5 for r in rows))
        self.assertEqual(self.last_record()["notes"], "")
        order.main(["b2_order.py", "5", "5", "assign5.jsonl"])
        rec = self.last_record()
        self.assertIn("shortfall=1", rec["notes"])
        self.assertEqual(rec["counts"], {"readers": 5, "latin_square_readers": 4, "seeded_readers": 1})
        order.main(["b2_order.py", "5", "5", "assign5b.jsonl"])
        self.assertEqual(runrecord.sha256_file("assign5.jsonl"), runrecord.sha256_file("assign5b.jsonl"))

    # --- agree ----------------------------------------------------------------
    def test_a_vs_d1_divergence_detected_first(self):
        self.commit()
        sha = [c for _, c in runrecord.read_jsonl("commits.jsonl")][0]["sha256"]
        runrecord.write_jsonl("responses.jsonl", [
            resp("c1", "A", "R1", "MIS", "static load"),
            resp("c1", "D1", "R1", "WELL", "static load", sha),
            resp("c1", "C", "R1", "MIS", "static load"),
            resp("c1", "D2", "R1", "MIS", "static load")])
        self.assertEqual(agree.main(["b2_agree.py", "responses.jsonl", "commits.jsonl", "agr.jsonl", "cmp.jsonl"]), 0)
        rec = self.last_record()
        self.assertTrue(rec["notes"].startswith("A_vs_D1 n=1 mismatches=1 ORDER EFFECT LIVE"))
        cmp_rows = [r for _, r in runrecord.read_jsonl("cmp.jsonl")]
        self.assertEqual((cmp_rows[0]["left_condition"], cmp_rows[0]["posed_match"]), ("A", False))
        self.assertEqual((cmp_rows[1]["left_condition"], cmp_rows[1]["right_condition"], cmp_rows[1]["posed_match"]), ("C", "D2", True))
        self.assertEqual(rec["counts"]["c_vs_d2_match"], 1)

    def test_three_auditor_agreement_math(self):
        runrecord.write_jsonl("commits.jsonl", [])
        runrecord.write_jsonl("responses.jsonl", [
            resp("c1", "B", "R1", "MIS", "static"), resp("c1", "B", "R2", "MIS", "static"),
            resp("c1", "B", "R3", "WELL", "static"),
            resp("c2", "B", "R1", "MIS", "x"), resp("c2", "B", "R2", "WELL", "y"), resp("c2", "B", "R3", "MIS", "x")])
        self.assertEqual(agree.main(["b2_agree.py", "responses.jsonl", "commits.jsonl", "agr.jsonl", "cmp.jsonl"]), 0)
        agr = {r["case_id"]: r for _, r in runrecord.read_jsonl("agr.jsonl")}
        c1 = agr["c1"]  # R1/R2 agree on both; R1/R3 and R2/R3 differ on posed only
        self.assertEqual((c1["auditor_count"], c1["pair_count"], c1["posed_agree_pairs"], c1["target_agree_pairs"], c1["full_disagreement_count"]), (3, 3, 1, 3, 0))
        self.assertAlmostEqual(c1["posed_agreement_rate"], 1 / 3)
        c2 = agr["c2"]  # R1/R3 agree on both; R2 differs from each on both
        self.assertEqual((c2["posed_agree_pairs"], c2["target_agree_pairs"], c2["full_disagreement_count"]), (1, 1, 2))
        self.assertTrue(self.last_record()["notes"].startswith("A_vs_D1 not computable"))

    def test_single_auditor_rates_are_none_not_zero(self):
        runrecord.write_jsonl("commits.jsonl", [])
        runrecord.write_jsonl("responses.jsonl", [resp("c1", "A", "R1", "MIS", "x")])
        agree.main(["b2_agree.py", "responses.jsonl", "commits.jsonl", "agr.jsonl", "cmp.jsonl"])
        row = [r for _, r in runrecord.read_jsonl("agr.jsonl")][0]
        self.assertIsNone(row["posed_agreement_rate"])
        self.assertEqual(row["pair_count"], 0)

    def test_d1_without_commit_is_rejected(self):
        runrecord.write_jsonl("commits.jsonl", [])
        runrecord.write_jsonl("responses.jsonl", [resp("c1", "D1", "R1", "MIS", "x", "deadbeef")])
        self.assertEqual(agree.main(["b2_agree.py", "responses.jsonl", "commits.jsonl", "agr.jsonl", "cmp.jsonl"]), 1)
        rec = self.last_record()
        self.assertEqual(rec["status"], "error")
        self.assertIn("responses.jsonl line 1", rec["notes"])
        self.assertFalse(os.path.exists("agr.jsonl"))

    def test_no_forbidden_field_in_any_output(self):
        conditions.main(["b2_conditions.py", "cases.jsonl", "pres"])
        order.main(["b2_order.py", "4", "1", "assign.jsonl"])
        self.commit()
        lock.main(["b2_lock.py", "release", "commits.jsonl", "cases.jsonl", "R1", "c1", "key.jsonl"])
        for name in ["assign.jsonl", "commits.jsonl", "key.jsonl", "runs.jsonl"] + [os.path.join("pres", f"condition_{c}.jsonl") for c in "ABCD"]:
            for n, row in runrecord.read_jsonl(name):
                for f in FORBIDDEN:
                    self.assertNotIn(f, row, f"{name} line {n} carries {f}")


if __name__ == "__main__":
    unittest.main()
