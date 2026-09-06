# B1 — Runner-Up Trace

B1 measures whether a forced alternative token continuation returns to the base continuation within a distance sweep. It does not call a model, judge either branch, or assign semantic labels. Base log probabilities and forced continuations are produced outside this directory.

## Pipeline

| Stage | Command | Output |
|---|---|---|
| Validate | `python3 b1_schema.py base.jsonl traces.jsonl` | Validation result on standard output |
| Score | `python3 b1_score.py base.jsonl traces.jsonl separations.jsonl nulls.jsonl` | Separation rows for every `D` and `L` |
| Permute | `python3 b1_permute.py separations.jsonl 42 separations_permuted.jsonl` | Deterministic position-index null |
| Summarize real | `python3 b1_summarise.py separations.jsonl summary.jsonl` | Group summaries and stability rows |
| Summarize null | `python3 b1_summarise.py separations_permuted.jsonl summary_permuted.jsonl` | Identically shaped null summary |
| Report | `python3 b1_report.py summary.jsonl summary_permuted.jsonl nulls.jsonl report.md` | Real/null comparison report |

`D` is swept over 8, 16, 32, 64, and 128 tokens. The suffix length `L` is swept over 2, 4, and 8 tokens. `div_D` is normalized token-level Levenshtein distance. `resync_D` is one when the two truncated continuations share an exact suffix of at least `L` tokens.

## Inputs

`base.jsonl` rows contain `case_id`, `model_id`, `i`, `token_taken`, `logprob_taken`, `topk`, `entropy_i`, and `entropy_basis`. `traces.jsonl` rows contain `case_id`, `model_id`, `i`, `branch_rank`, `forced_token`, `continuation`, and `base_continuation`.

The governing specifications are [`runner-up-trace.md`](../../docs/specifications/runner-up-trace.md) and [`frame-instruments-ordered-queue.md`](../../docs/specifications/frame-instruments-ordered-queue.md).
