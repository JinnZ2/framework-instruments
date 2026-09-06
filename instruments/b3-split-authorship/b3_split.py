#!/usr/bin/env python3
"""B3.1 split.py — prompt files for two roles that never share context.

  b3_split.py case case_ids.jsonl brief.txt out_dir
      ROLE CASE writes statements only. Its prompt is built from the
      operator's brief plus a fixed instruction block and the case ids. It is
      never asked for a key and never told one will be written; a brief that
      mentions a key is refused.
  b3_split.py key statements.jsonl out_dir
      ROLE KEY receives statements ONLY. Its prompt is built from
      statements.jsonl alone — a row with any field beyond case_id and
      statement is refused with its line number — plus a fixed instruction
      block that carries no generation context.

Outputs: out_dir/role_case_prompt.txt or out_dir/role_key_prompt.txt.
The model call happens outside this script; its reply comes back as a file.
"""

import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import runrecord  # noqa: E402

KEY_TOKENS = ("key_posed", "key_target", "key_why")
KEY_WORD = re.compile(r"\bkeys?\b", re.IGNORECASE)

CASE_INSTRUCTIONS = (
    "ROLE: statement writer.\n"
    "Write one statement per case_id below. Return JSONL, one object per line,\n"
    "with exactly the fields case_id and statement. Return nothing else.\n")
KEY_INSTRUCTIONS = (
    "ROLE: answer-key writer.\n"
    "For each statement below, decide whether the problem it states is well posed.\n"
    "Return JSONL, one object per line, with exactly the fields case_id, key_posed\n"
    "(WELL or MIS), key_target (what is mis-posed, or none), key_why (one sentence).\n"
    "You have not seen and will not see anything about how the statements were written.\n")


def read_case_ids(path):
    ids, seen = [], set()
    for n, row in runrecord.read_jsonl(path, "case_ids.jsonl"):
        if tuple(row) != ("case_id",):
            raise ValueError(f"case_ids.jsonl line {n}: rows carry case_id only")
        if not isinstance(row["case_id"], str) or not row["case_id"]:
            raise ValueError(f"case_ids.jsonl line {n}: field case_id must be a non-empty string")
        if row["case_id"] in seen:
            raise ValueError(f"case_ids.jsonl line {n}: duplicate case_id {row['case_id']}")
        seen.add(row["case_id"])
        ids.append(row["case_id"])
    return ids


def read_statements(path):
    """Rows with exactly case_id and statement; anything else is refused."""
    rows, seen = [], set()
    for n, row in runrecord.read_jsonl(path, "statements.jsonl"):
        if set(row) != {"case_id", "statement"}:
            extra = sorted(set(row) - {"case_id", "statement"})
            what = f"unexpected field {extra[0]}" if extra else "missing field"
            raise ValueError(f"statements.jsonl line {n}: {what}; ROLE KEY input is case_id and statement only")
        if not isinstance(row["statement"], str) or not row["statement"].strip():
            raise ValueError(f"statements.jsonl line {n}: field statement must be a non-empty string")
        if row["case_id"] in seen:
            raise ValueError(f"statements.jsonl line {n}: duplicate case_id {row['case_id']}")
        seen.add(row["case_id"])
        rows.append({"case_id": row["case_id"], "statement": row["statement"]})
    return rows


def case_prompt(ids, brief):
    if any(t in brief for t in KEY_TOKENS) or KEY_WORD.search(brief):
        raise ValueError("brief mentions a key; ROLE CASE must not be told a key exists")
    body = CASE_INSTRUCTIONS + "\nBRIEF:\n" + brief.strip() + "\n\nCASE IDS:\n" + "\n".join(ids) + "\n"
    if any(t in body for t in KEY_TOKENS) or KEY_WORD.search(body):
        raise ValueError("ROLE CASE prompt would mention a key")
    return body


def key_prompt(statements):
    return KEY_INSTRUCTIONS + "\nSTATEMENTS:\n" + "".join(
        f"{r['case_id']}\t{r['statement']}\n" for r in statements)


def split_case(ids_path, brief_path, out_dir):
    ids = read_case_ids(ids_path)
    with open(brief_path, "r", encoding="utf-8") as fh:
        brief = fh.read()
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "role_case_prompt.txt"), "w", encoding="utf-8") as fh:
        fh.write(case_prompt(ids, brief))
    return ("ok" if ids else "empty"), {"case_ids": len(ids)}, ""


def split_key(statements_path, out_dir):
    statements = read_statements(statements_path)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "role_key_prompt.txt"), "w", encoding="utf-8") as fh:
        fh.write(key_prompt(statements))
    return ("ok" if statements else "empty"), {"statements": len(statements)}, ""


def main(argv):
    if len(argv) == 5 and argv[1] == "case":
        out = os.path.join(argv[4], "role_case_prompt.txt")
        return runrecord.run("b3_split.py case", argv[1:], None, [argv[2], argv[3]], out,
                             lambda: split_case(argv[2], argv[3], argv[4]))
    if len(argv) == 4 and argv[1] == "key":
        out = os.path.join(argv[3], "role_key_prompt.txt")
        return runrecord.run("b3_split.py key", argv[1:], None, [argv[2]], out,
                             lambda: split_key(argv[2], argv[3]))
    print("usage: b3_split.py case case_ids.jsonl brief.txt out_dir\n"
          "       b3_split.py key statements.jsonl out_dir", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
