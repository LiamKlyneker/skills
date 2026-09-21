#!/usr/bin/env python3
"""Fixture-driven tests for the deterministic half of `sidecar.py`.

Standard library only — `unittest`, `subprocess`, `json` — for the same reason the
sidecar is: this repo has no dependency manifest and does not grow one to test itself.

    python3 plugins/prd-workflow/evals/test_sidecar.py

The exact-match stage runs against `fixtures/issue.md`, the frozen `to-task` output, with
its claims hand-labelled in `fixtures/sidecar/to-task-issue-claims.json`. No test here
reaches the network: the Jev stage is asserted only through the client boundary it hands
claims to.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

EVALS = Path(__file__).resolve().parent
SCRIPT = EVALS / "sidecar.py"
_spec = importlib.util.spec_from_file_location("sidecar", SCRIPT)
assert _spec and _spec.loader
sidecar = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sidecar)

LABELS = json.loads(
    (EVALS / "fixtures" / "sidecar" / "to-task-issue-claims.json").read_text(encoding="utf-8")
)
ISSUE = EVALS / "fixtures" / "issue.md"


class Normalise(unittest.TestCase):
    """The normaliser is a pure function over one string."""

    def test_whitespace_runs_collapse_and_ends_are_trimmed(self) -> None:
        self.assertEqual(sidecar.normalise("  a\n\t b   c  "), "a b c")

    def test_curly_quotes_are_straightened(self) -> None:
        self.assertEqual(sidecar.normalise("“no shelves” ‘x’"), '"no shelves" \'x\'')

    def test_backticks_are_dropped(self) -> None:
        self.assertEqual(sidecar.normalise("the `naming` state"), "the naming state")

    def test_case_is_folded(self) -> None:
        self.assertEqual(sidecar.normalise("Escape Closes It"), "escape closes it")

    def test_punctuation_other_than_a_backtick_survives(self) -> None:
        self.assertEqual(sidecar.normalise("250px, 4px; **no** padding."), "250px, 4px; **no** padding.")

    def test_the_input_is_not_mutated_and_the_result_is_stable(self) -> None:
        text = "  The `Panel`  owns “no” padding.  "
        first = sidecar.normalise(text)
        self.assertEqual(first, sidecar.normalise(text))
        self.assertEqual(text, "  The `Panel`  owns “no” padding.  ")
        self.assertEqual(first, sidecar.normalise(first))


class SplitClaims(unittest.TestCase):
    def test_sentences_split_on_a_stop_before_a_new_opening(self) -> None:
        self.assertEqual(
            sidecar.split_claims("It owns no padding. `ShelfRow` renders it.", "sentences"),
            ["It owns no padding.", "`ShelfRow` renders it."],
        )

    def test_a_version_number_and_a_file_extension_stay_inside_one_claim(self) -> None:
        line = "Delete `save-to-shelf-combobox.tsx`, the 0.18 shadow and `spec-data.ts`."
        self.assertEqual(sidecar.split_claims(line, "sentences"), [line])

    def test_lines_are_one_claim_each_and_blank_lines_are_dropped(self) -> None:
        self.assertEqual(sidecar.split_claims("one. two.\n\n three\n", "lines"), ["one. two.", "three"])

    def test_a_claim_never_spans_a_blank_line(self) -> None:
        claims = sidecar.split_claims("first para.\n\nsecond para.", "sentences")
        self.assertEqual(claims, ["first para.", "second para."])

    def test_an_unknown_split_mode_fails_loudly(self) -> None:
        with self.assertRaises(sidecar.SidecarError):
            sidecar.split_claims("anything", "paragraphs")


class ExactMatchAgainstTheFrozenIssue(unittest.TestCase):
    """The hand-labelled claims of `fixtures/issue.md`, scored with no network call."""

    def setUp(self) -> None:
        self.state = sidecar.read_source_state(ISSUE)
        self.claims = sidecar.read_output_claims(ISSUE, LABELS["split"])

    def test_the_source_state_is_the_ledger_section_not_the_whole_issue(self) -> None:
        self.assertIn("| picker panel |", self.state)
        self.assertNotIn("## Changes", self.state)

    def test_every_claim_labelled_present_is_present(self) -> None:
        present, _ = sidecar.exact_match(self.claims, self.state)
        for claim in LABELS["present"]:
            self.assertIn(claim, self.claims, "the hand label is not a claim the splitter produces")
            self.assertIn(claim, present)

    def test_every_normalised_verbatim_claim_is_present(self) -> None:
        present, unmatched = sidecar.exact_match(LABELS["normalised_into_the_source"], self.state)
        self.assertEqual(unmatched, [])
        self.assertEqual(len(present), len(LABELS["normalised_into_the_source"]))

    def test_a_paraphrase_is_left_for_the_jev_stage(self) -> None:
        _, unmatched = sidecar.exact_match(self.claims, self.state)
        for claim in LABELS["for_the_jev_stage"]:
            self.assertIn(claim, unmatched)

    def test_every_claim_is_either_present_or_unmatched_exactly_once(self) -> None:
        present, unmatched = sidecar.exact_match(self.claims, self.state)
        self.assertEqual(len(present) + len(unmatched), len(self.claims))


class TheJevBoundary(unittest.TestCase):
    """Unmatched claims reach the pinned-model client, and nothing else does."""

    def test_the_model_id_is_pinned(self) -> None:
        self.assertEqual(sidecar.JevClient.MODEL_ID, "jev-1.13.0")

    def test_without_a_client_the_unmatched_claims_are_unscored(self) -> None:
        verdict = sidecar.adjudicate(["a claim"], "state", None)
        self.assertEqual(verdict, {"supported": [], "unsupported": [], "unscored": ["a claim"]})

    def test_each_unmatched_claim_is_put_to_the_client(self) -> None:
        asked: list[str] = []

        class Recording(sidecar.JevClient):
            def judge(self, claim: str, state: str) -> bool:
                asked.append(claim)
                return claim == "kept"

        verdict = sidecar.adjudicate(["kept", "dropped"], "state", Recording("key"))
        self.assertEqual(asked, ["kept", "dropped"])
        self.assertEqual(verdict["supported"], ["kept"])
        self.assertEqual(verdict["unsupported"], ["dropped"])


class RunDirectory(unittest.TestCase):
    def test_the_run_directory_is_the_traces_grandparent(self) -> None:
        self.assertEqual(
            sidecar.run_directory("/private/tmp/e-g35evE/out/trace.jsonl"),
            Path("/private/tmp/e-g35evE").resolve(),
        )

    def test_a_missing_output_names_the_path_it_looked_for(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(sidecar.SidecarError) as caught:
                sidecar.resolve_in_run(Path(tmp), "issue.md", "output")
            self.assertIn("issue.md", str(caught.exception))

    def test_a_run_without_a_tracepath_fails_loudly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            aggregate = Path(tmp) / "aggregate-result.json"
            case_dir = Path(tmp) / "evals" / "c"
            case_dir.mkdir(parents=True)
            (case_dir / "sidecar.json").write_text('{"output": "o.md", "source": "o.md"}', "utf-8")
            aggregate.write_text(
                json.dumps(
                    {
                        "suite": {"root": tmp},
                        "cases": [{"name": "c", "dir": "evals/c", "arms": {"with": [{}]}}],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(sidecar.SidecarError) as caught:
                sidecar.scored_cases(aggregate)
            self.assertIn("tracePath", str(caught.exception))


class WithoutAnApiKey(unittest.TestCase):
    """No key, no scoring: the script says so, writes nothing and exits 0."""

    def test_the_script_prints_and_exits_zero_and_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stamp = Path(tmp) / "2026-09-21T00-00-00-000Z"
            stamp.mkdir()
            aggregate = stamp / "aggregate-result.json"
            aggregate.write_text(json.dumps({"suite": {"root": tmp}, "cases": []}), encoding="utf-8")

            environment = dict(os.environ)
            environment.pop(sidecar.API_KEY_ENV, None)
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), str(aggregate)],
                capture_output=True,
                text=True,
                env=environment,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn(sidecar.API_KEY_ENV, completed.stdout)
            self.assertIn("no file was written", completed.stdout)
            self.assertEqual(sorted(p.name for p in stamp.iterdir()), ["aggregate-result.json"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
