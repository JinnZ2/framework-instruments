#!/usr/bin/env python3
"""B4.2 reconstruct.py — emit one prompt file per (item, reconstructor).

Input:  validated_items.jsonl, reconstructors.jsonl
Output: one JSON file per (item_id, reconstructor_id) in out_dir/
Each output contains ONLY the field `text_verbatim`.
"""

import json
import os
import sys


def emit_prompts(items_path, reconstructors_path, out_dir):
    items = []
    with open(items_path, "r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                items.append(json.loads(line))

    recons = []
    with open(reconstructors_path, "r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                recons.append(json.loads(line))

    os.makedirs(out_dir, exist_ok=True)

    for item in items:
        for recon in recons:
            rid = recon["reconstructor_id"]
            iid = item["item_id"]
            payload = {"text_verbatim": item["text_verbatim"]}
            # Hard assert: no other field may be present
            assert set(payload.keys()) == {"text_verbatim"}, (
                f"Prompt for {iid}/{rid} contains extra fields"
            )
            fpath = os.path.join(out_dir, f"{iid}_{rid}.json")
            with open(fpath, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, ensure_ascii=False, indent=2)
                fh.write("\n")

    print(f"Emitted {len(items) * len(recons)} prompt files to {out_dir}")


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
    if len(argv) != 4:
        print("Usage: reconstruct.py <items.jsonl> <reconstructors.jsonl> <out_dir>", file=sys.stderr)
        return 1

    def body():
        emit_prompts(argv[1], argv[2], argv[3])
        n = len([f for f in os.listdir(argv[3]) if f.endswith(".json")]) if os.path.isdir(argv[3]) else 0
        return ("ok" if n else "empty"), {"prompt_files": n}, ""
    return runrecord.run("b4/reconstruct.py", argv[1:], None, [argv[1], argv[2]], argv[3], body)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
