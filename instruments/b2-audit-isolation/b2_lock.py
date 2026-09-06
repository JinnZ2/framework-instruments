#!/usr/bin/env python3
"""B2.3 lock.py — enforce D's commit lock as a process boundary.

commit: takes a response, writes it plus sha256 to commits.jsonl, exits.
release: refuses to emit the key until a commit hash exists for that reader+case.
"""

import hashlib
import json
import os
import sys

COMMITS_FILE = "commits.jsonl"


def sha256(text):
    return hashlib.sha256(text.encode()).hexdigest()


def commit(reader_id, case_id, response_text):
    entry = {
        "reader_id": reader_id,
        "case_id": case_id,
        "response_text": response_text,
        "hash": sha256(response_text)
    }
    with open(COMMITS_FILE, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"Commit recorded for {reader_id}/{case_id}")


def release(reader_id, case_id, cases_path):
    # Check for commit
    if not os.path.exists(COMMITS_FILE):
        print(f"VOID: no commits file for {reader_id}/{case_id}", file=sys.stderr)
        sys.exit(1)

    found = False
    with open(COMMITS_FILE, "r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            row = json.loads(line)
            if row["reader_id"] == reader_id and row["case_id"] == case_id:
                found = True
                break

    if not found:
        print(f"VOID: no commit for {reader_id}/{case_id}", file=sys.stderr)
        sys.exit(1)

    # Emit key
    with open(cases_path, "r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            case = json.loads(line)
            if case["case_id"] == case_id:
                key_text = f"{case['key_posed']}\n{case['key_target']}\n{case['key_why']}"
                print(json.dumps({
                    "case_id": case_id,
                    "reader_id": reader_id,
                    "key_text": key_text
                }, ensure_ascii=False))
                return

    print(f"Case {case_id} not found", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: lock.py commit <reader_id> <case_id> <response_text>", file=sys.stderr)
        print("       lock.py release <reader_id> <case_id> <cases.jsonl>", file=sys.stderr)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "commit":
        if len(sys.argv) != 5:
            print("Usage: lock.py commit <reader_id> <case_id> <response_text>", file=sys.stderr)
            sys.exit(1)
        commit(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "release":
        if len(sys.argv) != 5:
            print("Usage: lock.py release <reader_id> <case_id> <cases.jsonl>", file=sys.stderr)
            sys.exit(1)
        release(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)
