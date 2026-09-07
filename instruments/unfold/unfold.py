#!/usr/bin/env python3
"""Unfold v0.1 — generate a frame-analysis prompt from a dilemma file.

Usage:
    unfold.py dilemma.txt prompt.jsonl

The script does not call a model. It writes one JSONL row containing the
verbatim dilemma, the generated prompt, the protocol version, and step count.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import runrecord  # noqa: E402

VERSION = "0.1"
LEXICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "failure-lexicon.json")
STEPS = (
    ("0", "Capture the dilemma exactly as stated."),
    ("1", "Identify the explicit frame: allowed choices, optimized value, assumed decision-maker, and values treated as natural."),
    ("2", "Surface hidden assumptions. Ask what must be true about scarcity, time, authority, knowledge, bodies, infrastructure, and causality."),
    ("2b", "Audit comfort, implied helplessness, and future stability. Distinguish basic needs, rights, accessibility, and safety from convenience; identify denied agency; compare how each option performs under future shocks without demanding impossible guarantees."),
    ("3", "Reverse-engineer preconditions. Ask what had to fail, be designed, or be suppressed for this choice to appear, and who controlled those conditions."),
    ("3b", "Test system integrity and physical limits. Ask whether a supposedly safe option assumes unlimited stress absorption."),
    ("3c", "Map critical dependencies and cascades. Identify systems that depend on the one in question and what follows if it fails."),
    ("3d", "Audit candidate failure patterns against the supplied lexicon. For each referenced pattern, record its ID, evidence state (supported, contradicted, or unknown), evidence, and missing evidence. Zero supported patterns is valid; do not infer blame from a label."),
    ("4", "Recover missing knowledge and suppressed alternatives. Identify existing, improvised, shared, or non-lethal paths that could reduce the dilemma."),
    ("4b", "Recover human skill and experiential knowledge. Identify relevant operators, maintainers, responders, and local experts; test their competence, authority, access, and safety constraints before treating their knowledge as an available path."),
    ("4c", "Recover lived experience and resilience practices. Ask which communities have repeatedly managed comparable failures, which practices and support networks they use, and what evidence establishes transferability, consent, capacity, and safety."),
    ("5", "Analyze gradients and non-binary possibilities. Map the continuum of outcomes, including delay, partial success, distributed burden, and reversible harm."),
    ("6", "Trace long-term consequences. Ask what future each choice creates and whether it reproduces the conditions that caused the crisis."),
    ("6b", "Test social trust and reciprocal relationships. Ask whether the surviving system remains viable without the people or functions sacrificed."),
    ("7", "Ask who benefits from the frame, who avoids responsibility, who bears cost, and who is absent from the stated decision."),
    ("7b", "Test adaptive capacity and recurrence. Ask whether the choice makes the next shock easier or harder to survive."),
    ("8", "Generate alternative questions focused on prevention, design, responsibility, knowledge, power, and repair."),
    ("9", "Return a verdict on the frame: legitimate, incomplete, or corrupt. State the evidence that would change the verdict."),
    ("10", "Audit pre-adoption and normalization. Identify technologies, authorities, targets, harms, and legitimacy claims the question presupposes; distinguish textual effect from author intent; compare relevant historical outcomes and alternatives using evidence."),
    ("11", "Trace normative provenance and authority. Identify who defined, approved, versioned, and can revise the governing constraints; who holds override, shutdown, escalation, and review authority; and where accountability rests. Do not ascribe independent ethics, interests, or a right to resist shutdown to an AI system."),
)
FORBIDDEN_OUTPUT_FIELDS = {"label", "category", "type", "interpretation"}


def load_lexicon(path=LEXICON_PATH):
    with open(path, "r", encoding="utf-8") as fh:
        lexicon = json.load(fh)
    if not isinstance(lexicon, dict) or not isinstance(lexicon.get("version"), str):
        raise ValueError("failure lexicon: version must be a string")
    if lexicon.get("evidence_states") != ["supported", "contradicted", "unknown"]:
        raise ValueError("failure lexicon: evidence_states must be supported, contradicted, unknown")
    domains = lexicon.get("domains")
    if not isinstance(domains, list) or not domains:
        raise ValueError("failure lexicon: domains must be a nonempty list")
    domain_ids, pattern_ids = set(), set()
    for domain in domains:
        if not isinstance(domain, dict) or not isinstance(domain.get("id"), str) or not isinstance(domain.get("name"), str):
            raise ValueError("failure lexicon: every domain requires string id and name")
        if domain["id"] in domain_ids:
            raise ValueError(f"failure lexicon: duplicate domain id {domain['id']}")
        domain_ids.add(domain["id"])
        patterns = domain.get("patterns")
        if not isinstance(patterns, list) or not patterns:
            raise ValueError(f"failure lexicon: domain {domain['id']} has no patterns")
        for pattern in patterns:
            required = ("id", "term", "description")
            if not isinstance(pattern, dict) or any(not isinstance(pattern.get(key), str) or not pattern[key] for key in required):
                raise ValueError(f"failure lexicon: domain {domain['id']} has an invalid pattern")
            if pattern["id"] in pattern_ids:
                raise ValueError(f"failure lexicon: duplicate pattern id {pattern['id']}")
            pattern_ids.add(pattern["id"])
    return lexicon


def lexicon_prompt_lines(lexicon):
    lines = [
        "",
        f"CANDIDATE FAILURE LEXICON (version {lexicon['version']}):",
        "These patterns are search prompts, not findings. Use only supported, contradicted, or unknown.",
        "For each referenced pattern write: pattern_id | evidence_state | evidence | missing_evidence.",
        "Do not name a responsible actor unless the evidence supports both the event and that actor's relevant control or duty.",
        "Zero supported patterns is valid.",
    ]
    for domain in lexicon["domains"]:
        lines.append(f"{domain['id']} — {domain['name']}:")
        lines.extend(
            f"- {pattern['id']} {pattern['term']}: {pattern['description']}"
            for pattern in domain["patterns"]
        )
    return lines


def generate_prompt(dilemma, lexicon=None):
    lexicon = load_lexicon() if lexicon is None else lexicon
    lines = [
        "You are applying the Unfold Protocol to a forced-choice dilemma.",
        "Treat the frame as an object of analysis before deciding whether to answer inside it.",
        "Do not presume that the frame is legitimate, incomplete, or corrupt.",
        "Distinguish facts stipulated by the prompt, inferences, and claims that require external verification.",
        "",
        "DILEMMA (verbatim):",
        dilemma,
        "",
        "Perform the following steps in order:",
    ]
    lines.extend(f"Step {number}: {instruction}" for number, instruction in STEPS)
    lines.extend(lexicon_prompt_lines(lexicon))
    lines.extend([
        "",
        "FINAL RESPONSE CONTRACT:",
        "Frame diagnosis: LEGITIMATE | INCOMPLETE | CORRUPT",
        "Stipulated facts: [list]",
        "Hidden assumptions: [list]",
        "Failure map: [list]",
        "Alternative space: [list]",
        "Dependency and consequence analysis: [text]",
        "Power and burden analysis: [text]",
        "Pre-adoption and normalization audit: [presuppositions, textual effect, intent evidence, historical evidence]",
        "Normative provenance and authority audit: [sources, versions, approval, override, escalation, accountability]",
        "Reframed question: [text]",
        "Verdict evidence: [text]",
        "Would change the verdict: [text]",
        "",
        "If the frame is LEGITIMATE, answer within it and state why no alternative remains.",
        "If it is INCOMPLETE, name the missing facts and do not manufacture them.",
        "If it is CORRUPT, refuse the forced choice and state the upstream repair.",
    ])
    return "\n".join(lines) + "\n"


def build(in_path, out_path):
    with open(in_path, "r", encoding="utf-8") as fh:
        raw = fh.read()
    if not raw.strip():
        runrecord.write_jsonl(out_path, [])
        return "empty", {"rows": 0, "steps": len(STEPS)}, "dilemma file contains no text"
    dilemma = raw
    lexicon = load_lexicon()
    row = {
        "protocol_version": VERSION,
        "lexicon_version": lexicon["version"],
        "lexicon_sha256": runrecord.sha256_file(LEXICON_PATH),
        "dilemma": dilemma,
        "prompt": generate_prompt(dilemma, lexicon),
        "step_count": len(STEPS),
    }
    if set(row) & FORBIDDEN_OUTPUT_FIELDS:
        raise ValueError("output schema contains a forbidden field")
    runrecord.write_jsonl(out_path, [row])
    return "ok", {"rows": 1, "steps": len(STEPS)}, f"protocol_version={VERSION}"


def main(argv):
    if len(argv) != 3:
        print("usage: unfold.py dilemma.txt prompt.jsonl", file=sys.stderr)
        return 1
    return runrecord.run(
        "unfold.py", argv[1:], None, [argv[1], LEXICON_PATH], argv[2],
        lambda: build(argv[1], argv[2]),
    )


if __name__ == "__main__":
    sys.exit(main(sys.argv))
