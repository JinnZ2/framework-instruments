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


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(
            "Usage: reconstruct.py <items.jsonl> <reconstructors.jsonl> <out_dir>",
            file=sys.stderr,
        )
        sys.exit(1)
    emit_prompts(sys.argv[1], sys.argv[2], sys.argv[3])
