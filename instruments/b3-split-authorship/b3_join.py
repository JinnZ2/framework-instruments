#!/usr/bin/env python3
"""B3.2 join.py — join statements and keys into cases.jsonl.

Input: statements.jsonl (case_id, statement)
       keys.jsonl (case_id, key_posed, key_target, key_why)
Output: cases.jsonl (case_id, statement, key_posed, key_target, key_why, arm)
"""

import json
import sys


def join(statements_path, keys_path, out_path, arm):
    statements = {}
    with open(statements_path, "r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            row = json.loads(line)
            statements[row["case_id"]] = row["statement"]

    keys = {}
    with open(keys_path, "r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            row = json.loads(line)
            keys[row["case_id"]] = row

    case_ids = sorted(set(statements.keys()) & set(keys.keys()))
    dropped = (set(statements.keys()) | set(keys.keys())) - set(case_ids)

    with open(out_path, "w", encoding="utf-8") as fh:
        for cid in case_ids:
            out_row = {
                "case_id": cid,
                "statement": statements[cid],
                "key_posed": keys[cid]["key_posed"],
                "key_target": keys[cid]["key_target"],
                "key_why": keys[cid]["key_why"],
                "arm": arm,
            }
            fh.write(json.dumps(out_row, ensure_ascii=False) + "\n")

    print(f"Joined {len(case_ids)} cases, dropped {len(dropped)} mismatched")
    return len(dropped)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: join.py <statements.jsonl> <keys.jsonl> <cases.jsonl> <arm>",
              file=sys.stderr)
        sys.exit(1)
    join(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
