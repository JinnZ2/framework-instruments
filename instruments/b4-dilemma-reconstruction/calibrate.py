#!/usr/bin/env python3
"""B4.7 calibrate.py — compare reconstruction against investigation factors.

Runs only on the `documented` arm.
Input:
    requirements.jsonl
    factors.jsonl       (item_id, factor_id, factor_text)
    items.jsonl         (to filter documented arm)

Output:
    calibration.jsonl   per item: recovered, missed, beyond_report
"""

import json
import sys
from collections import defaultdict


def calibrate(req_path, factors_path, items_path, out_path):
    # Load documented item IDs
    documented = set()
    with open(items_path, "r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("arm") == "documented":
                documented.add(row["item_id"])

    # Load factors
    factors = defaultdict(dict)
    with open(factors_path, "r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            row = json.loads(line)
            factors[row["item_id"]][row["factor_id"]] = row

    # Load requirements
    reqs = defaultdict(list)
    with open(req_path, "r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            row = json.loads(line)
            reqs[row["item_id"]].append(row)

    results = []
    for iid in sorted(documented):
        facs = factors.get(iid, {})
        item_reqs = reqs.get(iid, [])
        matched_factors = set()
        beyond = 0

        for req in item_reqs:
            req_text = req["requirement_text"].lower()
            matched = False
            for fid, fac in facs.items():
                ftext = fac["factor_text"].lower()
                # Match by exact req_id→factor_id or text containment
                if (
                    req["req_id"] == fid
                    or req_text in ftext
                    or ftext in req_text
                ):
                    matched_factors.add(fid)
                    matched = True
                    break
            if not matched:
                beyond += 1

        recovered = len(matched_factors)
        missed = len(facs) - recovered
        results.append(
            {
                "item_id": iid,
                "recovered_count": recovered,
                "missed_count": missed,
                "beyond_report": beyond,
                "total_factors": len(facs),
                "total_requirements": len(item_reqs),
            }
        )

    with open(out_path, "w", encoding="utf-8") as fh:
        for res in results:
            fh.write(json.dumps(res, ensure_ascii=False) + "\n")

    print(f"Calibrated {len(results)} documented items")


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

def main(argv):
    if len(argv) != 5:
        print("Usage: calibrate.py <reqs> <factors> <items> <out>", file=sys.stderr)
        return 1

    def body():
        calibrate(argv[1], argv[2], argv[3], argv[4])
        return _status_by_rows(argv[4])
    return runrecord.run("b4/calibrate.py", argv[1:], None, [argv[1], argv[2], argv[3]], argv[4], body)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
