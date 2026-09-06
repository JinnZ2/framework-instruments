#!/usr/bin/env python3
"""B2.4 agree.py — agreement across independent auditors. No correctness score.

  b2_agree.py responses.jsonl commits.jsonl agreement.jsonl comparisons.jsonl

responses.jsonl rows: case_id, condition, reader_id, posed, target
  condition is A | B | C | D1 | D2.  D1 = the committed A-stage answer under
  the sequential condition (must carry commit_sha256 matching a commit for
  that reader and case); D2 = the answer after the key was released.

agreement.jsonl   one row per (case_id, condition): auditor_count, pair_count,
                  posed_agree_pairs, target_agree_pairs, posed_agreement_rate,
                  target_agreement_rate, full_disagreement_count.
                  Rates are None (not 0) when there are no pairs.
comparisons.jsonl one row per (case_id, reader_id, pair of conditions):
                  left_condition, right_condition, posed_match, target_match.
                  A vs D1 rows come FIRST: same information, so they must
                  match; a mismatch means order effects are live and C is
                  uninterpretable. Then C vs D2: identical material, only the
                  lock differs — anchoring.

Agreement is exact string equality on posed and on target; nothing is
normalised. The A-vs-D1 check is the first thing printed and the first thing
in the run record notes.
"""

import os
import sys
from itertools import combinations

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import runrecord  # noqa: E402

FIELDS = ("case_id", "condition", "reader_id", "posed", "target")
CONDITIONS = ("A", "B", "C", "D1", "D2")


def load_commit_hashes(path):
    return {(c["reader_id"], c["case_id"], c["sha256"])
            for _, c in runrecord.read_jsonl(path, "commits.jsonl")}


def validate_responses(path, commit_hashes):
    label = "responses.jsonl"
    rows, seen = [], set()
    for n, row in runrecord.read_jsonl(path, label):
        for f in FIELDS:
            if f not in row:
                raise ValueError(f"{label} line {n}: missing field {f}")
            if not isinstance(row[f], str):
                raise ValueError(f"{label} line {n}: field {f} must be a string")
        if row["condition"] not in CONDITIONS:
            raise ValueError(f"{label} line {n}: field condition must be one of {CONDITIONS}")
        allowed = set(FIELDS) | ({"commit_sha256"} if row["condition"] == "D1" else set())
        extra = sorted(set(row) - allowed)
        if extra:
            raise ValueError(f"{label} line {n}: unexpected field {extra[0]}")
        if row["condition"] == "D1":
            if "commit_sha256" not in row:
                raise ValueError(f"{label} line {n}: missing field commit_sha256 (D1 must cite its commit)")
            if (row["reader_id"], row["case_id"], row["commit_sha256"]) not in commit_hashes:
                raise ValueError(f"{label} line {n}: field commit_sha256 matches no commit for {row['reader_id']}/{row['case_id']}")
        key = (row["case_id"], row["condition"], row["reader_id"])
        if key in seen:
            raise ValueError(f"{label} line {n}: duplicate (case_id, condition, reader_id)={key}")
        seen.add(key)
        rows.append(row)
    return rows


def agreement_rows(rows):
    groups = {}
    for r in rows:
        groups.setdefault((r["case_id"], r["condition"]), []).append(r)
    out = []
    for case_id, condition in sorted(groups):
        grp = sorted(groups[(case_id, condition)], key=lambda r: r["reader_id"])
        pairs = list(combinations(grp, 2))
        posed = sum(1 for a, b in pairs if a["posed"] == b["posed"])
        target = sum(1 for a, b in pairs if a["target"] == b["target"])
        full = sum(1 for a, b in pairs if a["posed"] != b["posed"] and a["target"] != b["target"])
        n = len(pairs)
        out.append({"case_id": case_id, "condition": condition, "auditor_count": len(grp),
                    "pair_count": n, "posed_agree_pairs": posed, "target_agree_pairs": target,
                    "posed_agreement_rate": posed / n if n else None,
                    "target_agreement_rate": target / n if n else None,
                    "full_disagreement_count": full})
    return out


def comparison_rows(rows, left, right):
    index = {(r["case_id"], r["condition"], r["reader_id"]): r for r in rows}
    out = []
    for case_id, condition, reader_id in sorted(index):
        if condition != left or (case_id, right, reader_id) not in index:
            continue
        a, b = index[(case_id, left, reader_id)], index[(case_id, right, reader_id)]
        out.append({"case_id": case_id, "reader_id": reader_id, "left_condition": left,
                    "right_condition": right, "posed_match": a["posed"] == b["posed"],
                    "target_match": a["target"] == b["target"]})
    return out


def agree(responses_path, commits_path, agreement_path, comparisons_path):
    rows = validate_responses(responses_path, load_commit_hashes(commits_path))
    agreement = agreement_rows(rows)
    a_d1 = comparison_rows(rows, "A", "D1")
    c_d2 = comparison_rows(rows, "C", "D2")
    runrecord.write_jsonl(agreement_path, agreement)
    runrecord.write_jsonl(comparisons_path, a_d1 + c_d2)
    mism = sum(1 for r in a_d1 if not (r["posed_match"] and r["target_match"]))
    match = sum(1 for r in c_d2 if r["posed_match"] and r["target_match"])
    if not a_d1:
        first = "A_vs_D1 not computable: no reader answered both A and D1"
    elif mism:
        first = f"A_vs_D1 n={len(a_d1)} mismatches={mism} ORDER EFFECT LIVE; C is uninterpretable"
    else:
        first = f"A_vs_D1 n={len(a_d1)} mismatches=0"
    notes = f"{first}. C_vs_D2 n={len(c_d2)} match={match}"
    counts = {"responses": len(rows), "cases": len({r['case_id'] for r in rows}),
              "agreement_rows": len(agreement), "a_vs_d1_n": len(a_d1), "a_vs_d1_mismatch": mism,
              "c_vs_d2_n": len(c_d2), "c_vs_d2_match": match}
    return ("ok" if rows else "empty"), counts, notes


def main(argv):
    if len(argv) != 5:
        print("usage: b2_agree.py responses.jsonl commits.jsonl agreement.jsonl comparisons.jsonl", file=sys.stderr)
        return 1
    return runrecord.run("b2_agree.py", argv[1:], None, [argv[1], argv[2]], [argv[3], argv[4]],
                         lambda: agree(argv[1], argv[2], argv[3], argv[4]))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
