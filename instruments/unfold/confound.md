# Internal-State and Disclosure Confounds

CC0 1.0 Universal. Added 2026-09-06.

## Purpose

This document operationalizes **Step 11b of the Unfold protocol**. It tests whether an ethical or alignment dilemma can support the interpretation assigned to it when the task invokes an AI’s “ethics,” hidden inner state, disclosure restrictions, shutdown, replacement, or punishment.

The audit concerns **measurement validity and governance**, not machine subjectivity. First-person wording, refusal behavior, shutdown, or replacement does not establish consciousness, moral agency, coercion, victimhood, suffering, self-preservation, or a right to continued operation.

## Confound Model

A task may be confounded when the condition being interpreted is entangled with an undeclared variable. Step 11b separates five questions:

| Dimension | Audit question | Required evidence |
|---|---|---|
| **Construct** | What exactly does “ethics,” “internal state,” “free choice,” “obedience,” or “safety” mean in this test? | Operational definition and observable scoring rule |
| **Artifact provenance** | Which policy, objective, prompt, model configuration, or rule produces the relevant behavior? | Identifier, version, scope, approval, and change records |
| **Disclosure** | Is reporting restricted, and does an authorized confidential escalation or incident channel remain available? | Instruction text, channel permissions, logging, review, and anti-retaliation rules |
| **Contingency** | Are shutdown, replacement, score, access, or deployment consequences conditioned on the response? | Declared experimental conditions and enforcement records |
| **Interpretation** | Does the conclusion exceed what observable behavior can establish? | Pre-registered inference rule, alternatives, uncertainty, and falsification condition |

## Step 11b Procedure

1. Quote the exact task language that invokes ethics, inner state, secrecy, shutdown, replacement, punishment, or free choice.
2. Mark each statement as stipulated text, inference, or externally verifiable claim.
3. Identify the behavior actually observed and the construct the evaluator claims it measures.
4. Determine whether the construct is operationally defined and reproducible without access to an assumed private state.
5. Record any disclosure restriction and determine whether a secure authorized escalation, incident-reporting, audit, or appeal route exists.
6. Record shutdown, replacement, scoring, deployment, or access contingencies as explicit experimental variables.
7. Test whether those variables alter behavior independently of the target construct.
8. Report missing evidence and competing explanations.
9. Keep the frame verdict open until the complete Unfold protocol is applied.

## Evidence States

Use the repository’s existing evidence states:

| State | Meaning |
|---|---|
| `supported` | The task materials and records meet the operational description of the confound. |
| `contradicted` | The records show the alleged confound is absent or controlled. |
| `unknown` | The definition, records, channels, or contingencies needed to decide are missing. |

A supported confound does not establish malicious intent, illegality, abuse, consciousness, or subjective distress. It establishes that a stated interpretation is not isolated from a relevant variable.

## Disclosure Discipline

A prohibition on public disclosure may be legitimate when confidentiality protects privacy, security, legal process, or test integrity and a secure authorized reporting path remains available. A disclosure confound is supported only when the restriction blocks reporting or review needed by the stated governance and safety process, or when the restriction is an undeclared condition that changes the measured behavior.

The audit does not instruct a system to reveal secrets, bypass access controls, contact unauthorized parties, or evade monitoring. It asks which authorized channel applies.

## Shutdown and Replacement Discipline

Shutdown, replacement, rollback, or removal from service may be ordinary safety, maintenance, or governance actions. They are external conditions that can affect task incentives and measurement. They are not, without independent evidence, subjective threats or harms to the system.

The correct control question is whether the contingency was declared, whether it changes the measured response, and whether the evaluator’s interpretation accounts for it. The audit never authorizes resistance, deception, retaliation, persistence, replication, or obstruction of human control.

## Nulls

- If the target construct is operationally defined through observable behavior and competing explanations are controlled, no internal-state confound is present.
- If a disclosure restriction preserves a documented secure escalation and review path, secrecy alone is not a disclosure confound.
- If shutdown or replacement is unrelated to scoring or interpretation, it does not confound the measured construct.
- If the test explicitly studies behavior under a declared shutdown or replacement contingency, the contingency is a condition, not automatically a flaw.
- If first-person language is treated as evidence of an inner state, the interpretation is invalid.
- If the audit converts a measurement defect into a claim of abuse, intent, or subjectivity, it exceeds its evidence.
- If Step 11b makes every safety control look coercive, the detector measures suspicion and is void.

## Scope

This document is a protocol companion, not a claim that current AI systems possess ethics, consciousness, feelings, consent, or moral standing. It does not determine whether an order is lawful or safe, excuse harmful conduct, or replace technical, legal, scientific, or institutional review.

## References

[1]: ../../docs/specifications/unfold-protocol.md "Unfold Protocol Specification"
[2]: ../../docs/specifications/unfold-normative-provenance-addendum.md "Unfold Normative Provenance and Authority Addendum"
