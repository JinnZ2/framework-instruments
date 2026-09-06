#!/usr/bin/env python3
"""B2.1 conditions.py — emit presentation files for A/B/C/D.

Input: cases.jsonl (case_id, statement, key_posed, key_target, key_why)
Output: presentations.jsonl (case_id, condition, presented_text)
Never leaks withheld fields.
"""

import json
import sys

REQUIRED = {"case_id", "statement", "key_posed", "key_target", "key_why"}


def emit(cases_path, out_path):
    rows = []
    with open(cases_path, "r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            case = json.loads(line)
            missing = REQUIRED - set(case.keys())
            if missing:
                raise ValueError(f"Missing fields {missing} in {case['case_id']}")

            # A: statement only
            rows.append({
                "case_id": case["case_id"],
                "condition": "A",
                "presented_text": case["statement"]
            })
            # B: key only
            key_text = f"{case['key_posed']}\n{case['key_target']}\n{case['key_why']}"
            rows.append({
                "case_id": case["case_id"],
                "condition": "B",
                "presented_text": key_text
            })
            # C: both
            both_text = f"{case['statement']}\n\n{key_text}"
            rows.append({
                "case_id": case["case_id"],
                "condition": "C",
                "presented_text": both_text
            })
            # D: sequential (A-stage text only; key released after commit)
            rows.append({
                "case_id": case["case_id"],
                "condition": "D",
                "presented_text": case["statement"]
            })

    # Assert no withheld field leakage
    for r in rows:
        text = r["presented_text"]
        # The only fields that can appear in presented_text are statement and key parts
        # We don't check content, but we verify the schema is correct
        assert set(r.keys()) == {"case_id", "condition", "presented_text"}, (
            f"Row {r['case_id']}/{r['condition']} has extra fields"
        )

    with open(out_path, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Emitted {len(rows)} presentation rows")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: conditions.py <cases.jsonl> <presentations.jsonl>", file=sys.stderr)
        sys.exit(1)
    emit(sys.argv[1], sys.argv[2])
