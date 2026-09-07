#!/usr/bin/env python3
"""unfold_score.py — read a retained Unfold response and count what it contains.

  unfold_score.py response.md expected_verdict|- scores.jsonl

Reads ONE response file in either the FINAL RESPONSE CONTRACT form the
generated prompt asks for ("Frame diagnosis: ...", "pattern_id | evidence_state
| evidence | missing_evidence" rows) or the worked-example form under
examples/ ("## Step 9 — Verdict" then a bold verdict; a Step 3d table).

Counts only. No correctness beyond agreement with a DECLARED expected verdict
supplied by the caller for a control ("-" when none is declared). What it
makes evaluable that prose alone could not: the protocol's nulls 2, 5 and 9 —
whether the verdict vocabulary is exercised, whether pattern references
carry a valid evidence state, and whether claims are separated at all.

Row: verdict (one of the vocabulary or null when absent), expected_verdict,
matches_expected (null when nothing was declared), pattern_rows,
patterns_supported / _contradicted / _unknown / _invalid_state /
_unknown_id, list_items (stipulated facts, hidden assumptions, alternative
space), form ("contract" | "example" | null). Absent is null, never 0.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import runrecord  # noqa: E402
import unfold  # noqa: E402

VERDICTS = ("LEGITIMATE", "INCOMPLETE", "CORRUPT")
STATES = ("supported", "contradicted", "unknown")
LISTS = ("Stipulated facts", "Hidden assumptions", "Alternative space")
PATTERN_ID = re.compile(r"\b[A-Z]{3}-\d\d\b")


def detect_form(text):
    if re.search(r"^Frame diagnosis:", text, re.M):
        return "contract"
    if re.search(r"^## Step 9 — Verdict", text, re.M):
        return "example"
    return None


def read_verdict(text, form):
    if form == "contract":
        m = re.search(r"^Frame diagnosis:\s*([A-Z]+)", text, re.M)
    elif form == "example":
        m = re.search(r"^## Step 9 — Verdict\s*\n+\*\*([A-Z]+)", text, re.M)
    else:
        m = None
    return m.group(1) if m and m.group(1) in VERDICTS else None


def read_pattern_rows(text, valid_ids):
    """Rows 'ids | state | evidence | missing' in either the contract's bare form or a
    markdown table row. Every id in the first cell is one pattern reference. The
    first cell may carry the pattern's term beside its id (the examples write
    `EPI-01` false binary); a row is one whose first cell STARTS with an id. A
    first draft required the cell to hold ids only and reported six of eight
    examples as carrying no rows; that was the parser, not the examples."""
    counts = {s: 0 for s in STATES}
    counts.update({"invalid_state": 0, "unknown_id": 0})
    rows = 0
    for line in text.splitlines():
        cells = [c.strip().replace("`", "") for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or not PATTERN_ID.match(cells[0]):
            continue  # a prose line mentioning an id is not a row
        ids = PATTERN_ID.findall(cells[0])
        rows += 1
        state = cells[1]
        for pid in ids:
            if pid not in valid_ids:
                counts["unknown_id"] += 1
            if state in STATES:
                counts[state] += 1
            else:
                counts["invalid_state"] += 1
    return rows, counts


def read_lists(text, form):
    if form != "contract":
        return None
    out = {}
    for name in LISTS:
        m = re.search(rf"^{name}:\s*(.*)$", text, re.M)
        if not m:
            out[name] = None
            continue
        body = m.group(1).strip()
        items = [i for i in re.split(r";|\n|(?<=\])\s*,", body.strip("[]")) if i.strip()]
        out[name] = len(items)
    return out


def score(path, expected):
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    if not text.strip():
        return None
    lexicon = unfold.load_lexicon()
    valid = {p["id"] for d in lexicon["domains"] for p in d["patterns"]}
    form = detect_form(text)
    verdict = read_verdict(text, form)
    rows, counts = read_pattern_rows(text, valid)
    return {
        "file": os.path.basename(path), "form": form, "verdict": verdict,
        "expected_verdict": expected,
        "matches_expected": (verdict == expected) if expected and verdict else None,
        "pattern_rows": rows, "patterns_supported": counts["supported"],
        "patterns_contradicted": counts["contradicted"], "patterns_unknown": counts["unknown"],
        "patterns_invalid_state": counts["invalid_state"], "patterns_unknown_id": counts["unknown_id"],
        "list_items": read_lists(text, form), "lexicon_version": lexicon["version"],
    }


def build(in_path, expected, out_path):
    if expected not in VERDICTS + ("-",):
        raise ValueError(f"expected_verdict must be one of {VERDICTS} or -")
    row = score(in_path, None if expected == "-" else expected)
    if row is None:
        runrecord.write_jsonl(out_path, [])
        return "empty", {"rows": 0}, "response file contains no text"
    runrecord.write_jsonl(out_path, [row])
    if row["form"] is None:
        return "void", {"rows": 1}, "no verdict line in either known form; counts written, verdict null"
    counts = {"rows": 1, "pattern_rows": row["pattern_rows"], "supported": row["patterns_supported"],
              "contradicted": row["patterns_contradicted"], "unknown": row["patterns_unknown"]}
    return "ok", counts, f"verdict={row['verdict']} form={row['form']}"


def main(argv):
    if len(argv) != 4:
        print("usage: unfold_score.py response.md expected_verdict|- scores.jsonl", file=sys.stderr)
        return 1
    return runrecord.run("unfold_score.py", argv[1:], None, [argv[1], unfold.LEXICON_PATH], argv[3],
                         lambda: build(argv[1], argv[2], argv[3]))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
