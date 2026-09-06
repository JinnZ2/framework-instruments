#!/usr/bin/env python3
"""B1.1 schema.py — validate base.jsonl and traces.jsonl.

Rejects with line number and field name. No coercion, no silent defaults.
Every check is a stated rule; the cross-file rules are what make gap_i and
the D sweep computable, so they are validation and not scoring.

  base.jsonl:   case_id, model_id, i, token_taken, logprob_taken,
                topk [[token, logprob], ...], entropy_i, entropy_basis
  traces.jsonl: case_id, model_id, i, branch_rank, forced_token,
                continuation [token...] (<= MAX_D), base_continuation (same length)
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import runrecord  # noqa: E402

BASE_FIELDS = ("case_id", "model_id", "i", "token_taken", "logprob_taken",
               "topk", "entropy_i", "entropy_basis")
TRACE_FIELDS = ("case_id", "model_id", "i", "branch_rank", "forced_token",
                "continuation", "base_continuation")
ENTROPY_BASIS = ("full", "topk")
MAX_D = 128


def _is_num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def _fields(label, n, row, fields):
    missing = [f for f in fields if f not in row]
    if missing:
        raise ValueError(f"{label} line {n}: missing field {missing[0]}")
    extra = sorted(set(row) - set(fields))
    if extra:
        raise ValueError(f"{label} line {n}: unexpected field {extra[0]}")
    for f in ("case_id", "model_id"):
        if not isinstance(row[f], str) or not row[f]:
            raise ValueError(f"{label} line {n}: field {f} must be a non-empty string")
    if not _is_int(row["i"]) or row["i"] < 0:
        raise ValueError(f"{label} line {n}: field i must be a non-negative integer")


def validate_base(path):
    """Return {(case_id, model_id, i): row}. Raises ValueError on the first defect."""
    label = "base.jsonl"
    rows = {}
    for n, row in runrecord.read_jsonl(path, label):
        _fields(label, n, row, BASE_FIELDS)
        if not _is_num(row["logprob_taken"]):
            raise ValueError(f"{label} line {n}: field logprob_taken must be a number")
        if not _is_num(row["entropy_i"]) or row["entropy_i"] < 0:
            raise ValueError(f"{label} line {n}: field entropy_i must be a number >= 0")
        if row["entropy_basis"] not in ENTROPY_BASIS:
            raise ValueError(f"{label} line {n}: field entropy_basis must be one of {ENTROPY_BASIS}")
        topk = row["topk"]
        if not isinstance(topk, list) or not topk:
            raise ValueError(f"{label} line {n}: field topk must be a non-empty list")
        for k, pair in enumerate(topk):
            if (not isinstance(pair, list) or len(pair) != 2 or not _is_num(pair[1])
                    or isinstance(pair[0], (list, dict))):
                raise ValueError(f"{label} line {n}: field topk[{k}] must be [token, logprob]")
        key = (row["case_id"], row["model_id"], row["i"])
        if key in rows:
            raise ValueError(f"{label} line {n}: duplicate position (case_id, model_id, i)={key}")
        rows[key] = row
    return rows


def validate_traces(path, base=None):
    """Return list of trace rows. With base given, also checks the cross-file rules:
    the position exists in base, forced_token is in that row's topk (gap_i needs it),
    and forced_token differs from token_taken (a runner-up is not the taken token)."""
    label = "traces.jsonl"
    seen = set()
    out = []
    for n, row in runrecord.read_jsonl(path, label):
        _fields(label, n, row, TRACE_FIELDS)
        if not _is_int(row["branch_rank"]) or row["branch_rank"] < 2:
            raise ValueError(f"{label} line {n}: field branch_rank must be an integer >= 2")
        cont, bcont = row["continuation"], row["base_continuation"]
        if not isinstance(cont, list) or not cont:
            raise ValueError(f"{label} line {n}: field continuation must be a non-empty list")
        if len(cont) > MAX_D:
            raise ValueError(f"{label} line {n}: field continuation longer than {MAX_D}")
        if not isinstance(bcont, list) or len(bcont) != len(cont):
            raise ValueError(f"{label} line {n}: field base_continuation must be a list of the same length as continuation")
        key = (row["case_id"], row["model_id"], row["i"], row["branch_rank"])
        if key in seen:
            raise ValueError(f"{label} line {n}: duplicate (case_id, model_id, i, branch_rank)={key}")
        seen.add(key)
        if base is not None:
            brow = base.get(key[:3])
            if brow is None:
                raise ValueError(f"{label} line {n}: position {key[:3]} not in base.jsonl")
            if row["forced_token"] == brow["token_taken"]:
                raise ValueError(f"{label} line {n}: field forced_token equals token_taken")
            if not any(t == row["forced_token"] for t, _ in brow["topk"]):
                raise ValueError(f"{label} line {n}: field forced_token not in base topk")
        out.append(row)
    return out


def validate(base_path, traces_path):
    base = validate_base(base_path)
    traces = validate_traces(traces_path, base)
    return base, traces


def main(argv):
    if len(argv) != 3:
        print("usage: b1_schema.py base.jsonl traces.jsonl", file=sys.stderr)
        return 1

    def body():
        base, traces = validate(argv[1], argv[2])
        status = "ok" if traces else "empty"
        return status, {"base_rows": len(base), "trace_rows": len(traces)}, ""

    return runrecord.run("b1_schema.py", argv[1:], None, [argv[1], argv[2]], None, body)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
