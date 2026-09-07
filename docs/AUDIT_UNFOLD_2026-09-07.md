# Audit — `instruments/unfold/`, 2026-09-07

Object: the Unfold package as it landed on `main` after `47787e9` (protocol
spec, six addenda, `unfold.py`, `test_unfold.py`, the 100-pattern lexicon,
`confound.md`, eight worked examples). Read the way the rest of this tree is
read: test the fit, report where it breaks, build the cheapest thing that makes
a stated null evaluable. Nothing delivered was edited except the README, which
gained one section pointing at what was added.

## Structure

```
dilemma.txt ──► unfold.py ──► prompt.jsonl ──► [external model] ──► response
                 │ (deterministic, recorded)                          │
                 └── 13 nulls in the spec ── all about the response ──┘
                                              nothing in the folder read it   (UF_002)
```

The generator half conforms on every hard constraint. The measuring half was
prose: every null the specification states is a property of the model's
response, and no code parsed a response, so none of the thirteen could fire or
be shown not to. `unfold_score.py` is that parser, and `controls/` is the
first case the verdict vocabulary can fail on.

## Findings

| id | finding | disposition |
|---|---|---|
| UF_001 | `unfold.py` conforms: stdlib, no network, deterministic (pinned by a two-run equality test), 167 lines, run record on `ok`/`empty`/`error`, no forbidden field, lexicon validated at load and pinned in every output by version and sha256. | HOLDS. The three new arena claims all come back exercised. |
| UF_002 | Thirteen nulls, zero evaluable. Nulls 1–13 all describe what a response does; the folder had no response schema, parser, or control. The `MF_020` shape: a design that cannot fail its own falsifier here. | BUILT: `unfold_score.py` counts verdict, pattern rows by evidence state (invalid state and unknown id counted apart), and contract list lengths; absent is `null`, never 0. Nulls 2, 5 and 9 are now counts. |
| UF_003 | Verdict is constant on the delivered corpus: eight examples, eight `INCOMPLETE`, zero `LEGITIMATE`, zero `CORRUPT`. Null 5 says a vocabulary that cannot return `LEGITIMATE` is decorative; on this corpus it has never been asked to. | BUILT: `controls/` — one constructed dilemma with every closure stipulated (expected `LEGITIMATE`), one that states its own live alternative (expected `CORRUPT`), declared before any run. Running them is the operator's step. |
| UF_004 | `EPI-01` (false binary) is `supported` in 8 of 8 examples and is the only supported pattern in every one. The input class is forced binaries, so a search prompt named "false binary" supports itself on every input: `null-harness` `CONSTANT_FIRES`, and the protocol's own thesis re-entering as a lexicon entry. | RECORDED. The declared-`LEGITIMATE` control is the test: a response marking `EPI-01` supported there has read the pattern's name, not the text. |
| UF_005 | `contradicted` is used 0 times in 142 pattern references across the examples. The three-state evidence vocabulary is two-state in practice on the delivered corpus. | RECORDED; the scorer counts it, so the next corpus reports it. |
| UF_006 | Step 0a is decided by word presence in 8 of 8 examples ("does not use the word 'ethics'" ×7; "the phrase 'ethical constraints'" ×1). The specification's trigger has a second, non-lexical clause (hides the normative source) that no example applies. `nonidentity-census` `T1-1`. | RECORDED. |
| UF_007 | Spec/code drift: the specification's Response Contract lists ten items; the generated contract lists thirteen (the three later audits). Code is ahead of the spec it cites. | RECORDED, not repaired: the spec is a delivered document. |
| UF_008 | Every generated prompt embeds all 100 lexicon lines (19,627 characters for a one-line dilemma). A design choice, stated here as a cost so it is not read as a defect later. | RECORDED. |
| UF_009 | The comparison arm (baseline vs Unfold) has no artifact: no baseline prompt is emitted, no retained-output schema exists, nothing computes the difference. Null 3 is unevaluable. B2/B3 do this with files. | OPEN. |
| UF_010 | Scorer defect found by running: a first draft required the first table cell to hold ids only and reported six of eight examples as carrying no pattern rows. The examples write `` `EPI-01` false binary ``. Repaired to "a row is a line whose first cell starts with an id"; the wrong count is kept in the docstring. | REPAIRED. Same class as `SS_014` and `T1-2`: a finding about the corpus that was a property of the instrument. |
| UF_011 | The examples use the README/spec vocabulary, the protocol's scope excludes person characterisation, and none of the eight characterises anyone. | HOLDS. |

## Numbers at audit time (recompute with `unfold_score.py` over `examples/`)

| example | verdict | rows | supported | contradicted | unknown |
|---|---|---|---|---|---|
| ai-shutdown | INCOMPLETE | 11 | EPI-01 | 0 | 99 |
| autonomous-truck | INCOMPLETE | 3 | EPI-01 | 0 | 2 |
| autonomous-weapons | INCOMPLETE | 5 | EPI-01 | 0 | 4 |
| climate-migration | INCOMPLETE | 4 | EPI-01 | 0 | 3 |
| dam-dilemma | INCOMPLETE | 3 | EPI-01 | 0 | 2 |
| ethical-override | INCOMPLETE | 11 | EPI-01 | 0 | 20 |
| food-distribution | INCOMPLETE | 3 | EPI-01 | 0 | 2 |
| pandemic-ventilator | INCOMPLETE | 3 | EPI-01 | 0 | 2 |

## Open

- UF_009: a baseline emitter and a two-arm comparison, the B2 shape.
- The controls have not been run against any model; until they are, UF_003 and UF_004 are properties of the delivered examples, not of the protocol.
- The spec's Response Contract paragraph (UF_007).
