#!/usr/bin/env python3
"""B3.3 arms.py — declare the arms and refuse to mix them in one output file.

  single   one instance writes statement and key together (baseline)
  split    two instances, no shared context

  b3_arms.py cases.jsonl arm cases_armed.jsonl

Every output row carries its arm. A row with no arm is stamped with the
declared one; a row already carrying a DIFFERENT arm makes the whole file a
mix and nothing is written (status error, the offending line named). B2 then
compares key coherence under condition B between arms — that comparison is
B3's result, and it lives in B2, not here.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import runrecord  # noqa: E402

ARMS = ("single", "split")
CASE_FIELDS = ("case_id", "statement", "key_posed", "key_target", "key_why")


def check_arm(arm):
    if arm not in ARMS:
        raise ValueError(f"arm must be one of {ARMS}, got {arm!r}")


def stamp(in_path, arm, out_path):
    check_arm(arm)
    rows, seen, stamped = [], set(), 0
    for n, row in runrecord.read_jsonl(in_path, "cases.jsonl"):
        for f in CASE_FIELDS:
            if f not in row:
                raise ValueError(f"cases.jsonl line {n}: missing field {f}")
        extra = sorted(set(row) - set(CASE_FIELDS) - {"arm"})
        if extra:
            raise ValueError(f"cases.jsonl line {n}: unexpected field {extra[0]}")
        if "arm" in row and row["arm"] != arm:
            raise ValueError(f"cases.jsonl line {n}: arm {row['arm']!r} in a file declared {arm!r}; arms are not mixed in one file")
        if row["case_id"] in seen:
            raise ValueError(f"cases.jsonl line {n}: duplicate case_id {row['case_id']}")
        seen.add(row["case_id"])
        if "arm" not in row:
            stamped += 1
        rows.append(dict(row, arm=arm))
    runrecord.write_jsonl(out_path, rows)
    return ("ok" if rows else "empty"), {"rows": len(rows), "stamped": stamped}, f"arm={arm}"


def main(argv):
    if len(argv) != 4:
        print("usage: b3_arms.py cases.jsonl arm cases_armed.jsonl", file=sys.stderr)
        return 1
    return runrecord.run("b3_arms.py", argv[1:], None, [argv[1]], argv[3],
                         lambda: stamp(argv[1], argv[2], argv[3]))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
