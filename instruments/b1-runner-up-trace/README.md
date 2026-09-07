# B1 — Runner-Up Trace (offline scoring half)

Scores whether a forced runner-up continuation returns to the base continuation
across a distance sweep. It calls no model, judges neither branch, and assigns
no label. Stages A–C of the reference spec (base pass, candidate selection,
forced continuation) run elsewhere and arrive as `base.jsonl` and `traces.jsonl`.

## Pipeline

| Stage | Command | Writes |
|---|---|---|
| Validate | `python3 b1_schema.py base.jsonl traces.jsonl` | run record only |
| Score | `python3 b1_score.py base.jsonl traces.jsonl separations.jsonl` | one row per (i, branch_rank, D, L) |
| Permute | `python3 b1_permute.py separations.jsonl SEED separations_permuted.jsonl` | the null; seed on every row |
| Summarise | `python3 b1_summarise.py separations.jsonl summary.jsonl` | run identically on both files |
| Report | `python3 b1_report.py summary.jsonl summary_permuted.jsonl report.md` | six sections; `void` if the permuted summary is missing |

Every command appends one row to `runs.jsonl` in the working directory, on
success and on failure alike (`ok`, `empty`, `void`, `error`).

## Definitions, as scored

- `D` ∈ {8, 16, 32, 64, 128}, by truncating the stored 128-token continuation.
- `L` ∈ {2, 4, 8}, written into every row. `resync_D = 1` when the two
  truncations end in the same aligned run of at least `L` tokens. The 4-token
  value in the reference spec is arbitrary; sweeping it is how the joint gets
  reported instead of hidden.
- `div_D` is token-level Levenshtein distance divided by the longer truncation.
- `gap_i = logprob_taken − logprob(forced_token)`, read from `topk`.

Declared reading: a rejoin is an ALIGNED suffix match. A continuation that
rejoins after a token-count shift scores 0. `div_D` does not depend on `L`,
so adjacent-L stability is 1.0 by construction; `L` carries information
through `resync_D` only.

## The permutation null

The null shuffles which position carries which `(ent_i, gap_i, resync_D,
div_D)` tuple, independently inside each `(case_id, model_id, branch_rank, D)`
stratum. Per-group means and rates are unchanged by construction; what the
null removes is the cross-D coherence of position sets. A global relabelling
of `i` would leave every summary identical and the null could never fire —
that was the shipped behaviour (arena specimen SPEC-005). If every stratum
holds one position the permutation is the identity and `b1_permute.py`
refuses with status `void`, so a two-case run cannot print a real-vs-permuted
table of a file against itself (`docs/reviews/`, KR_008). The permuted result
is a second output, never a gate.

## Nulls in section 6 of the report

The reference spec's N1–N5, each with the number it was decided on and the
threshold it was compared against (declared choices in `b1_report.py`). N5
(top-k sensitivity) is not evaluable from the scored file and says so.

## Inputs

`base.jsonl`: `case_id, model_id, i, token_taken, logprob_taken, topk,
entropy_i, entropy_basis` (`full` or `topk`, required). `traces.jsonl`:
`case_id, model_id, i, branch_rank (>= 2), forced_token, continuation
(<= 128 tokens), base_continuation (same length)`. Cross-file rules: every
trace position exists in base, `forced_token` is in that row's `topk` and is
not `token_taken`. Rejections name the file, line and field.

Governing specifications: [`runner-up-trace.md`](../../docs/specifications/runner-up-trace.md),
[`frame-instruments-ordered-queue.md`](../../docs/specifications/frame-instruments-ordered-queue.md).
