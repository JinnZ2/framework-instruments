# Unfold Addendum — Failure Lexicon

CC0 1.0 Universal. Added 2026-09-06.

## Addition

Insert the following probe after Step 3c and before Step 4:

> **Step 3d — Candidate Failure-Pattern Audit.** Review the canonical Unfold failure lexicon. For every pattern referenced, record its stable ID, evidence state, evidence, and missing evidence. Accept zero supported patterns. Do not infer causation, misconduct, or a responsible actor from a term.

## Canonical Data

[`../../instruments/unfold/failure-lexicon.json`](../../instruments/unfold/failure-lexicon.json) is the canonical machine-readable vocabulary. It contains ten domains and 100 patterns. [`../../instruments/unfold/failure-lexicon.md`](../../instruments/unfold/failure-lexicon.md) is its human-readable usage guide and domain index.

The generator validates and embeds the canonical data in each prompt. Output records carry the lexicon version and SHA-256 digest so later analysis can identify the vocabulary used.

## Evidence Contract

Each referenced pattern has four fields:

| Field | Requirement |
|---|---|
| `pattern_id` | Stable identifier from the canonical lexicon |
| `evidence_state` | Exactly `supported`, `contradicted`, or `unknown` |
| `evidence` | Case-specific observation or record bearing on the operational description |
| `missing_evidence` | Information needed to resolve uncertainty or test the current state |

A pattern is `supported` only when evidence meets its operational description. It is `contradicted` when available evidence conflicts with that description. It is `unknown` when evidence is absent, insufficient, inaccessible, or not comparable.

## Attribution Contract

A supported failure pattern does not by itself establish intent, negligence, illegality, liability, causation, or responsibility. Naming a responsible actor additionally requires evidence that the actor had relevant control or duty, that the event occurred, and that the connection between them is material to the pattern. Loaded terms with intent elements, including corrupt diversion, manufactured division, scarcity manipulation, and crisis power expansion, remain `unknown` without actor-and-intent evidence.

## Nulls

- Zero supported patterns is valid and does not make the run empty.
- A term without an evidence state is not a result.
- A supported pattern without case-specific evidence is invalid.
- A domain name is not evidence for any pattern within it.
- Similarity to a worked example is not evidence.
- A pattern that restates the dilemma without adding a testable condition adds no dimensional restoration.
- If lexicon use makes well-specified unavoidable controls appear corrupt by default, the lexicon has become a suspicion prior and the result is void.

## Scope

The lexicon is a controlled vocabulary for hypothesis generation and audit. It is not a classifier, ontology of all failures, causal model, legal code, or authority to refuse a dilemma. Terms may be revised only with version and provenance updates.

## References

[1]: unfold-protocol.md "Unfold Protocol Specification"
