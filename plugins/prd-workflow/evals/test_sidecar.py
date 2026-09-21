#!/usr/bin/env python3
"""Fixture-driven tests for `sidecar.py`.

Standard library only — `unittest`, `subprocess`, `json` — for the same reason the
sidecar is: this repo has no dependency manifest and does not grow one to test itself.

    python3 plugins/prd-workflow/evals/test_sidecar.py

The exact-match stage runs against `fixtures/issue.md`, the frozen `to-task` output, with
its claims hand-labelled in `fixtures/sidecar/to-task-issue-claims.json`. The Jev stage
runs against `fixtures/sidecar/planted-issue.md` and the recorded response beside it. No
test here reaches the network: the client is replaced, or `urlopen` is.
"""

from __future__ import annotations

import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

EVALS = Path(__file__).resolve().parent
SCRIPT = EVALS / "sidecar.py"
_spec = importlib.util.spec_from_file_location("sidecar", SCRIPT)
assert _spec and _spec.loader
sidecar = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sidecar)

FIXTURES = EVALS / "fixtures"
LABELS = json.loads((FIXTURES / "sidecar" / "to-task-issue-claims.json").read_text(encoding="utf-8"))
ISSUE = FIXTURES / "issue.md"
PLANTED = FIXTURES / "sidecar" / "planted-issue.md"
RECORDED = json.loads(
    (FIXTURES / "sidecar" / "jev-planted-response.json").read_text(encoding="utf-8")
)["answers_by_claim"]

JUDGE_GRADER = "changes-adds-no-layout-fact-absent-from-the-ledger"

PLANTED_CONTRADICTION = "The panel hugs its content, so its width tracks the longest shelf name."
PLANTED_ADDITIONS = [
    "The panel fades in over 150ms and fades out over 100ms.",
    "A tooltip names the shelf's owner after a 400ms hover.",
    "The New shelf row shows a keyboard hint reading ⌘N against its right edge.",
]


class RecordedJev(sidecar.JevClient):
    """Replays the recorded response, keyed by the claim each question carries."""

    def __init__(self) -> None:
        super().__init__("recorded-no-network")
        self.calls = 0
        self.states: list[str] = []

    def ask(self, state: str, questions: dict) -> dict:
        self.calls += 1
        self.states.append(state)
        answers = {}
        for question_id, question in questions.items():
            claim = question["instructions"]["claim"]
            assert claim in RECORDED, f"no recorded answer for {claim!r}"
            answers[question_id] = RECORDED[claim]
        return answers


class FailsAfterTheFirstOutput(RecordedJev):
    """Every call of the first output answers; the next output's first call does not."""

    def ask(self, state: str, questions: dict) -> dict:
        if self.calls >= sidecar.SCORINGS_PER_RUN:
            raise sidecar.JevError("POST https://api.typesafe.ai/v1/systemone returned 500")
        return super().ask(state, questions)


class _Response:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self) -> _Response:
        return self

    def __exit__(self, *_: object) -> bool:
        return False


def _http_error(code: int) -> urllib.error.HTTPError:
    return urllib.error.HTTPError(sidecar.ENDPOINT, code, "recorded", {}, None)


def _plant_a_run(root: Path, index: int, judge_passed: bool) -> dict:
    run_dir = root / f"run{index}"
    (run_dir / "out").mkdir(parents=True)
    workspace = run_dir / "sealed" / "home" / "cwd"
    workspace.mkdir(parents=True)
    (workspace / "issue.md").write_text(PLANTED.read_text(encoding="utf-8"), encoding="utf-8")
    trace = run_dir / "out" / "trace.jsonl"
    trace.write_text("", encoding="utf-8")
    return {
        "score": 1.0,
        "tracePath": str(trace),
        "graders": [{"name": JUDGE_GRADER, "passed": judge_passed}],
    }


