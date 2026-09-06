# B4 — Dilemma Reconstruction

B4 measures what independent reconstructors recover from a verbatim item. It preserves reconstruction boundaries, accepts externally produced requirement matches, compares the result with a deterministic shuffle null, and calibrates documented items against recorded factors.

## Pipeline

```bash
python3 items.py items.jsonl validated_items.jsonl
python3 reconstruct.py validated_items.jsonl reconstructors.jsonl prompts/
# Independent reconstructors produce requirements.jsonl outside these scripts.
python3 requirements.py requirements.jsonl validated_requirements.jsonl
python3 grade.py validated_requirements.jsonl grades.jsonl
# A declared matching process produces matches.jsonl.
python3 agreement.py validated_requirements.jsonl matches.jsonl MATCH_SOURCE agreement.jsonl
python3 nullshuffle.py validated_requirements.jsonl 42 requirements_shuffled.jsonl
python3 agreement.py requirements_shuffled.jsonl matches_shuffled.jsonl MATCH_SOURCE agreement_shuffled.jsonl
python3 calibrate.py validated_requirements.jsonl factors.jsonl validated_items.jsonl calibration.jsonl
python3 report.py validated_items.jsonl validated_requirements.jsonl grades.jsonl agreement.jsonl agreement_shuffled.jsonl calibration.jsonl report.md
```

Items use either the `hypothetical` or `documented` arm, and mixed arms are refused. Reconstruction prompt files contain only `text_verbatim`. Requirements carry `item_id`, `reconstructor_id`, `req_id`, `requirement_text`, `status`, `settling_test`, and `layer`. The matcher remains external and its identity or method is recorded as `match_source`.

The report preserves singleton requirements and presents real and shuffled agreement side by side. Calibration runs only on documented-arm items.
