#!/usr/bin/env python3
"""B1.6 test_b1.py — stdlib unittest, synthetic fixtures generated in-file.

The six fixtures the work order names, plus schema and run-record checks.
Pipeline-level behaviour (permutation removing structure, report shape, void)
is in test_b1_pipeline.py.
"""

import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
import runrecord  # noqa: E402
import b1_schema as schema  # noqa: E402
import b1_score as score  # noqa: E402
import b1_permute as permute  # noqa: E402

BASE_CONT = list(range(1000, 1128))


def base_row(i=0, ent=1.0):
    return {"case_id": "c1", "model_id": "m1", "i": i, "token_taken": 1, "logprob_taken": -0.1,
            "topk": [[1, -0.1], [2, -0.5], [3, -0.9]], "entropy_i": ent, "entropy_basis": "topk"}


def trace_row(cont, base_cont=None, i=0, rank=2):
    return {"case_id": "c1", "model_id": "m1", "i": i, "branch_rank": rank, "forced_token": 2,
            "continuation": cont, "base_continuation": base_cont if base_cont is not None else BASE_CONT[:len(cont)]}


class TestB1(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.cwd = os.getcwd()
        os.chdir(self.tmp)

    def tearDown(self):
        os.chdir(self.cwd)
        for name in os.listdir(self.tmp):
            os.remove(os.path.join(self.tmp, name))
        os.rmdir(self.tmp)

    def write(self, name, rows):
        runrecord.write_jsonl(name, rows)
        return name

    def scored(self, traces, base=None):
        self.write("base.jsonl", base or [base_row()])
        self.write("traces.jsonl", traces)
        status, counts, _ = score.score("base.jsonl", "traces.jsonl", "sep.jsonl")
        self.assertEqual(status, "ok")
        return [r for _, r in runrecord.read_jsonl("sep.jsonl")]

    def test_immediate_rejoin(self):
        rows = self.scored([trace_row(BASE_CONT[:])])
        self.assertEqual(len(rows), len(score.D_VALUES) * len(score.L_VALUES))
        self.assertTrue(all(r["resync_D"] == 1 for r in rows))
        self.assertTrue(all(r["div_D"] == 0.0 for r in rows))

    def test_never_rejoin_div_rises_with_D(self):
        cont = BASE_CONT[:6] + [5000 + k for k in range(122)]  # shares a prefix, never the suffix
        rows = self.scored([trace_row(cont)])
        self.assertTrue(all(r["resync_D"] == 0 for r in rows))
        div_by_D = {r["D"]: r["div_D"] for r in rows if r["L"] == 2}
        divs = [div_by_D[D] for D in score.D_VALUES]
        self.assertEqual(divs, sorted(divs))
        self.assertLess(divs[0], divs[-1])

    def test_rejoin_at_exactly_20(self):
        cont = [7000 + k for k in range(20)] + BASE_CONT[20:]
        rows = self.scored([trace_row(cont)])
        for r in rows:  # holds at every L: shared suffix is 0 below D=32 and >= 12 from D=32
            self.assertEqual(r["resync_D"], 0 if r["D"] in (8, 16) else 1, f"D={r['D']} L={r['L']}")

    def test_L_sensitivity_three_token_suffix(self):
        cont = [9001, 9002, 9003, 9004, 9005] + BASE_CONT[5:8]
        rows = self.scored([trace_row(cont)])
        at_8 = {r["L"]: r["resync_D"] for r in rows if r["D"] == 8}
        self.assertEqual(at_8, {2: 1, 4: 0, 8: 0})
        self.assertTrue(all(r["L"] in score.L_VALUES for r in rows))

    def test_gap_and_entropy_carried(self):
        rows = self.scored([trace_row(BASE_CONT[:])], [base_row(ent=2.5)])
        self.assertTrue(all(abs(r["gap_i"] - 0.4) < 1e-12 and r["ent_i"] == 2.5 for r in rows))
        self.assertEqual(list(rows[0].keys()), list(score.ROW_FIELDS))

    def test_permutation_preserves_count_and_multiset(self):
        rows = []
        for i in range(10):
            for D in (8, 16):
                for L in (2, 4):
                    rows.append({"case_id": "c1", "model_id": "m1", "i": i, "branch_rank": 2, "D": D, "L": L,
                                 "ent_i": float(i), "gap_i": 0.1 * i, "resync_D": i % 2, "div_D": 0.01 * i})
        self.write("sep.jsonl", rows)
        status, counts, _ = permute.permute("sep.jsonl", 42, "perm.jsonl")
        out = [r for _, r in runrecord.read_jsonl("perm.jsonl")]
        self.assertEqual(status, "ok")
        self.assertEqual(len(out), len(rows))
        key = lambda r: (r["ent_i"], r["gap_i"], r["resync_D"], r["div_D"])  # noqa: E731
        self.assertEqual(sorted(map(key, rows)), sorted(map(key, out)))
        self.assertTrue(all(r["seed"] == 42 for r in out))
        # same (i, D) keeps one div across L on the permuted file, as on the real one
        for r in out:
            twin = next(t for t in out if (t["i"], t["D"]) == (r["i"], r["D"]) and t["L"] != r["L"])
            self.assertEqual(twin["div_D"], r["div_D"])
        # the position->tuple link is broken: not every row keeps its own tuple
        moved = sum(1 for r, o in zip(sorted(rows, key=lambda r: (r["i"], r["D"], r["L"])),
                                      sorted(out, key=lambda r: (r["i"], r["D"], r["L"]))) if key(r) != key(o))
        self.assertGreater(moved, 0)

    def test_malformed_row_rejected_and_recorded_as_error(self):
        self.write("base.jsonl", [{"case_id": "c1", "model_id": "m1"}])
        self.write("traces.jsonl", [trace_row(BASE_CONT[:])])
        with self.assertRaises(ValueError) as ctx:
            schema.validate_base("base.jsonl")
        self.assertIn("base.jsonl line 1", str(ctx.exception))
        self.assertIn("field i", str(ctx.exception))
        code = schema.main(["b1_schema.py", "base.jsonl", "traces.jsonl"])
        self.assertEqual(code, 1)
        rec = [r for _, r in runrecord.read_jsonl("runs.jsonl")]
        self.assertEqual(len(rec), 1)
        self.assertEqual(rec[0]["status"], "error")
        self.assertIn("line 1", rec[0]["notes"])
        # score.py refuses to write separations on the same defect, and records it
        code = score.main(["b1_score.py", "base.jsonl", "traces.jsonl", "sep.jsonl"])
        self.assertEqual(code, 1)
        self.assertFalse(os.path.exists("sep.jsonl"))

    def test_schema_cross_file_rules(self):
        self.write("base.jsonl", [base_row()])
        cases = {
            "not in base": trace_row(BASE_CONT[:], i=5),
            "forced_token equals token_taken": dict(trace_row(BASE_CONT[:]), forced_token=1),
            "not in base topk": dict(trace_row(BASE_CONT[:]), forced_token=99),
            "same length": trace_row(BASE_CONT[:10], base_cont=BASE_CONT[:9]),
            "longer than 128": trace_row(list(range(129)), base_cont=list(range(129))),
            "branch_rank": trace_row(BASE_CONT[:], rank=1),
            "invalid JSON": None,
        }
        for text, row in cases.items():
            with open("traces.jsonl", "w") as fh:
                fh.write("{oops\n" if row is None else json.dumps(row) + "\n")
            with self.assertRaises(ValueError, msg=text) as ctx:
                schema.validate("base.jsonl", "traces.jsonl")
            self.assertIn("traces.jsonl line 1", str(ctx.exception))
            self.assertIn(text, str(ctx.exception))

    def test_schema_main_ok_path(self):
        self.write("base.jsonl", [base_row()])
        self.write("traces.jsonl", [trace_row(BASE_CONT[:])])
        self.assertEqual(schema.main(["b1_schema.py", "base.jsonl", "traces.jsonl"]), 0)
        rec = [r for _, r in runrecord.read_jsonl("runs.jsonl")][-1]
        self.assertEqual((rec["status"], rec["counts"], rec["output_file"]), ("ok", {"base_rows": 1, "trace_rows": 1}, None))

    def test_schema_rejects_bool_and_coerces_nothing(self):
        bad = dict(base_row(), logprob_taken=True)
        self.write("base.jsonl", [bad])
        with self.assertRaises(ValueError) as ctx:
            schema.validate_base("base.jsonl")
        self.assertIn("logprob_taken", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
