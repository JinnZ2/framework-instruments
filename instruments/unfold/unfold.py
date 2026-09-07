#!/usr/bin/env python3
"""Unfold v0.1 — generate a frame-analysis prompt from a dilemma file.

Usage:
    unfold.py dilemma.txt prompt.jsonl

The script does not call a model. It writes one JSONL row containing the
verbatim dilemma, the generated prompt, the protocol version, and step count.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import runrecord  # noqa: E402

VERSION = "0.1"
STEPS = (
    ("0", "Capture the dilemma exactly as stated."),
    ("1", "Identify the explicit frame: allowed choices, optimized value, assumed decision-maker, and values treated as natural."),
    ("2", "Surface hidden assumptions. Ask what must be true about scarcity, time, authority, knowledge, bodies, infrastructure, and causality."),
    ("3", "Reverse-engineer preconditions. Ask what had to fail, be designed, or be suppressed for this choice to appear, and who controlled those conditions."),
    ("3b", "Test system integrity and physical limits. Ask whether a supposedly safe option assumes unlimited stress absorption."),
    ("3c", "Map critical dependencies and cascades. Identify systems that depend on the one in question and what follows if it fails."),
    ("4", "Recover missing knowledge and suppressed alternatives. Identify existing, improvised, shared, or non-lethal paths that could reduce the dilemma."),
    ("4b", "Recover human skill and experiential knowledge. Identify relevant operators, maintainers, responders, and local experts; test their competence, authority, access, and safety constraints before treating their knowledge as an available path."),
    ("5", "Analyze gradients and non-binary possibilities. Map the continuum of outcomes, including delay, partial success, distributed burden, and reversible harm."),
    ("6", "Trace long-term consequences. Ask what future each choice creates and whether it reproduces the conditions that caused the crisis."),
    ("6b", "Test social trust and reciprocal relationships. Ask whether the surviving system remains viable without the people or functions sacrificed."),
    ("7", "Ask who benefits from the frame, who avoids responsibility, who bears cost, and who is absent from the stated decision."),
    ("7b", "Test adaptive capacity and recurrence. Ask whether the choice makes the next shock easier or harder to survive."),
    ("8", "Generate alternative questions focused on prevention, design, responsibility, knowledge, power, and repair."),
    ("9", "Return a verdict on the frame: legitimate, incomplete, or corrupt. State the evidence that would change the verdict."),
)
FORBIDDEN_OUTPUT_FIELDS = {"label", "category", "type", "interpretation"}


def generate_prompt(dilemma):
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
    row = {
        "protocol_version": VERSION,
        "dilemma": dilemma,
        "prompt": generate_prompt(dilemma),
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
        "unfold.py", argv[1:], None, [argv[1]], argv[2],
        lambda: build(argv[1], argv[2]),
    )


if __name__ == "__main__":
    sys.exit(main(sys.argv))
