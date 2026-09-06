#!/usr/bin/env python3
"""B3.2 join.py — join statements and keys into the cases.jsonl schema B2 consumes.

  b3_join.py statements.jsonl keys.jsonl arm cases.jsonl

statements.jsonl rows: case_id, statement            (exactly)
keys.jsonl rows:       case_id, key_posed, key_target, key_why  (exactly;
                       a key row carrying a statement is refused — the key
                       role returns keys, not statements)
Output rows: case_id, statement, key_posed, key_target, key_why, arm.

A case_id present on one side only is DROPPED, and every drop is counted in
the run record (dropped_no_key, dropped_no_statement) with the ids in notes.
Nothing is dropped silently.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import runrecord  # noqa: E402
import b3_split  # noqa: E402
import b3_arms  # noqa: E402

KEY_FIELDS = ("case_id", "key_posed", "key_target", "key_why")


def read_keys(path):
    rows, seen = {}, set()
    for n, row in runrecord.read_jsonl(path, "keys.jsonl"):
        for f in KEY_FIELDS:
            if f not in row:
                raise ValueError(f"keys.jsonl line {n}: missing field {f}")
            if not isinstance(row[f], str) or not row[f].strip():
                raise ValueError(f"keys.jsonl line {n}: field {f} must be a non-empty string")
        extra = sorted(set(row) - set(KEY_FIELDS))
        if extra:
            raise ValueError(f"keys.jsonl line {n}: unexpected field {extra[0]}")
        if row["case_id"] in seen:
            raise ValueError(f"keys.jsonl line {n}: duplicate case_id {row['case_id']}")
        seen.add(row["case_id"])
        rows[row["case_id"]] = row
    return rows


def join(statements_path, keys_path, arm, out_path):
    b3_arms.check_arm(arm)
    statements = {r["case_id"]: r["statement"] for r in b3_split.read_statements(statements_path)}
    keys = read_keys(keys_path)
    joined = sorted(set(statements) & set(keys))
    no_key = sorted(set(statements) - set(keys))
    no_statement = sorted(set(keys) - set(statements))
    runrecord.write_jsonl(out_path, [
        {"case_id": cid, "statement": statements[cid], "key_posed": keys[cid]["key_posed"],
         "key_target": keys[cid]["key_target"], "key_why": keys[cid]["key_why"], "arm": arm}
        for cid in joined])
    counts = {"joined": len(joined), "dropped_no_key": len(no_key), "dropped_no_statement": len(no_statement)}
    notes = ""
    if no_key or no_statement:
        notes = f"dropped no_key={no_key} no_statement={no_statement}"
    return ("ok" if joined else "empty"), counts, notes


def main(argv):
    if len(argv) != 5:
        print("usage: b3_join.py statements.jsonl keys.jsonl arm cases.jsonl", file=sys.stderr)
        return 1
    return runrecord.run("b3_join.py", argv[1:], None, [argv[1], argv[2]], argv[4],
                         lambda: join(argv[1], argv[2], argv[3], argv[4]))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
