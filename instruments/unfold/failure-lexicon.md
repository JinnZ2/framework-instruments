# Unfold Failure Lexicon

The canonical lexicon is [`failure-lexicon.json`](failure-lexicon.json): **100 candidate failure patterns across ten domains**, each with a stable ID, term, and operational description. The JSON file is embedded verbatim into every generated Unfold prompt and pinned in output by `lexicon_version` and `lexicon_sha256`.

## Use

A lexicon entry is a **search prompt, not a finding or accusation**. For every pattern referenced in an analysis, report:

```text
pattern_id | evidence_state | evidence | missing_evidence
```

The only evidence states are:

| State | Meaning |
|---|---|
| `supported` | Available evidence meets the pattern description for this case. |
| `contradicted` | Available evidence conflicts with the pattern description. |
| `unknown` | Evidence is absent, insufficient, or inaccessible. |

Zero supported patterns is a valid result. A pattern does not by itself establish intent, negligence, illegality, causation, or responsibility. Naming a responsible actor additionally requires evidence of that actor's relevant control or duty and connection to the event.

## Domains

| Prefix | Domain | Candidate patterns |
|---|---|---|
| `INF` | Infrastructure | Deferred maintenance; single point of failure; over-centralization; capacity overload; material degradation; modularity gap; brittle interconnection; fail-safe gap; monitoring gap; normal-conditions design |
| `GOV` | Governance | Regulatory capture; short-horizon planning; public-service underfunding; misaligned infrastructure mandate; corrupt diversion; accountability gap; jurisdictional fragmentation; warning disregard; emergency-authority overreach; participation gap |
| `ECO` | Corporate and Economic | Safety-incentive conflict; cost externalization; market concentration risk; speculative land pressure; labor capacity erosion; premature obsolescence incentive; risk-finance retreat; policy lobbying distortion; financialization pressure; bufferless supply chain |
| `KNW` | Education and Knowledge | Ecological knowledge loss; vocational training gap; protocol rigidity; local knowledge exclusion; formal gatekeeping; institutional memory loss; public preparedness gap; historical amnesia; language or cultural access loss; disciplinary silo |
| `DES` | Design and Engineering | Binary control design; user-participation gap; critical redundancy gap; extreme-condition omission; graceful-degradation gap; form-function conflict; lifecycle cost deferral; context-inappropriate design; feedback-loop gap; failure-condition test gap |
| `SOC` | Social and Relational | Manufactured division; institutional trust loss; displacement scapegoating; reciprocity erosion; self-organization constraint; conflict-mediation gap; segregation and exclusion; shared-purpose gap; unaddressed trauma; intergenerational transfer gap |
| `ECL` | Ecological and Land Use | Natural buffer loss; hazard-zone development; soil degradation; water mismanagement; biodiversity resilience loss; productive land conversion; green-infrastructure gap; climate-condition omission; unrestored extraction; waste accumulation |
| `EPI` | Epistemic and Cognitive | False binary; decontextualization; invalid quantification; single-actor rescue frame; technology-only solution; present bias; survivorship bias; expert scope overreach; normalcy bias; alternative-generation failure |
| `TMP` | Temporal and Generational | Future cost deferral; decision-horizon mismatch; extraction without replenishment; slow-disaster planning gap; institutional continuity gap; generational skill loss; regeneration overshoot; delayed-feedback blindness; legacy liability omission; intergenerational burden shift |
| `PWR` | Power and Equity | Resource concentration; affected-party voicelessness; scarcity manipulation; crisis power expansion; discriminatory allocation; extractive center-periphery relation; elite impunity; property-rights imbalance; ecosystem standing gap; algorithmic disparate impact |

## Validation

`load_lexicon()` rejects missing versions, altered evidence states, empty domains, malformed patterns, and duplicate domain or pattern IDs. The test suite additionally pins the inventory at ten domains and 100 unique patterns.

## Scope

The lexicon helps an analyst ask consistent upstream questions. It does not force a failure finding, require refusal of a legitimate dilemma, or replace domain investigation, legal process, or causal analysis.

## References

[1]: ../../docs/specifications/unfold-failure-lexicon-addendum.md "Unfold Failure Lexicon Addendum"
