#!/usr/bin/env python3
"""B3.1 split.py — emit prompt files for split authorship.

ROLE CASE: writes statements only. Output: statements.jsonl (case_id, statement).
ROLE KEY: receives statements.jsonl ONLY, writes key_posed, key_target, key_why.
Enforced by file boundary: ROLE KEY input is built from statements.jsonl alone.
"""

import json
import os
import sys


def emit_role_case_prompts(case_specs_path, out_dir):
    """Read case specs and emit ROLE CASE prompt files."""
    os.makedirs(out_dir, exist_ok=True)
    statements = []
    with open(case_specs_path, "r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            spec = json.loads(line)
            statements.append({"case_id": spec["case_id"], "statement": None})
    # Write prompt for ROLE CASE
    prompt_path = os.path.join(out_dir, "role_case_prompt.jsonl")
    with open(prompt_path, "w", encoding="utf-8") as fh:
        for s in statements:
            fh.write(json.dumps(s, ensure_ascii=False) + "\n")
    print(f"ROLE CASE prompt: {prompt_path}")


def emit_role_key_prompts(statements_path, out_dir):
    """Build ROLE KEY input from statements.jsonl alone."""
    os.makedirs(out_dir, exist_ok=True)
    statements = []
    with open(statements_path, "r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            row = json.loads(line)
            # Assert no extra fields (no generation context, no self-authored statement)
            assert set(row.keys()) == {"case_id", "statement"}, (
                f"ROLE KEY input contains extra fields: {set(row.keys())}"
            )
            statements.append({"case_id": row["case_id"], "statement": row["statement"]})

    prompt_path = os.path.join(out_dir, "role_key_prompt.jsonl")
    with open(prompt_path, "w", encoding="utf-8") as fh:
        for s in statements:
            fh.write(json.dumps(s, ensure_ascii=False) + "\n")
    print(f"ROLE KEY prompt: {prompt_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: split.py case <case_specs.jsonl> <out_dir>", file=sys.stderr)
        print("       split.py key <statements.jsonl> <out_dir>", file=sys.stderr)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "case":
        emit_role_case_prompts(sys.argv[2], sys.argv[3])
    elif cmd == "key":
        emit_role_key_prompts(sys.argv[2], sys.argv[3])
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)
