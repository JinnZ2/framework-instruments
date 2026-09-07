# Audit of an external review — Kimi deep-research report, 2026-09-07

**Object.** `frameworkinstrumentsdeepresearch.zip`, sha256
`13ab0dba8538274808abedb451b345576432aa2e7ea944951c91b2b4db82ab86`: one
markdown report (142 lines) and five figures, inspecting this repository at
commit `47787e9` (the merge of `claude/frame-instruments-pipeline-dsz99e`).

**Not landed.** The report's §7 characterises the author and the wider
ecosystem. The ordered-queue specification's OUT OF SCOPE rule binds every
document in this tree, so the report stays outside it; its hash is recorded
above, and every number it states about this repository is transcribed into
`check_report.py` as data and recomputed there. Run:

```bash
python3 docs/reviews/2026-09-07-kimi-deep-research/check_report.py checks.jsonl
```

External-literature claims (MMLU-Redux, GSM1k, the DeepMind enclave pilot,
ARC-AGI-3 harness results, NIST, BetterBench, mutation-scored LLM judges) are
**UNVERIFIED** here: the egress policy refuses their sources. Nothing below
rests on any of them.

## Findings

| id | report states | observed | reading |
|---|---|---|---|
| KR_001 | Four commits, all 2026-09-06; created 17:07 UTC; last push 22:59 UTC; 0 stars, 0 forks; four self-filed open issues. | All hold. Merge commit `47787e9` is 17:59 −05:00 = 22:59 UTC. Issues #1–#4 (run record, fixtures, schema, N1–N5) opened 17:08 UTC by the repository owner. | CONSISTENT. The four issues are the four items `docs/AUDIT_2026-09-06.md` closed, and they are still open; closing them is the operator's call. |
| KR_002 | "roughly 4,200 lines of Python across 23 scripts" | 4,240 lines over 34 `.py` files including tests; 2,933 over 25 without tests; 23 run-record scripts. | Both numbers are right and do not share a frame: the line count includes the tests, the script count excludes them. |
| KR_003 | "seven unbuilt instrument specifications" | Eight files under `docs/specifications/`; two are built (ordered queue, runner-up trace), one is the telemetry protocol; the report's own Figure 1 shows four specification-only rows and one marker. | Count differs inside the report (7 in prose, 5 in its figure). |
| KR_004 | Coverage 69 of 72, the three unexercised pairs named. | Reproduced at `47787e9`. On `main` after the `unfold/` package: 72 of 75, same three. | CONSISTENT, dated. |
| KR_005 | 12 specimens: 10 `false`, 1 `partial`, 1 `undifferentiated`; 11 `detector_exercised: false`; two masking chains. | Reproduced from `arena/specimens.jsonl`, chains `SPEC-002<-001`, `SPEC-007<-005`. | CONSISTENT. |
| KR_006 | `path_probe`: 10 of 11 claims exercised; `test_permutation_preserves_count_and_multiset` still passes. | Reproduced (seed 7). | CONSISTENT. Left standing as the arena's live finding. |
| KR_007 | Figure 3 is "a case whose forced continuation rejoins the base after a 20-token shift", scoring `resync = 0` at short D and resynchronising "once D exceeded the shift, because a rejoin is defined as an aligned suffix match". | The five printed means (1, 1, 0.8125, 0.6562, 0.5781) reproduce **exactly** from an ALIGNED rejoin at token 20 plus a never-rejoin case. A continuation shifted by even one token returns `resync = 0` at every D under the aligned reading. | The fixture was not shifted; the D ≥ 32 behaviour is D crossing the rejoin point plus L. The report's conclusion (code honours the declared reading) is right; the mechanism it gives is inverted, since the aligned reading is precisely what makes a shifted case never resync. |
| KR_008 | "two methodological nulls (N2, N4) firing with their triggering numbers printed" | Both fire because the fixture has one position per stratum: N2's high-entropy decile is a single row, and the permutation is the identity (`single_position_strata = strata = 10` in the permute run record), so real and permuted Jaccard are both 1.0. | Read as instrument behaviour, they are the n = 2 artefact; the run record carried the diagnostic and the report did not read it. **Changed by this audit:** `b1_permute.py` now refuses an identity permutation with status `void`, so a two-position run cannot print a real-vs-permuted table of a file against itself. |
| KR_009 | "OpenAI's 2026-09-03 announcement that GPT-4o … will retire from ChatGPT on 2026-02-13" | Retirement precedes the announcement by 202 days. | Internally inconsistent; one date is wrong. Carried, source unreachable. |
| KR_010 | Five verbatim quotes attributed to the frame-location, backcast and routing specifications. | All five present verbatim. | CONSISTENT. |
| KR_011 | The unmerged second build in `Simulators` is "the split-authorship principle applied to the project's own construction, with an AI system as one of the arms". | Both builds' commits carry the same `Co-Authored-By` trailer (this model), one day apart. | Two arms of one author class do not decorrelate on authorship (`triad-playground` `TP_008`'s shared-bias result). The report's §8 asks for outside verification of exactly this and does not notice its §7 sentence already assumes it. |
| KR_012 | SPEC-003 "is representative" of "the ways greens lie" in this repository; the arena "quantifies the historical record". | SPEC-001..003 describe `full_instrument_suite`, a package not in this repository, entered verbatim from a work order and marked unverified in `arena/README.md`. | Provenance flattened: three of the twelve specimens are carried, not observed here. |
| KR_013 | "Only six of twelve exist as tested code." | B1–B4, arena, run record. | CONSISTENT. |
| KR_014 | "no implemented instrument has ever touched real model data" | True at `47787e9` and now; B2/B3 have no case material in either repository. | CONSISTENT, and the sharpest sentence in the report. |

## What the report gets right that mattered

The probe result (KR_006) and the coverage residue (KR_004) were checked by
running, not by reading, and both held. The verdict that the instruments are
"built, calibrated against synthetic fixtures, and wired to record their own
failures; the measurement of the world has not yet begun" is the same
sentence `docs/AUDIT_2026-09-06.md` ends on.

## Open

- Issues #1–#4 remain open against work that is merged.
- KR_007 and KR_008 are the same shape: a two-case run produces numbers that
  look like measurements. The aligned/shifted reading (`FI_017`) is still one
  reading; the shifted alternative is unbuilt.
