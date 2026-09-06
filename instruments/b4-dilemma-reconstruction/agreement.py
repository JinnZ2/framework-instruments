#!/usr/bin/env python3
"""B4.5 agreement.py — wraps B2 agree.py, adds match_source field.

Usage:
    agreement.py <requirements.jsonl> <matches.jsonl> <match_source> <agreement.jsonl>

match_source is recorded verbatim in every output row (who/what produced matches.jsonl).
"""

import json
import sys
import os

# Ensure agree.py from B2 is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import agree


def main(req_path, matches_path, match_source, out_path):
    reqs = agree.load_requirements(req_path)
    matches = agree.load_matches(matches_path)
    results = agree.compute_agreement(reqs, matches)
    for res in results:
        res["match_source"] = match_source
    with open(out_path, "w", encoding="utf-8") as fh:
        for res in results:
            fh.write(json.dumps(res, ensure_ascii=False) + "\n")
    print(f"Agreement written for {len(results)} items, source={match_source}")


# ---- run-record wiring (added; logic above is unchanged) --------------------
import os  # noqa: E402
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import runrecord  # noqa: E402


def _rows(path):
    try:
        return sum(1 for _ in runrecord.read_jsonl(path))
    except (OSError, ValueError):
        return None


def _status_by_rows(path):
    n = _rows(path)
    return ("ok" if n else "empty"), {"rows": n}, ""

def cli(argv):
    if len(argv) != 5:
        print("Usage: agreement.py <reqs> <matches> <match_source> <out>", file=sys.stderr)
        return 1

    def body():
        main(argv[1], argv[2], argv[3], argv[4])
        status, counts, notes = _status_by_rows(argv[4])
        return status, counts, f"match_source={argv[3]}"
    return runrecord.run("b4/agreement.py", argv[1:], None, [argv[1], argv[2]], argv[4], body)


if __name__ == "__main__":
    sys.exit(cli(sys.argv))
