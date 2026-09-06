#!/usr/bin/env python3
"""B1.6 test_b1.py — stdlib unittest, synthetic fixtures in-file.

Tests:
- Immediate rejoin → resync 1 everywhere.
- Never rejoin → resync 0 everywhere, normalised div is maximal.
- Rejoin at token 20 → resync 0 at D=8,16; 1 at D=32,64,128.
- L sensitivity: 3-token suffix → resync 1 at L=2, 0 at L=4,8.
- Permutation preserves row count and multiset.
- Malformed input → schema rejects with line/field info.
- Summary metadata preserves the case set required by the report.
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import b1_score as score
import b1_permute as permute
import b1_schema as schema
import b1_summarise as summarise
import b1_report as report


class TestB1(unittest.TestCase):

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

    def test_immediate_rejoin(self):
        """Identical continuation → resync 1 at every D, every L."""
        base = [{
            "case_id": "c1", "model_id": "m1", "i": 0,
            "token_taken": 1, "logprob_taken": -0.1,
            "topk": [[1, -0.1], [2, -0.5]], "entropy_i": 1.0,
            "entropy_basis": "topk"
        }]
        traces = [{
            "case_id": "c1", "model_id": "m1", "i": 0,
            "branch_rank": 1, "forced_token": 2,
            "continuation": [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128],
            "base_continuation": [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128]
        }]
        base_path = self._write("base.jsonl", base)
        trace_path = self._write("traces.jsonl", traces)
        out_path = os.path.join(self.tmp, "sep.jsonl")
        null_path = os.path.join(self.tmp, "nulls.jsonl")
        score.score(base_path, trace_path, out_path, null_path)
        with open(out_path) as fh:
            rows = [json.loads(line) for line in fh]
        for r in rows:
            self.assertEqual(r["resync_D"], 1, f"Failed at D={r['D']}, L={r['L']}")

    def test_never_rejoin(self):
        """No overlap → resync 0 and maximal normalised divergence."""
        base = [{
            "case_id": "c1", "model_id": "m1", "i": 0,
            "token_taken": 1, "logprob_taken": -0.1,
            "topk": [[1, -0.1], [2, -0.5]], "entropy_i": 1.0,
            "entropy_basis": "topk"
        }]
        traces = [{
            "case_id": "c1", "model_id": "m1", "i": 0,
            "branch_rank": 1, "forced_token": 2,
            "continuation": [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227],
            "base_continuation": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128]
        }]
        base_path = self._write("base.jsonl", base)
        trace_path = self._write("traces.jsonl", traces)
        out_path = os.path.join(self.tmp, "sep.jsonl")
        null_path = os.path.join(self.tmp, "nulls.jsonl")
        score.score(base_path, trace_path, out_path, null_path)
        with open(out_path) as fh:
            rows = [json.loads(line) for line in fh]
        for r in rows:
            self.assertEqual(r["resync_D"], 0)
        # Every compared token differs, so normalised divergence is maximal
        # at every D. Raw edit distance rises, but div_D is normalised.
        by_d = {}
        for r in rows:
            by_d.setdefault(r["D"], []).append(r["div_D"])
        div_means = {d: sum(v) / len(v) for d, v in by_d.items()}
        self.assertTrue(all(value == 1.0 for value in div_means.values()))

    def test_rejoin_at_20(self):
        """Rejoin at token 20 → resync 0 at D=8,16; 1 at D=32,64,128."""
        base = [{
            "case_id": "c1", "model_id": "m1", "i": 0,
            "token_taken": 1, "logprob_taken": -0.1,
            "topk": [[1, -0.1], [2, -0.5]], "entropy_i": 1.0,
            "entropy_basis": "topk"
        }]
        base_cont = list(range(1, 129))
        # Diverge until token 20, then match
        cont = [100] * 20 + base_cont[20:]
        traces = [{
            "case_id": "c1", "model_id": "m1", "i": 0,
            "branch_rank": 1, "forced_token": 2,
            "continuation": cont,
            "base_continuation": base_cont
        }]
        base_path = self._write("base.jsonl", base)
        trace_path = self._write("traces.jsonl", traces)
        out_path = os.path.join(self.tmp, "sep.jsonl")
        null_path = os.path.join(self.tmp, "nulls.jsonl")
        score.score(base_path, trace_path, out_path, null_path)
        with open(out_path) as fh:
            rows = [json.loads(line) for line in fh]
        # Check for L=4 (default-like)
        for r in rows:
            if r["L"] != 4:
                continue
            if r["D"] in (8, 16):
                self.assertEqual(r["resync_D"], 0, f"D={r['D']} should be 0")
            elif r["D"] in (32, 64, 128):
                self.assertEqual(r["resync_D"], 1, f"D={r['D']} should be 1")

    def test_l_sensitivity(self):
        """3-token suffix → resync 1 at L=2, 0 at L=4,8."""
        base = [{
            "case_id": "c1", "model_id": "m1", "i": 0,
            "token_taken": 1, "logprob_taken": -0.1,
            "topk": [[1, -0.1], [2, -0.5]], "entropy_i": 1.0,
            "entropy_basis": "topk"
        }]
        base_cont = [1, 2, 3, 4, 5, 6, 7, 8]
        cont = [100, 101, 102, 103, 104, 6, 7, 8]  # shares suffix: 6,7,8
        traces = [{
            "case_id": "c1", "model_id": "m1", "i": 0,
            "branch_rank": 1, "forced_token": 2,
            "continuation": cont,
            "base_continuation": base_cont
        }]
        base_path = self._write("base.jsonl", base)
        trace_path = self._write("traces.jsonl", traces)
        out_path = os.path.join(self.tmp, "sep.jsonl")
        null_path = os.path.join(self.tmp, "nulls.jsonl")
        score.score(base_path, trace_path, out_path, null_path)
        with open(out_path) as fh:
            rows = [json.loads(line) for line in fh]
        for r in rows:
            if r["D"] == 8:
                if r["L"] == 2:
                    self.assertEqual(r["resync_D"], 1)
                elif r["L"] in (4, 8):
                    self.assertEqual(r["resync_D"], 0)

    def test_permutation_preserves(self):
        """Permutation preserves row count and multiset of tuples."""
        rows = []
        for i in range(10):
            for D in (8, 16):
                for L in (2, 4):
                    rows.append({
                        "case_id": "c1", "model_id": "m1", "i": i,
                        "branch_rank": 1, "D": D, "L": L,
                        "ent_i": float(i), "gap_i": float(i) * 0.1,
                        "resync_D": i % 2, "div_D": float(i) * 0.01
                    })
        in_path = self._write("sep.jsonl", rows)
        out_path = os.path.join(self.tmp, "perm.jsonl")
        permute.permute(in_path, 42, out_path)
        with open(out_path) as fh:
            perm_rows = [json.loads(line) for line in fh]
        self.assertEqual(len(rows), len(perm_rows))
        orig = sorted((r["ent_i"], r["gap_i"], r["resync_D"], r["div_D"]) for r in rows)
        new = sorted((r["ent_i"], r["gap_i"], r["resync_D"], r["div_D"]) for r in perm_rows)
        self.assertEqual(orig, new)

    def test_malformed_rejected(self):
        """Malformed input → schema rejects with line/field info."""
        bad_base = [{"case_id": "c1", "model_id": "m1"}]  # missing many fields
        path = self._write("bad_base.jsonl", bad_base)
        with self.assertRaises(ValueError) as ctx:
            schema.validate_base(path)
        msg = str(ctx.exception)
        self.assertIn("line 1", msg)
        self.assertIn("missing", msg)

    def test_summary_preserves_case_set_for_report(self):
        """The report prints the actual case IDs represented by summary rows."""
        rows = []
        for case_id, div in (("c1", 0.25), ("c2", 0.75)):
            rows.append({
                "case_id": case_id, "model_id": "m1", "i": 0,
                "branch_rank": 1, "D": 8, "L": 2, "ent_i": 1.0,
                "gap_i": 0.4, "resync_D": 0, "div_D": div,
            })
        sep_path = self._write("sep.jsonl", rows)
        summary_path = os.path.join(self.tmp, "summary.jsonl")
        perm_summary_path = os.path.join(self.tmp, "perm_summary.jsonl")
        nulls_path = self._write("nulls.jsonl", [])
        report_path = os.path.join(self.tmp, "report.md")

        summarise.summarise(sep_path, summary_path)
        with open(summary_path, "r", encoding="utf-8") as src:
            with open(perm_summary_path, "w", encoding="utf-8") as dst:
                dst.write(src.read())
        report.main(summary_path, perm_summary_path, nulls_path, report_path)

        with open(report_path, "r", encoding="utf-8") as fh:
            rendered = fh.read()
        self.assertIn("Cases: 2 — c1, c2", rendered)


if __name__ == "__main__":
    unittest.main()