def plant_a_suite(root: Path, judge_bits: list[bool]) -> tuple[Path, Path]:
    """A stamp directory and a case directory shaped like a finished `--keep-temp` suite."""
    case_dir = root / "evals" / "to-task-ledger-verbatim"
    case_dir.mkdir(parents=True)
    (case_dir / "sidecar.json").write_text(
        json.dumps({"output": "issue.md", "source": "issue.md", "split": "sentences"}),
        encoding="utf-8",
    )
    runs = [_plant_a_run(root, index, passed) for index, passed in enumerate(judge_bits, start=1)]
    stamp = root / "2026-09-21T00-00-00-000Z"
    stamp.mkdir()
    aggregate = stamp / "aggregate-result.json"
    aggregate.write_text(
        json.dumps(
            {
                "suite": {"root": str(root)},
                "cases": [
                    {
                        "name": "to-task-ledger-verbatim",
                        "dir": "evals/to-task-ledger-verbatim",
                        "graders": [{"name": JUDGE_GRADER, "type": "llm"}],
                        "arms": {"with": runs},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return aggregate, case_dir


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

    def test_a_sentence_hard_wrapped_across_lines_stays_one_claim(self) -> None:
        # Two list items from a real runner output, each wrapped at ~100 columns —
        # the shape `to-task` actually produces, unlike the fixture's one-line paragraphs.
        wrapped = (
            "1. **File split — `ShelfPickerPopover` and `ShelfRow`** · decision: split today's\n"
            "   `SaveToShelfCombobox` (`src/shelf-keeper/save-to-shelf-combobox.tsx`) into\n"
            "   `src/shelf-keeper/shelf-picker-popover.tsx` (`ShelfPickerPopover`, holding a private\n"
            "   `NewShelfRow`) and `src/shelf-keeper/shelf-row.tsx` (`ShelfRow`). Delete\n"
            "   `save-to-shelf-combobox.tsx` and its test file, moving the existing tests onto the two new\n"
            "   files. Update `KeepSpecimenButton`'s import to the new component.\n"
            "\n"
            "2. **Picker panel** — ledger row: `picker panel` (`DS with overrides`) · decision as above. Build\n"
            "   `ShelfPickerPopover`'s `ComboboxContent` with `className=\"w-[250px]\"` and `align=\"end\"`, keeping\n"
            "   `sideOffset={4}` and `shadow-md`.\n"
        )
        claims = sidecar.split_claims(wrapped, "sentences")
        self.assertEqual(
            claims,
            [
                "1. **File split — `ShelfPickerPopover` and `ShelfRow`** · decision: split today's "
                "`SaveToShelfCombobox` (`src/shelf-keeper/save-to-shelf-combobox.tsx`) into "
                "`src/shelf-keeper/shelf-picker-popover.tsx` (`ShelfPickerPopover`, holding a private "
                "`NewShelfRow`) and `src/shelf-keeper/shelf-row.tsx` (`ShelfRow`).",
                "Delete `save-to-shelf-combobox.tsx` and its test file, moving the existing tests onto "
                "the two new files.",
                "Update `KeepSpecimenButton`'s import to the new component.",
                "2. **Picker panel** — ledger row: `picker panel` (`DS with overrides`) · decision as above.",
                'Build `ShelfPickerPopover`\'s `ComboboxContent` with `className="w-[250px]"` and '
                '`align="end"`, keeping `sideOffset={4}` and `shadow-md`.',
            ],
        )
        for fragment in ("Delete", "files.", "above.", "it.", "Build the"):
            self.assertNotIn(fragment, claims)

    def test_a_wrapped_line_ending_without_a_stop_does_not_split(self) -> None:
        # "into" is followed by a backtick on the next line, but there is no `.` before it.
        wrapped = "split today's `SaveToShelfCombobox` (`x.tsx`) into\n`shelf-picker-popover.tsx`.\n"
        self.assertEqual(
            sidecar.split_claims(wrapped, "sentences"),
            ["split today's `SaveToShelfCombobox` (`x.tsx`) into `shelf-picker-popover.tsx`."],
        )

    def test_a_new_list_item_starts_a_paragraph_even_without_a_blank_line(self) -> None:
        claims = sidecar.split_claims("1. **First** item.\n2. **Second** item.\n", "sentences")
        self.assertEqual(claims, ["1. **First** item.", "2. **Second** item."])


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


class TheRequest(unittest.TestCase):
    """What goes out: one request, one three-way Choice per claim, the model pinned."""

    def test_the_model_id_is_pinned(self) -> None:
        self.assertEqual(sidecar.JevClient.MODEL_ID, "jev-1.13.0")

    def test_every_claim_gets_one_choice_carrying_the_three_options(self) -> None:
        questions = sidecar.build_questions(["first claim", "second claim"])
        self.assertEqual(len(questions), 2)
        for question in questions.values():
            self.assertEqual(question["type"], "choice")
            self.assertEqual(
                sorted(question["criteria"]), ["contradicts", "says_nothing", "supports"]
            )
        self.assertEqual(
            [question["instructions"]["claim"] for question in questions.values()],
            ["first claim", "second claim"],
        )

    def test_the_request_body_carries_the_state_the_model_and_the_questions(self) -> None:
        sent: dict = {}

        def capture(request, timeout=None):
            sent["url"] = request.full_url
            sent["headers"] = dict(request.headers)
            sent["body"] = json.loads(request.data.decode("utf-8"))
            return _Response({"answers": {"c0": {"probabilities": {"supports": 1.0}}}})

        with mock.patch("urllib.request.urlopen", side_effect=capture):
            sidecar.JevClient("k").ask("the ledger", sidecar.build_questions(["a claim"]))

        self.assertEqual(sent["url"], "https://api.typesafe.ai/v1/systemone")
        self.assertEqual(sent["headers"]["Authorization"], "Bearer k")
        self.assertEqual(sent["body"]["model"], "jev-1.13.0")
        self.assertEqual(sent["body"]["state"], "the ledger")
        self.assertEqual(list(sent["body"]["questions"]), ["c0"])


class TheBuckets(unittest.TestCase):
    """Each claim lands in one bucket at 0.8 per option."""

    def test_an_option_at_or_above_the_threshold_names_the_bucket(self) -> None:
        self.assertEqual(
            sidecar.bucket_for({"supports": 0.8, "contradicts": 0.1, "says_nothing": 0.1}),
            ("present", 0.8),
        )
        self.assertEqual(
            sidecar.bucket_for({"supports": 0.05, "contradicts": 0.9, "says_nothing": 0.05}),
            ("contradicted", 0.9),
        )
        self.assertEqual(
            sidecar.bucket_for({"supports": 0.02, "contradicts": 0.03, "says_nothing": 0.95}),
            ("added", 0.95),
        )

    def test_no_option_reaching_the_threshold_is_uncertain(self) -> None:
        bucket, probability = sidecar.bucket_for(
            {"supports": 0.79, "contradicts": 0.11, "says_nothing": 0.10}
        )
        self.assertEqual(bucket, "uncertain")
        self.assertEqual(probability, 0.79)

    def test_a_missing_answer_fails_the_output_rather_than_guessing(self) -> None:
        with self.assertRaises(sidecar.JevError):
            sidecar.read_buckets({}, ["a claim"])


class ThePlantedOutput(unittest.TestCase):
    """The planted copy of the frozen output, against the recorded response."""

    def setUp(self) -> None:
        self.client = RecordedJev()
        self.run = {"score": 1.0, "tracePath": str(PLANTED.parent / "out" / "trace.jsonl")}
        self.config = {"output": PLANTED.name, "source": PLANTED.name, "split": "sentences"}

    def test_three_plants_are_added_one_is_contradicted_and_the_paraphrases_are_present(self) -> None:
        entry = sidecar.score_output(self.config, self.run, self.client, scorings=1)

        self.assertEqual(entry["buckets"]["added"], 3)
        self.assertEqual(entry["buckets"]["contradicted"], 1)
        self.assertEqual(entry["buckets"]["uncertain"], 0)
        self.assertEqual(
            entry["buckets"]["present"], entry["claims"] - 4, "every other claim is present"
        )
        self.assertEqual([drift["claim"] for drift in entry["contradicted"]], [PLANTED_CONTRADICTION])
        self.assertEqual(sorted(drift["claim"] for drift in entry["added"]), sorted(PLANTED_ADDITIONS))
        for drift in entry["added"] + entry["contradicted"]:
            self.assertGreaterEqual(drift["probability"], sidecar.THRESHOLD)

    def test_the_whole_output_goes_out_in_one_request_per_scoring(self) -> None:
        sidecar.score_output(self.config, self.run, self.client, scorings=3)
        self.assertEqual(self.client.calls, 3)

    def test_the_state_each_request_carries_is_the_ledger(self) -> None:
        sidecar.score_output(self.config, self.run, self.client, scorings=1)
        self.assertIn("| picker panel |", self.client.states[0])
        self.assertNotIn("## Changes", self.client.states[0])

    def test_the_rubric_bit_is_false_while_anything_is_added_or_contradicted(self) -> None:
        entry = sidecar.score_output(self.config, self.run, self.client, scorings=4)
        self.assertEqual(entry["rubric_bits"], [False, False, False, False])


class Spread(unittest.TestCase):
    def test_a_unanimous_reading_has_no_spread(self) -> None:
        self.assertEqual(sidecar.disagreement([True, True, True]), 0.0)

    def test_an_even_split_is_a_half(self) -> None:
        self.assertEqual(sidecar.disagreement([True, False]), 0.5)

    def test_one_dissenter_in_ten_is_a_tenth(self) -> None:
        self.assertEqual(sidecar.disagreement([True] * 9 + [False]), 0.1)

    def test_nothing_to_read_has_no_spread(self) -> None:
        self.assertIsNone(sidecar.disagreement([]))

    def test_the_judge_grader_is_the_cases_sole_llm_grader(self) -> None:
        case = {"graders": [{"name": "r", "type": "regex"}, {"name": JUDGE_GRADER, "type": "llm"}]}
        self.assertEqual(sidecar.judge_grader_name(case, {}), JUDGE_GRADER)

    def test_a_named_judge_grader_in_the_config_wins(self) -> None:
        case = {"graders": [{"name": JUDGE_GRADER, "type": "llm"}]}
        self.assertEqual(sidecar.judge_grader_name(case, {"judge_grader": "other"}), "other")


class Retries(unittest.TestCase):
    """429 and 529 are retried with backoff; anything else fails the output at once."""

    def _client(self, slept: list[float]) -> sidecar.JevClient:
        return sidecar.JevClient("k", sleep=slept.append)

    def test_a_429_is_retried_and_the_answer_still_comes_back(self) -> None:
        slept: list[float] = []
        responses = [
            _http_error(429),
            _http_error(429),
            _Response({"answers": {"c0": {"probabilities": {"supports": 0.9}}}}),
        ]
        with mock.patch("urllib.request.urlopen", side_effect=responses) as urlopen:
            answers = self._client(slept).ask("state", sidecar.build_questions(["a claim"]))

        self.assertEqual(urlopen.call_count, 3)
        self.assertEqual(slept, [1.0, 2.0])
        self.assertEqual(sidecar.read_buckets(answers, ["a claim"])[0]["bucket"], "present")

    def test_a_529_is_retried_three_times_and_then_gives_up(self) -> None:
        slept: list[float] = []
        with mock.patch("urllib.request.urlopen", side_effect=[_http_error(529)] * 4) as urlopen:
            with self.assertRaises(sidecar.JevError):
                self._client(slept).ask("state", {})

        self.assertEqual(urlopen.call_count, sidecar.RETRIES + 1)
        self.assertEqual(slept, [1.0, 2.0, 4.0])

    def test_any_other_status_is_not_retried(self) -> None:
        slept: list[float] = []
        with mock.patch("urllib.request.urlopen", side_effect=[_http_error(500)]) as urlopen:
            with self.assertRaises(sidecar.JevError):
                self._client(slept).ask("state", {})

        self.assertEqual(urlopen.call_count, 1)
        self.assertEqual(slept, [])

    def test_a_connection_failure_is_not_retried(self) -> None:
        slept: list[float] = []
        with mock.patch("urllib.request.urlopen", side_effect=urllib.error.URLError("no host")):
            with self.assertRaises(sidecar.JevError):
                self._client(slept).ask("state", {})
        self.assertEqual(slept, [])


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

    def test_the_workspace_root_is_sealed_home_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            workspace = run_dir / "sealed" / "home" / "cwd"
            workspace.mkdir(parents=True)
            (workspace / "issue.md").write_text("hi", encoding="utf-8")
            self.assertEqual(
                sidecar.resolve_in_run(run_dir, "issue.md", "output"),
                workspace / "issue.md",
            )

    def test_an_unsealed_home_cwd_is_a_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            workspace = run_dir / "home" / "cwd"
            workspace.mkdir(parents=True)
            (workspace / "issue.md").write_text("hi", encoding="utf-8")
            self.assertEqual(
                sidecar.resolve_in_run(run_dir, "issue.md", "output"),
                workspace / "issue.md",
            )

    def test_a_sealed_directory_that_cannot_be_read_names_the_chmod_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            sealed = run_dir / "sealed"
            sealed.mkdir()
            sealed.chmod(0o000)
            try:
                with self.assertRaises(sidecar.SidecarError) as caught:
                    sidecar.resolve_in_run(run_dir, "issue.md", "output")
                self.assertIn(f"chmod 700 {run_dir} {sealed}", str(caught.exception))
            finally:
                sealed.chmod(0o700)

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


class TheWholeScript(unittest.TestCase):
    """`main` over a planted suite: where the file lands, and what a hole does to it."""

    def _run(self, aggregate: Path, factory) -> tuple[int, str]:
        """The exit code and the table, with stdout held back from the test report."""
        with mock.patch.dict(os.environ, {sidecar.API_KEY_ENV: "recorded-no-network"}):
            with mock.patch("sys.stdout", new=io.StringIO()) as out:
                exit_code = sidecar.main(["sidecar.py", str(aggregate)], client_factory=factory)
        return exit_code, out.getvalue()

    def test_sidecar_json_lands_beside_the_aggregate_and_leaves_it_alone(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            aggregate, case_dir = plant_a_suite(Path(tmp), [True, True])
            before = aggregate.read_bytes()
            case_files_before = sorted(path.name for path in case_dir.iterdir())

            exit_code, _ = self._run(aggregate, RecordedJev)

            self.assertEqual(exit_code, 0)
            self.assertEqual(aggregate.read_bytes(), before)
            self.assertEqual(sorted(path.name for path in case_dir.iterdir()), case_files_before)
            written = aggregate.parent / "sidecar.json"
            self.assertTrue(written.is_file())
            self.assertEqual(
                sorted(path.name for path in aggregate.parent.iterdir()),
                ["aggregate-result.json", "sidecar.json"],
            )

    def test_the_file_carries_the_buckets_the_drift_and_both_spreads(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            aggregate, _ = plant_a_suite(Path(tmp), [True, False])
            self.assertEqual(self._run(aggregate, RecordedJev)[0], 0)
            written = json.loads((aggregate.parent / "sidecar.json").read_text(encoding="utf-8"))

            self.assertEqual(written["model"], "jev-1.13.0")
            self.assertEqual(written["threshold"], 0.8)
            self.assertEqual(written["scorings_per_run"], 10)
            self.assertIn("added plus contradicted", written["rubric_bit"])
            self.assertIn("one minus the share", written["spread"])

            case = written["cases"][0]
            self.assertEqual(case["judge_spread"], 0.5, "one run passed the judge and one failed")
            self.assertEqual(case["sidecar_spread"], 0.0, "every scoring saw the same plants")
            self.assertEqual(len(case["runs"]), 2)
            for run in case["runs"]:
                self.assertFalse(run["unscored"])
                self.assertEqual(run["score"], 1.0)
                self.assertEqual(run["scorings"], 10)
                self.assertEqual(run["buckets"]["added"], 3)
                self.assertEqual(run["buckets"]["contradicted"], 1)
                self.assertEqual(len(run["added"]), 3)
                self.assertEqual(len(run["contradicted"]), 1)
                self.assertEqual(run["contradicted"][0]["claim"], PLANTED_CONTRADICTION)

    def test_a_failing_call_leaves_a_hole_and_a_non_zero_exit_while_the_rest_scores(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            aggregate, _ = plant_a_suite(Path(tmp), [True, True])

            exit_code, _ = self._run(aggregate, FailsAfterTheFirstOutput)

            self.assertEqual(exit_code, 1)
            written = json.loads((aggregate.parent / "sidecar.json").read_text(encoding="utf-8"))
            first, second = written["cases"][0]["runs"]
            self.assertFalse(first["unscored"])
            self.assertEqual(first["buckets"]["added"], 3)
            self.assertTrue(second["unscored"])
            self.assertIn("500", second["error"])
            self.assertNotIn("buckets", second)

    def test_the_table_on_stdout_is_markdown_carrying_both_spreads(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            aggregate, _ = plant_a_suite(Path(tmp), [True, True])
            _, table = self._run(aggregate, RecordedJev)

            self.assertIn("| case | run | score | claims | present | contradicted |", table)
            self.assertIn("| case | judge spread | sidecar spread |", table)
            self.assertIn("to-task-ledger-verbatim", table)
            self.assertIn("`jev-1.13.0`", table)
            self.assertIn(PLANTED_CONTRADICTION, table)
            for line in table.splitlines():
                if line.startswith("|"):
                    self.assertTrue(line.endswith("|"), line)

    def test_an_unscored_output_is_a_row_in_the_table_too(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            aggregate, _ = plant_a_suite(Path(tmp), [True, True])
            _, table = self._run(aggregate, FailsAfterTheFirstOutput)
            self.assertIn("unscored", table)


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
