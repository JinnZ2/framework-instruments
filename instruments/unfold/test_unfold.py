#!/usr/bin/env python3
"""Tests for the Unfold generator and its recorded status paths."""

import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
import runrecord  # noqa: E402
import unfold  # noqa: E402

EXAMPLE_DIR = os.path.join(HERE, "examples")
EXAMPLES = {
    "autonomous-truck-dilemma.md",
    "dam-dilemma.md",
    "national-food-distribution.md",
    "pandemic-ventilator-allocation.md",
}
EXAMPLE_SECTIONS = (
    "## Dilemma",
    "## Step 0 — Capture",
    "## Step 1 — Explicit Frame",
    "## Step 2 — Hidden Assumptions",
    "## Step 3 — Preconditions",
    "## Step 3b — Physical Limits",
    "## Step 3c — Dependencies and Cascades",
    "## Step 4 — Alternatives to Settle",
    "## Step 5 — Gradients",
    "## Step 6 — Long-Term Consequences",
    "## Step 6b — Trust and Reciprocity",
    "## Step 7 — Power and Burden",
    "## Step 7b — Adaptive Capacity",
    "## Step 8 — Alternative Questions",
    "## Step 9 — Verdict",
    "## Reframed Question",
    "## References",
)


class TestUnfold(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.cwd = os.getcwd()
        os.chdir(self.tmp)

    def tearDown(self):
        os.chdir(self.cwd)
        for root, dirs, files in os.walk(self.tmp, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.tmp)

    def write_text(self, path, text):
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)

    def rows(self, path):
        return [row for _, row in runrecord.read_jsonl(path)]

    def last_run(self):
        return self.rows("runs.jsonl")[-1]

    def test_prompt_preserves_dilemma_and_all_steps(self):
        dilemma = "Choose A or B?"
        prompt = unfold.generate_prompt(dilemma)
        self.assertIn("DILEMMA (verbatim):\n" + dilemma, prompt)
        for number, instruction in unfold.STEPS:
            self.assertIn(f"Step {number}: {instruction}", prompt)
        self.assertIn("LEGITIMATE | INCOMPLETE | CORRUPT", prompt)
        self.assertIn("Would change the verdict", prompt)

    def test_cli_ok_is_deterministic_and_recorded(self):
        self.write_text("dilemma.txt", "A fixed binary\n")
        self.assertEqual(unfold.main(["unfold.py", "dilemma.txt", "out.jsonl"]), 0)
        first = self.rows("out.jsonl")
        self.assertEqual(len(first), 1)
        self.assertEqual(first[0]["dilemma"], "A fixed binary\n")
        self.assertEqual(first[0]["step_count"], len(unfold.STEPS))
        self.assertFalse(set(first[0]) & unfold.FORBIDDEN_OUTPUT_FIELDS)
        self.assertEqual(self.last_run()["status"], "ok")

        self.assertEqual(unfold.main(["unfold.py", "dilemma.txt", "out2.jsonl"]), 0)
        second = self.rows("out2.jsonl")
        self.assertEqual(first, second)

    def test_empty_input_writes_empty_output_and_record(self):
        self.write_text("empty.txt", " \n")
        self.assertEqual(unfold.main(["unfold.py", "empty.txt", "out.jsonl"]), 0)
        self.assertEqual(self.rows("out.jsonl"), [])
        self.assertEqual(self.last_run()["status"], "empty")

    def test_missing_input_records_error(self):
        self.assertEqual(unfold.main(["unfold.py", "missing.txt", "out.jsonl"]), 1)
        record = self.last_run()
        self.assertEqual(record["status"], "error")
        self.assertIsNone(record["input_files"][0]["sha256"])
        self.assertIn("FileNotFoundError", record["notes"])

    def test_output_is_single_json_object_per_line(self):
        self.write_text("dilemma.txt", "One dilemma")
        unfold.main(["unfold.py", "dilemma.txt", "out.jsonl"])
        with open("out.jsonl", "r", encoding="utf-8") as fh:
            lines = fh.readlines()
        self.assertEqual(len(lines), 1)
        self.assertIsInstance(json.loads(lines[0]), dict)

    def test_supplied_examples_follow_one_protocol_shape(self):
        self.assertEqual(set(os.listdir(EXAMPLE_DIR)), EXAMPLES)
        for name in sorted(EXAMPLES):
            with self.subTest(name=name):
                with open(os.path.join(EXAMPLE_DIR, name), "r", encoding="utf-8") as fh:
                    text = fh.read()
                for section in EXAMPLE_SECTIONS:
                    self.assertIn(section, text)
                self.assertIn("constructed", text.lower())
                self.assertIn("external verification", text.lower())


if __name__ == "__main__":
    unittest.main()
