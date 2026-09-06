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


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(
            "Usage: agreement.py <reqs> <matches> <match_source> <out>",
            file=sys.stderr,
        )
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
