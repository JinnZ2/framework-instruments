#!/usr/bin/env python3
"""B2.1 conditions.py — four presentation files from cases.jsonl.

  A  STATEMENT ONLY   statement, no key
  B  KEY ONLY         key_posed + key_target + key_why, NO statement
  C  BOTH             simultaneous
  D  SEQUENTIAL       the A text; the key is released only by b2_lock.py

One file per condition (condition_A.jsonl .. condition_D.jsonl) so a reader
handed one file cannot see another condition's material. Every row carries
case_id, condition, presented_text ONLY.

Leak rules, enforced not requested:
  - a presentation is BUILT from a fixed allow-list of field names per
    condition; no other field can reach presented_text by construction;
  - condition B is refused for a case whose statement text occurs inside its
    key text (a key that quotes the statement in full is not "no statement").
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import runrecord  # noqa: E402

CASE_FIELDS = ("case_id", "statement", "key_posed", "key_target", "key_why")
OPTIONAL = ("arm",)  # B3 output carries an arm; it is never presented
KEY_PARTS = ("key_posed", "key_target", "key_why")
ALLOW = {"A": ("statement",), "B": KEY_PARTS, "C": ("statement",) + KEY_PARTS, "D": ("statement",)}
ROW_FIELDS = ("case_id", "condition", "presented_text")


def validate_cases(path):
    cases, seen = [], set()
    for n, row in runrecord.read_jsonl(path, "cases.jsonl"):
        for f in CASE_FIELDS:
            if f not in row:
                raise ValueError(f"cases.jsonl line {n}: missing field {f}")
            if not isinstance(row[f], str) or not row[f].strip():
                raise ValueError(f"cases.jsonl line {n}: field {f} must be a non-empty string")
        extra = sorted(set(row) - set(CASE_FIELDS) - set(OPTIONAL))
        if extra:
            raise ValueError(f"cases.jsonl line {n}: unexpected field {extra[0]}")
        if row["case_id"] in seen:
            raise ValueError(f"cases.jsonl line {n}: duplicate case_id {row['case_id']}")
        seen.add(row["case_id"])
        cases.append((n, row))
    return cases


def present(case, condition):
    parts = [case[f] for f in ALLOW[condition]]
    if condition == "C":
        text = case["statement"] + "\n\n" + "\n".join(case[f] for f in KEY_PARTS)
    else:
        text = "\n".join(parts)
    return {"case_id": case["case_id"], "condition": condition, "presented_text": text}


def build(cases):
    files = {c: [] for c in ALLOW}
    for n, case in cases:
        for condition in ALLOW:
            row = present(case, condition)
            if condition == "B" and case["statement"] in row["presented_text"]:
                raise ValueError(f"cases.jsonl line {n}: statement occurs inside the key text; condition B cannot withhold it")
            if tuple(row) != ROW_FIELDS:
                raise ValueError(f"cases.jsonl line {n}: presentation row carries fields other than {ROW_FIELDS}")
            files[condition].append(row)
    return files


def conditions(cases_path, out_dir):
    cases = validate_cases(cases_path)
    files = build(cases)
    os.makedirs(out_dir, exist_ok=True)
    for condition, rows in files.items():
        runrecord.write_jsonl(os.path.join(out_dir, f"condition_{condition}.jsonl"), rows)
    counts = {"cases": len(cases)}
    counts.update({f"rows_{c}": len(r) for c, r in files.items()})
    return ("ok" if cases else "empty"), counts, ""


def out_paths(out_dir):
    return [os.path.join(out_dir, f"condition_{c}.jsonl") for c in ALLOW]


def main(argv):
    if len(argv) != 3:
        print("usage: b2_conditions.py cases.jsonl out_dir", file=sys.stderr)
        return 1
    return runrecord.run("b2_conditions.py", argv[1:], None, [argv[1]], out_paths(argv[2]),
                         lambda: conditions(argv[1], argv[2]))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
