#!/usr/bin/env python3
"""B3.3 arms.py — declare arms and refuse to mix them.

Valid arms: single, split.
Every row carries its arm. Refuses to write if mixed arms detected.
"""

import json
import sys

VALID_ARMS = {"single", "split"}


def validate(in_path, out_path):
    rows = []
    with open(in_path, "r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            row = json.loads(line)
            if "arm" not in row:
                raise ValueError(f"Missing arm in {row.get('case_id', '?')}")
            if row["arm"] not in VALID_ARMS:
                raise ValueError(f"Invalid arm {row['arm']!r}")
            rows.append(row)

    arms = {r["arm"] for r in rows}
    if len(arms) > 1:
        print(f"ERROR: Mixed arms {arms}. Refusing to write.", file=sys.stderr)
        sys.exit(1)

    with open(out_path, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Validated {len(rows)} cases, arm={arms.pop()}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: arms.py <cases.jsonl> <validated_cases.jsonl>", file=sys.stderr)
        sys.exit(1)
    validate(sys.argv[1], sys.argv[2])
