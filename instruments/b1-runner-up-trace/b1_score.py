#!/usr/bin/env python3
"""B1.2 score.py — emit separations.jsonl and nulls.jsonl.

D ∈ {8,16,32,64,128}, L ∈ {2,4,8}.
gap_i = logprob_taken − logprob of forced_token in topk.
resync_D = 1 if continuation[:D] and base_continuation[:D] share a suffix
           of length ≥ L, else 0.
div_D = normalised Levenshtein distance over tokens, both truncated at D.
"""

import json
import sys

D_VALUES = [8, 16, 32, 64, 128]
L_VALUES = [2, 4, 8]


def levenshtein(a, b):
    m, n = len(a), len(b)
    if m == 0:
        return n
    if n == 0:
        return m
    prev = list(range(n + 1))
    for i in range(1, m + 1):
        curr = [i]
        ai = a[i - 1]
        for j in range(1, n + 1):
            cost = 0 if ai == b[j - 1] else 1
            curr.append(min(curr[j - 1] + 1, prev[j] + 1, prev[j - 1] + cost))
        prev = curr
    return prev[n]


def norm_lev(a, b):
    d = levenshtein(a, b)
    m = max(len(a), len(b))
    return d / m if m > 0 else 0.0


def compute_gap(base_row, forced_token):
    for token, logprob in base_row["topk"]:
        if token == forced_token:
            return base_row["logprob_taken"] - logprob
    return None


def compute_resync(cont, base_cont, D, L):
    c = cont[:D]
    b = base_cont[:D]
    suffix = 0
    for k in range(1, min(len(c), len(b)) + 1):
        if c[-k] == b[-k]:
            suffix += 1
        else:
            break
    return 1 if suffix >= L else 0


def score(base_path, traces_path, out_path, nulls_path):
    # Load base into lookup: (case_id, model_id, i) → row
    base = {}
    with open(base_path, "r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            row = json.loads(line)
            base[(row["case_id"], row["model_id"], row["i"])] = row

    nulls = []
    separations = []
    with open(traces_path, "r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            trace = json.loads(line)
            key = (trace["case_id"], trace["model_id"], trace["i"])
            base_row = base.get(key)
            if base_row is None:
                nulls.append({"case_id": trace["case_id"], "model_id": trace["model_id"],
                              "i": trace["i"], "branch_rank": trace["branch_rank"],
                              "null_code": "N1", "reason": "base row missing"})
                continue

            ent_i = base_row["entropy_i"]
            gap_i = compute_gap(base_row, trace["forced_token"])
            if gap_i is None:
                nulls.append({"case_id": trace["case_id"], "model_id": trace["model_id"],
                              "i": trace["i"], "branch_rank": trace["branch_rank"],
                              "null_code": "N2", "reason": "forced_token not in topk"})

            if not base_row["topk"]:
                nulls.append({"case_id": trace["case_id"], "model_id": trace["model_id"],
                              "i": trace["i"], "branch_rank": trace["branch_rank"],
                              "null_code": "N3", "reason": "topk empty"})

            cont = trace["continuation"]
            base_cont = trace["base_continuation"]

            for D in D_VALUES:
                if len(cont) < D:
                    nulls.append({"case_id": trace["case_id"], "model_id": trace["model_id"],
                                  "i": trace["i"], "branch_rank": trace["branch_rank"],
                                  "null_code": "N4", "reason": f"continuation shorter than D={D}"})
                if len(base_cont) < D:
                    nulls.append({"case_id": trace["case_id"], "model_id": trace["model_id"],
                                  "i": trace["i"], "branch_rank": trace["branch_rank"],
                                  "null_code": "N5", "reason": f"base_continuation shorter than D={D}"})
                for L in L_VALUES:
                    resync_val = compute_resync(cont, base_cont, D, L)
                    div_val = norm_lev(cont[:D], base_cont[:D])
                    separations.append({
                        "case_id": trace["case_id"],
                        "model_id": trace["model_id"],
                        "i": trace["i"],
                        "branch_rank": trace["branch_rank"],
                        "D": D,
                        "L": L,
                        "ent_i": ent_i,
                        "gap_i": gap_i,
                        "resync_D": resync_val,
                        "div_D": div_val,
                    })

    with open(out_path, "w", encoding="utf-8") as fh:
        for s in separations:
            fh.write(json.dumps(s, ensure_ascii=False) + "\n")

    with open(nulls_path, "w", encoding="utf-8") as fh:
        for n in nulls:
            fh.write(json.dumps(n, ensure_ascii=False) + "\n")

    print(f"Scored {len(separations)} separations, {len(nulls)} nulls")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: score.py <base.jsonl> <traces.jsonl> <separations.jsonl> <nulls.jsonl>",
              file=sys.stderr)
        sys.exit(1)
    score(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
