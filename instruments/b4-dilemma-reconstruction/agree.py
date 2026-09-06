#!/usr/bin/env python3
"""B2 agree.py — core agreement computation.

Input:
    requirements.jsonl  (item_id, reconstructor_id, req_id, ...)
    matches.jsonl       (item_id, req_a, req_b, matched)

Output:
    agreement.jsonl     per-item pairwise agreement, full-disagreement,
                        singleton set.

Matching is external; this script only computes statistics from matches.jsonl.
"""

import json
from collections import defaultdict


def load_requirements(path):
    """Return dict: item_id → reconstructor_id → list of requirement rows."""
    data = defaultdict(lambda: defaultdict(list))
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            row = json.loads(line)
            data[row["item_id"]][row["reconstructor_id"]].append(row)
    return data


def load_matches(path):
    """Return set of (item_id, req_a, req_b) where matched is true."""
    matched = set()
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("matched"):
                matched.add((row["item_id"], row["req_a"], row["req_b"]))
    return matched


def compute_agreement(reqs, matches):
    """Compute agreement statistics per item."""
    results = []
    for item_id in sorted(reqs.keys()):
        recon_data = reqs[item_id]
        recon_ids = sorted(recon_data.keys())
        if len(recon_ids) < 2:
            continue

        # Pairwise agreement
        pairwise = []
        for i, rid_a in enumerate(recon_ids):
            for rid_b in recon_ids[i + 1 :]:
                reqs_a = recon_data[rid_a]
                reqs_b = recon_data[rid_b]
                matched_count = 0
                for ra in reqs_a:
                    has_match = False
                    for rb in reqs_b:
                        key = (item_id, ra["req_id"], rb["req_id"])
                        key_rev = (item_id, rb["req_id"], ra["req_id"])
                        if key in matches or key_rev in matches:
                            has_match = True
                            break
                    if has_match:
                        matched_count += 1
                min_size = min(len(reqs_a), len(reqs_b))
                agreement = matched_count / min_size if min_size > 0 else 0.0
                pairwise.append(
                    {
                        "reconstructor_a": rid_a,
                        "reconstructor_b": rid_b,
                        "agreement": agreement,
                        "matched": matched_count,
                        "total_a": len(reqs_a),
                        "total_b": len(reqs_b),
                    }
                )

        full_disagreement = sum(1 for p in pairwise if p["agreement"] == 0.0)

        # Singleton set: requirements returned by exactly one reconstructor.
        # Keyed by (reconstructor_id, req_id) to avoid cross-reconstructor collisions.
        req_counts = defaultdict(int)
        for rid in recon_ids:
            for r in recon_data[rid]:
                req_counts[(rid, r["req_id"])] += 1
        # A singleton is a req_id that appears for exactly one reconstructor
        # (i.e. its unique key count == 1, and no other reconstructor has it).
        # We report the full (reconstructor_id, req_id) keys for clarity.
        singletons = [f"{rid}:{req_id}" for (rid, req_id), cnt in req_counts.items() if cnt == 1]

        results.append(
            {
                "item_id": item_id,
                "pairwise": pairwise,
                "full_disagreement_count": full_disagreement,
                "singleton_set": singletons,
            }
        )
    return results


# ---- run-record wiring (added; logic above is unchanged) --------------------
import os  # noqa: E402
import sys  # noqa: E402
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
    if len(argv) != 4:
        print("Usage: agree.py <requirements.jsonl> <matches.jsonl> <agreement.jsonl>", file=sys.stderr)
        return 1

    def body():
        reqs = load_requirements(argv[1])
        matches = load_matches(argv[2])
        results = compute_agreement(reqs, matches)
        with open(argv[3], "w", encoding="utf-8") as fh:
            for res in results:
                fh.write(json.dumps(res, ensure_ascii=False) + "\n")
        return ("ok" if results else "empty"), {"rows": len(results)}, ""
    return runrecord.run("b4/agree.py", argv[1:], None, [argv[1], argv[2]], argv[3], body)


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
