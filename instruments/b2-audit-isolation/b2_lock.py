#!/usr/bin/env python3
"""B2.3 lock.py — condition D's commit lock as a PROCESS boundary.

  commit  commits.jsonl reader_id case_id response_file
      appends {reader_id, case_id, utc, sha256, response_text}; a second
      commit for the same reader and case is refused (void).
  release commits.jsonl cases.jsonl reader_id case_id key_out.jsonl
      refuses (void, recorded) unless a commit exists for that reader and
      case AND its stored text still hashes to its stored sha256; then writes
      the key for that case to key_out.jsonl with the commit hash on the row.

commit never opens cases.jsonl; release never writes commits.jsonl. No
invocation holds both a fresh commit and an unlocked key.
"""

import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import runrecord  # noqa: E402

KEY_PARTS = ("key_posed", "key_target", "key_why")


def load_commits(path):
    if not os.path.isfile(path):
        return []
    return [r for _, r in runrecord.read_jsonl(path, "commits.jsonl")]


def find_commit(commits, reader_id, case_id):
    for c in commits:
        if c.get("reader_id") == reader_id and c.get("case_id") == case_id:
            return c
    return None


def commit(commits_path, reader_id, case_id, response_path):
    if find_commit(load_commits(commits_path), reader_id, case_id) is not None:
        return "void", {}, f"commit already exists for {reader_id}/{case_id}; a commit is made once"
    with open(response_path, "r", encoding="utf-8") as fh:
        text = fh.read()
    if not text.strip():
        return "void", {}, "empty response; nothing to commit"
    entry = {"reader_id": reader_id, "case_id": case_id,
             "utc": datetime.now(timezone.utc).isoformat(),
             "sha256": runrecord.sha256_text(text), "response_text": text}
    with open(commits_path, "a", encoding="utf-8") as fh:
        fh.write(runrecord.json.dumps(entry, ensure_ascii=False) + "\n")
    return "ok", {"commits_total": len(load_commits(commits_path))}, f"sha256={entry['sha256']}"


def release(commits_path, cases_path, reader_id, case_id, out_path):
    c = find_commit(load_commits(commits_path), reader_id, case_id)
    if c is None:
        return "void", {}, f"no commit for {reader_id}/{case_id}; key not released"
    if runrecord.sha256_text(c.get("response_text", "")) != c.get("sha256"):
        return "void", {}, f"commit for {reader_id}/{case_id} fails its own hash; key not released"
    for n, case in runrecord.read_jsonl(cases_path, "cases.jsonl"):
        if case.get("case_id") == case_id:
            for f in KEY_PARTS:
                if f not in case:
                    raise ValueError(f"cases.jsonl line {n}: missing field {f}")
            runrecord.write_jsonl(out_path, [{
                "case_id": case_id, "reader_id": reader_id, "condition": "D",
                "commit_sha256": c["sha256"],
                "presented_text": "\n".join(case[f] for f in KEY_PARTS),
            }])
            return "ok", {"released": 1}, f"against commit sha256={c['sha256']}"
    raise ValueError(f"case_id {case_id} not in cases.jsonl")


def main(argv):
    if len(argv) == 6 and argv[1] == "commit":
        _, _, commits_path, reader_id, case_id, response_path = argv
        return runrecord.run("b2_lock.py commit", argv[1:], None, [response_path], commits_path,
                             lambda: commit(commits_path, reader_id, case_id, response_path))
    if len(argv) == 7 and argv[1] == "release":
        _, _, commits_path, cases_path, reader_id, case_id, out_path = argv
        return runrecord.run("b2_lock.py release", argv[1:], None, [commits_path, cases_path], out_path,
                             lambda: release(commits_path, cases_path, reader_id, case_id, out_path))
    print("usage: b2_lock.py commit commits.jsonl reader_id case_id response_file\n"
          "       b2_lock.py release commits.jsonl cases.jsonl reader_id case_id key_out.jsonl", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
