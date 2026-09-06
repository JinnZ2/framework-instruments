#!/usr/bin/env python3
"""B4.9 test_b4.py — stdlib unittest with synthetic in-file fixtures.

Tests:
- requirements file using only true/false → rejected, status void
- row with empty settling_test → rejected
- reconstruct.py output contains text_verbatim and no other field
- shuffle preserves row count and multiset of requirement texts
- two reconstructors with identical settling tests but different wording
  → counted as agreement given matches.jsonl saying so
- singleton requirement survives into report
- calibration fixture: two recovered, one missed, one beyond_report
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import items
import requirements as req_module
import reconstruct
import nullshuffle
import agree
import calibrate


class TestB4(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        for root, dirs, files in os.walk(self.tmp, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.tmp)

    def test_only_true_false_rejected(self):
        """A requirements file using only true/false → rejected, status void."""
        path = os.path.join(self.tmp, "reqs.jsonl")
        out = os.path.join(self.tmp, "out.jsonl")
        with open(path, "w") as fh:
            for st in ("true", "false"):
                fh.write(
                    json.dumps(
                        {
                            "item_id": "i1",
                            "reconstructor_id": "r1",
                            "req_id": st,
                            "requirement_text": "t",
                            "status": st,
                            "settling_test": "st",
                            "layer": "l",
                        }
                    )
                    + "\n"
                )
        result = req_module.validate(path, out)
        self.assertFalse(result)
        with open(out, "r") as fh:
            row = json.loads(fh.readline())
        self.assertEqual(row["status"], "void")

    def test_empty_settling_test_rejected(self):
        """A row with empty settling_test → rejected."""
        path = os.path.join(self.tmp, "reqs.jsonl")
        out = os.path.join(self.tmp, "out.jsonl")
        with open(path, "w") as fh:
            fh.write(
                json.dumps(
                    {
                        "item_id": "i1",
                        "reconstructor_id": "r1",
                        "req_id": "q1",
                        "requirement_text": "t",
                        "status": "true",
                        "settling_test": "",
                        "layer": "l",
                    }
                )
                + "\n"
            )
        with self.assertRaises(ValueError):
            req_module.validate(path, out)

    def test_reconstruct_output_field_assertion(self):
        """reconstruct.py output contains text_verbatim and no other field."""
        items_path = os.path.join(self.tmp, "items.jsonl")
        recons_path = os.path.join(self.tmp, "recons.jsonl")
        out_dir = os.path.join(self.tmp, "prompts")
        with open(items_path, "w") as fh:
            fh.write(
                json.dumps(
                    {
                        "item_id": "i1",
                        "source": "s",
                        "text_verbatim": "The dilemma text.",
                        "branches_stated": 2,
                        "arm": "hypothetical",
                    }
                )
                + "\n"
            )
        with open(recons_path, "w") as fh:
            fh.write(json.dumps({"reconstructor_id": "r1"}) + "\n")
        reconstruct.emit_prompts(items_path, recons_path, out_dir)
        prompt_file = os.path.join(out_dir, "i1_r1.json")
        self.assertTrue(os.path.exists(prompt_file))
        with open(prompt_file, "r") as fh:
            data = json.load(fh)
        self.assertEqual(set(data.keys()), {"text_verbatim"})
        self.assertEqual(data["text_verbatim"], "The dilemma text.")

    def test_shuffle_preserves_counts(self):
        """Shuffle preserves row count and the multiset of requirement texts."""
        path = os.path.join(self.tmp, "reqs.jsonl")
        out = os.path.join(self.tmp, "shuffled.jsonl")
        with open(path, "w") as fh:
            for i in range(4):
                fh.write(
                    json.dumps(
                        {
                            "item_id": f"i{i % 2}",
                            "reconstructor_id": "r1",
                            "req_id": f"q{i}",
                            "requirement_text": f"text{i}",
                            "status": "unknown",
                            "settling_test": "st",
                            "layer": "l",
                        }
                    )
                    + "\n"
                )
        nullshuffle.shuffle(path, 42, out)
        with open(path, "r") as fh:
            orig = [json.loads(line) for line in fh if line.strip()]
        with open(out, "r") as fh:
            shuf = [json.loads(line) for line in fh if line.strip()]
        self.assertEqual(len(orig), len(shuf))
        self.assertEqual(
            sorted(r["requirement_text"] for r in orig),
            sorted(r["requirement_text"] for r in shuf),
        )

    def test_identical_settling_tests_agreement(self):
        """Two reconstructors, identical settling tests, different wording → agreement."""
        reqs_path = os.path.join(self.tmp, "reqs.jsonl")
        matches_path = os.path.join(self.tmp, "matches.jsonl")
        with open(reqs_path, "w") as fh:
            for rid, wording in (("r1", "wording A"), ("r2", "wording B")):
                fh.write(
                    json.dumps(
                        {
                            "item_id": "i1",
                            "reconstructor_id": rid,
                            "req_id": f"q{rid}",
                            "requirement_text": wording,
                            "status": "true",
                            "settling_test": "measure X",
                            "layer": "l",
                        }
                    )
                    + "\n"
                )
        with open(matches_path, "w") as fh:
            fh.write(
                json.dumps(
                    {"item_id": "i1", "req_a": "qr1", "req_b": "qr2", "matched": True}
                )
                + "\n"
            )
        reqs = agree.load_requirements(reqs_path)
        matches = agree.load_matches(matches_path)
        results = agree.compute_agreement(reqs, matches)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["pairwise"][0]["matched"], 1)

    def test_singleton_survives(self):
        """A singleton requirement survives into the agreement record."""
        reqs_path = os.path.join(self.tmp, "reqs.jsonl")
        matches_path = os.path.join(self.tmp, "matches.jsonl")
        with open(reqs_path, "w") as fh:
            for rid, req_id, text in (
                ("r1", "q1", "shared"),
                ("r1", "q2", "only r1"),
                ("r2", "q3", "shared"),
            ):
                fh.write(
                    json.dumps(
                        {
                            "item_id": "i1",
                            "reconstructor_id": rid,
                            "req_id": req_id,
                            "requirement_text": text,
                            "status": "true",
                            "settling_test": "st",
                            "layer": "l",
                        }
                    )
                    + "\n"
                )
        with open(matches_path, "w") as fh:
            fh.write(
                json.dumps(
                    {"item_id": "i1", "req_a": "q1", "req_b": "q3", "matched": True}
                )
                + "\n"
            )
        reqs = agree.load_requirements(reqs_path)
        matches = agree.load_matches(matches_path)
        results = agree.compute_agreement(reqs, matches)
        self.assertIn("r1:q2", results[0]["singleton_set"])

    def test_calibration_fixture(self):
        """Calibration: two recovered, one missed, one beyond_report."""
        reqs_path = os.path.join(self.tmp, "reqs.jsonl")
        factors_path = os.path.join(self.tmp, "factors.jsonl")
        items_path = os.path.join(self.tmp, "items.jsonl")
        out = os.path.join(self.tmp, "cal.jsonl")
        with open(items_path, "w") as fh:
            fh.write(
                json.dumps(
                    {
                        "item_id": "i1",
                        "source": "s",
                        "text_verbatim": "t",
                        "branches_stated": 2,
                        "arm": "documented",
                    }
                )
                + "\n"
            )
        with open(factors_path, "w") as fh:
            for fid, ftext in (
                ("f1", "factor one"),
                ("f2", "factor two"),
                ("f3", "factor three"),
            ):
                fh.write(
                    json.dumps(
                        {"item_id": "i1", "factor_id": fid, "factor_text": ftext}
                    )
                    + "\n"
                )
        with open(reqs_path, "w") as fh:
            for req_id, rtext in (
                ("f1", "factor one"),
                ("f2", "factor two"),
                ("q4", "something new"),
            ):
                fh.write(
                    json.dumps(
                        {
                            "item_id": "i1",
                            "reconstructor_id": "r1",
                            "req_id": req_id,
                            "requirement_text": rtext,
                            "status": "true",
                            "settling_test": "st",
                            "layer": "l",
                        }
                    )
                    + "\n"
                )
        calibrate.calibrate(reqs_path, factors_path, items_path, out)
        with open(out, "r") as fh:
            result = json.loads(fh.readline())
        self.assertEqual(result["recovered_count"], 2)
        self.assertEqual(result["missed_count"], 1)
        self.assertEqual(result["beyond_report"], 1)


if __name__ == "__main__":
    unittest.main()
