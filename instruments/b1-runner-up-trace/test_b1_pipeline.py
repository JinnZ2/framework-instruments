#!/usr/bin/env python3
"""B1 pipeline tests: every main() through the run record, the permutation
null removing cross-D structure, the void path, report shape, forbidden fields."""

import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
import runrecord  # noqa: E402
import b1_score as score  # noqa: E402
import b1_permute as permute  # noqa: E402
import b1_summarise as summarise  # noqa: E402
import b1_report as report  # noqa: E402

FORBIDDEN = ("label", "category", "type", "interpretation")
SECTIONS = ["## 1. Counts and case set", "## 2. D sweep", "## 3. L sweep",
            "## 4. Stability overlaps", "## 5. Real vs permuted", "## 6. Nulls triggered"]
BASE_CONT = list(range(1000, 1128))


def fixture(n_positions=20, separating=(0, 1, 2)):
    """Positions in `separating` never rejoin; every other position is the base."""
    base, traces = [], []
    for i in range(n_positions):
        base.append({"case_id": "c1", "model_id": "m1", "i": i, "token_taken": 1, "logprob_taken": -0.1,
                     "topk": [[1, -0.1], [2, -0.5], [3, -0.9]], "entropy_i": 0.1 * i, "entropy_basis": "full"})
        for rank, forced in ((2, 2), (3, 3)):
            cont = [5000 + i * 200 + k for k in range(128)] if i in separating else BASE_CONT[:]
            traces.append({"case_id": "c1", "model_id": "m1", "i": i, "branch_rank": rank, "forced_token": forced,
                           "continuation": cont, "base_continuation": BASE_CONT[:]})
    return base, traces


class TestB1Pipeline(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.cwd = os.getcwd()
        os.chdir(self.tmp)

    def tearDown(self):
        os.chdir(self.cwd)
        for name in os.listdir(self.tmp):
            os.remove(os.path.join(self.tmp, name))
        os.rmdir(self.tmp)

    def run_pipeline(self, seed=11):
        base, traces = fixture()
        runrecord.write_jsonl("base.jsonl", base)
        runrecord.write_jsonl("traces.jsonl", traces)
        codes = [
            score.main(["b1_score.py", "base.jsonl", "traces.jsonl", "sep.jsonl"]),
            permute.main(["b1_permute.py", "sep.jsonl", str(seed), "sep_perm.jsonl"]),
            summarise.main(["b1_summarise.py", "sep.jsonl", "summary.jsonl"]),
            summarise.main(["b1_summarise.py", "sep_perm.jsonl", "summary_perm.jsonl"]),
            report.main(["b1_report.py", "summary.jsonl", "summary_perm.jsonl", "report.md"]),
        ]
        return codes

    def test_every_main_writes_a_record(self):
        self.assertEqual(self.run_pipeline(), [0, 0, 0, 0, 0])
        recs = [r for _, r in runrecord.read_jsonl("runs.jsonl")]
        self.assertEqual([r["script"] for r in recs],
                         ["b1_score.py", "b1_permute.py", "b1_summarise.py", "b1_summarise.py", "b1_report.py"])
        self.assertTrue(all(r["status"] == "ok" for r in recs))
        self.assertEqual(recs[1]["seed"], 11)
        self.assertEqual(recs[0]["counts"]["entropy_basis_full"], 20)

    def test_no_forbidden_field_in_any_output(self):
        self.run_pipeline()
        for name in ("sep.jsonl", "sep_perm.jsonl", "summary.jsonl", "summary_perm.jsonl", "runs.jsonl"):
            for n, row in runrecord.read_jsonl(name):
                for f in FORBIDDEN:
                    self.assertNotIn(f, row, f"{name} line {n} carries {f}")

    def test_permutation_removes_cross_D_structure(self):
        """Real: the same three positions top the div decile at every D (Jaccard 1.0).
        Permuted per D: the tuples land on different positions at each D."""
        self.run_pipeline()
        real = [r for _, r in runrecord.read_jsonl("summary.jsonl")]
        perm = [r for _, r in runrecord.read_jsonl("summary_perm.jsonl")]
        real_dj = [r["jaccard"] for r in real if "D_pair" in r]
        perm_dj = [r["jaccard"] for r in perm if "D_pair" in r]
        self.assertTrue(real_dj and all(j == 1.0 for j in real_dj))
        self.assertLess(sum(perm_dj) / len(perm_dj), sum(real_dj) / len(real_dj))
        # what the null does NOT touch: per-group counts, mean div and resync rate
        for rr in real:
            if "jaccard" in rr:
                continue
            pr = next(p for p in perm if "jaccard" not in p and (p["D"], p["L"], p["model_id"]) == (rr["D"], rr["L"], rr["model_id"]))
            self.assertEqual((pr["count"], pr["mean_div_D"], pr["resync_rate"]), (rr["count"], rr["mean_div_D"], rr["resync_rate"]))
        # and adjacent-L Jaccard is 1.0 by construction on the real file
        self.assertTrue(all(r["jaccard"] == 1.0 for r in real if "L_pair" in r))

    def test_report_shape_and_nulls(self):
        self.run_pipeline()
        with open("report.md", encoding="utf-8") as fh:
            text = fh.read()
        heads = [line for line in text.splitlines() if line.startswith("## ")]
        self.assertEqual(heads, SECTIONS)
        self.assertIn("Cases present: 1 — c1", text)
        for code in ("N1", "N2", "N3", "N4", "N5"):
            self.assertIn(f"**{code}**", text)
        self.assertIn("**N1** not fired", text)   # resync 0.85 < 0.9 floor
        self.assertIn("**N4** not fired", text)   # permuted stability below real
        self.assertIn("**N5** NOT EVALUATED", text)
        self.assertIn(str(report.N3_JACCARD_FLOOR), text)

    def test_report_void_without_permuted_summary(self):
        base, traces = fixture()
        runrecord.write_jsonl("base.jsonl", base)
        runrecord.write_jsonl("traces.jsonl", traces)
        score.main(["b1_score.py", "base.jsonl", "traces.jsonl", "sep.jsonl"])
        summarise.main(["b1_summarise.py", "sep.jsonl", "summary.jsonl"])
        code = report.main(["b1_report.py", "summary.jsonl", "summary_perm.jsonl", "report.md"])
        self.assertEqual(code, 2)
        self.assertFalse(os.path.exists("report.md"))
        last = [r for _, r in runrecord.read_jsonl("runs.jsonl")][-1]
        self.assertEqual((last["script"], last["status"]), ("b1_report.py", "void"))
        self.assertIsNone(last["input_files"][1]["sha256"])

    def test_empty_input_is_recorded_empty(self):
        runrecord.write_jsonl("sep.jsonl", [])
        self.assertEqual(summarise.main(["b1_summarise.py", "sep.jsonl", "summary.jsonl"]), 0)
        last = [r for _, r in runrecord.read_jsonl("runs.jsonl")][-1]
        self.assertEqual(last["status"], "empty")
        self.assertTrue(os.path.exists("summary.jsonl"))


if __name__ == "__main__":
    unittest.main()
