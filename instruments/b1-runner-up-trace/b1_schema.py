#!/usr/bin/env python3
"""B1.1 schema.py — validate base.jsonl and traces.jsonl.

Rejects with line number and field name. No coercion.
"""

import json
import sys

BASE_FIELDS = {"case_id", "model_id", "i", "token_taken", "logprob_taken",
               "topk", "entropy_i", "entropy_basis"}
TRACE_FIELDS = {"case_id", "model_id", "i", "branch_rank", "forced_token",
                "continuation", "base_continuation"}
VALID_ENTROPY_BASIS = {"full", "topk"}


def validate_base(path):
    with open(path, "r", encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            missing = BASE_FIELDS - set(row.keys())
            if missing:
                raise ValueError(f"base.jsonl line {n}: missing {missing}")
            extra = set(row.keys()) - BASE_FIELDS
            if extra:
                raise ValueError(f"base.jsonl line {n}: extra {extra}")
            if row["entropy_basis"] not in VALID_ENTROPY_BASIS:
                raise ValueError(f"base.jsonl line {n}: invalid entropy_basis")
            if not isinstance(row["topk"], list):
                raise ValueError(f"base.jsonl line {n}: topk not a list")


def validate_traces(path):
    with open(path, "r", encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            missing = TRACE_FIELDS - set(row.keys())
            if missing:
                raise ValueError(f"traces.jsonl line {n}: missing {missing}")
            extra = set(row.keys()) - TRACE_FIELDS
            if extra:
                raise ValueError(f"traces.jsonl line {n}: extra {extra}")
            if not isinstance(row["continuation"], list):
                raise ValueError(f"traces.jsonl line {n}: continuation not a list")
            if not isinstance(row["base_continuation"], list):
                raise ValueError(f"traces.jsonl line {n}: base_continuation not a list")


def main(base_path, traces_path):
    validate_base(base_path)
    validate_traces(traces_path)
    print(f"Validated {base_path} and {traces_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: schema.py <base.jsonl> <traces.jsonl>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
