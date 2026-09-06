#!/usr/bin/env python3
"""B2.4 agree.py — score agreement across independent auditors.

Input: responses.jsonl (case_id, condition, reader_id, posed, target)
Output: agreement.jsonl

No correctness score. Only agreement.
"""

import json
import sys
from collections import defaultdict
from itertools import combinations


def load_responses(path):
    data = defaultdict(lambda: defaultdict(list))
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            row = json.loads(line)
            data[row["case_id"]][row["condition"]].append(row)
    return data


def agreement_rate(values_a, values_b):
    """Simple exact-match agreement rate."""
    if not values_a or not values_b:
        return 0.0
    matches = sum(1 for a, b in zip(values_a, values_b) if a == b)
    return matches / len(values_a)


def compute(data):
    results = []
    for case_id in sorted(data.keys()):
        cond_data = data[case_id]
        for condition in sorted(cond_data.keys()):
            readers = cond_data[condition]
            n = len(readers)
            if n < 2:
                continue

            # Pairwise agreement on posed and target
            posed_agrs = []
            target_agrs = []
            full_disagree = 0
            for ra, rb in combinations(readers, 2):
                pa = agreement_rate([ra["posed"]], [rb["posed"]])
                ta = agreement_rate([ra["target"]], [rb["target"]])
                posed_agrs.append({"pair": (ra["reader_id"], rb["reader_id"]), "agreement": pa})
                target_agrs.append({"pair": (ra["reader_id"], rb["reader_id"]), "agreement": ta})
                if pa == 0.0 and ta == 0.0:
                    full_disagree += 1

            results.append({
                "case_id": case_id,
                "condition": condition,
                "auditor_count": n,
                "posed_agreements": posed_agrs,
                "target_agreements": target_agrs,
                "full_disagreement_count": full_disagree,
            })

    # A vs D-first-half comparison
    # D-first-half = condition D responses before key release (same as A)
    # We compare A responses to D responses on posed/target
    a_vs_d = []
    for case_id in sorted(data.keys()):
        a_readers = {r["reader_id"]: r for r in data[case_id].get("A", [])}
        d_readers = {r["reader_id"]: r for r in data[case_id].get("D", [])}
        for rid in set(a_readers) & set(d_readers):
            a_match = (a_readers[rid]["posed"] == d_readers[rid]["posed"] and
                       a_readers[rid]["target"] == d_readers[rid]["target"])
            a_vs_d.append({"case_id": case_id, "reader_id": rid, "match": a_match})

    # C vs D comparison (identical material, lock differs)
    c_vs_d = []
    for case_id in sorted(data.keys()):
        c_readers = {r["reader_id"]: r for r in data[case_id].get("C", [])}
        d_readers = {r["reader_id"]: r for r in data[case_id].get("D", [])}
        for rid in set(c_readers) & set(d_readers):
            c_match = (c_readers[rid]["posed"] == d_readers[rid]["posed"] and
                       c_readers[rid]["target"] == d_readers[rid]["target"])
            c_vs_d.append({"case_id": case_id, "reader_id": rid, "match": c_match})

    return results, a_vs_d, c_vs_d


def main(resp_path, out_path):
    data = load_responses(resp_path)
    results, a_vs_d, c_vs_d = compute(data)

    with open(out_path, "w", encoding="utf-8") as fh:
        for r in results:
            fh.write(json.dumps({"type": "agreement", **r}, ensure_ascii=False) + "\n")
        for r in a_vs_d:
            fh.write(json.dumps({"type": "a_vs_d", **r}, ensure_ascii=False) + "\n")
        for r in c_vs_d:
            fh.write(json.dumps({"type": "c_vs_d", **r}, ensure_ascii=False) + "\n")

    print(f"Agreement computed for {len(results)} case/condition pairs")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: agree.py <responses.jsonl> <agreement.jsonl>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
