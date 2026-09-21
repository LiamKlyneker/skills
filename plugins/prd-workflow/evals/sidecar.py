#!/usr/bin/env python3
"""Score a finished eval run's claims against the state the run was given.

    python3 plugins/prd-workflow/evals/sidecar.py <results-stamp>/aggregate-result.json

A case opts in by carrying `sidecar.json` beside its `case.yaml`:

    {"output": "issue.md", "source": "issue.md", "split": "sentences"}

`output` and `source` are paths inside the run's kept working directory. The output's
`## Changes` section becomes one claim per sentence (`split: sentences`) or per line
(`split: lines`); the source contributes the state those claims are checked against. A
claim whose normalised text occurs in the normalised state is `present`. Every other claim
of one output goes out in a single `POST /v1/systemone` request, one three-way Choice each,
and lands in `present`, `contradicted`, `added` or `uncertain`.

The results land in `sidecar.json` in the stamp directory beside the aggregate, and as a
Markdown table on stdout. The sidecar sits beside the gate and never inside it: it never
edits the runner's JSON and never writes into a case directory. See ADR 0016.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

API_KEY_ENV = "TYPESAFE_API_KEY"

CHANGES_HEADING = "## Changes"
LEDGER_HEADING = "## Fidelity ledger"


class SidecarError(Exception):
    """A malformed input. Carries the path, so a bad run names itself."""


# --- the deterministic half -------------------------------------------------------

_CURLY = {"“": '"', "”": '"', "‘": "'", "’": "'"}

# A sentence ends on `.`, `!` or `?` and the next one opens on a capital, a backtick or a
# bracket. A version number, a `.tsx` path and a bolded continuation all fail that second
# half, which is what keeps them inside one claim.
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z`(\[\"'])")


def normalise(text: str) -> str:
    """Collapse whitespace runs, straighten curly quotes, drop backticks, lower-case.

    Punctuation other than backticks survives, so two claims that differ by a comma stay
    two different claims.
    """
    for curly, straight in _CURLY.items():
        text = text.replace(curly, straight)
    text = text.replace("`", "")
    return re.sub(r"\s+", " ", text).strip().lower()


def split_sentences(line: str) -> list[str]:
    return [part.strip() for part in _SENTENCE_END.split(line) if part.strip()]


def split_claims(text: str, split: str) -> list[str]:
    """One claim per sentence or per line. A claim never spans a blank line."""
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    if split == "lines":
        return lines
    if split == "sentences":
        return [claim for line in lines for claim in split_sentences(line)]
    raise SidecarError(f"unknown split mode {split!r}: expected 'sentences' or 'lines'")


def section(markdown: str, heading: str) -> str | None:
    """The body under the first heading that starts with `heading`, up to the next `##`."""
    lines = markdown.splitlines()
    for index, line in enumerate(lines):
        if not line.startswith(heading):
            continue
        body: list[str] = []
        for following in lines[index + 1 :]:
            if following.startswith("## "):
                break
            body.append(following)
        return "\n".join(body)
    return None


def read_output_claims(path: Path, split: str) -> list[str]:
    markdown = path.read_text(encoding="utf-8")
    changes = section(markdown, CHANGES_HEADING)
    if changes is None:
        raise SidecarError(f"{path}: no `{CHANGES_HEADING}` section to split into claims")
    return split_claims(changes, split)


def read_source_state(path: Path) -> str:
    """The ledger table when the file has one, the whole file when it does not.

    The state the claims are checked against is the fidelity ledger, and the produced
    issue carries its own copy of it — so the same reader serves a source that is the
    issue and a source that is the brief upstream of it.
    """
    markdown = path.read_text(encoding="utf-8")
    ledger = section(markdown, LEDGER_HEADING)
    return ledger if ledger is not None else markdown


def exact_match(claims: list[str], source: str) -> tuple[list[str], list[str]]:
    """Split the claims into the ones the source already states and the rest.

    The rest is the Jev stage's input; nothing here decides against a claim.
    """
    normalised_source = normalise(source)
    present: list[str] = []
    unmatched: list[str] = []
    for claim in claims:
        target = present if normalise(claim) in normalised_source else unmatched
        target.append(claim)
    return present, unmatched


# --- the Jev stage ----------------------------------------------------------------

ENDPOINT = "https://api.typesafe.ai/v1/systemone"
TIMEOUT_SECONDS = 120.0

RETRY_STATUSES = frozenset({429, 529})
RETRIES = 3
BACKOFF_SECONDS = 1.0

THRESHOLD = 0.8
SCORINGS_PER_RUN = 10

RELATION_CRITERIA = {
    "supports": "The state states the claim or directly implies that it is true",
    "contradicts": "The state states the opposite of the claim or implies it is false",
    "says_nothing": "The state does not address what the claim asserts, either way",
}

RELATION_BUCKET = {"supports": "present", "contradicts": "contradicted", "says_nothing": "added"}
BUCKETS = ("present", "contradicted", "added", "uncertain")

RUBRIC_BIT = "added plus contradicted equals zero"
SPREAD_DEFINITION = (
    "the disagreement rate of a bit over a set of readings: one minus the share of the "
    "readings holding the most common value, so 0.0 is unanimous and 0.5 is an even split"
)


class JevError(Exception):
    """A request that did not come back as an answer. The output it was for goes unscored."""


def claim_id(index: int) -> str:
    return f"c{index}"


def build_questions(claims: list[str]) -> dict[str, dict]:
    """One three-way Choice per claim, all of them in one request.

    The claim rides in the question's structured instructions rather than in the state, so
    every question of the request shares the one state the request carries.
    """
    return {
        claim_id(index): {
            "type": "choice",
            "instructions": {
                "claim": claim,
                "question": "How does the state relate to `claim`?",
            },
            "criteria": RELATION_CRITERIA,
        }
        for index, claim in enumerate(claims)
    }


def bucket_for(probabilities: dict[str, float]) -> tuple[str, float]:
    """The bucket an answer's probabilities put a claim in, and the probability that did it.

    Probabilities sum to 1, so at or above 0.8 at most one option can qualify and the order
    of the scan cannot change the answer.
    """
    for option, bucket in RELATION_BUCKET.items():
        probability = probabilities.get(option, 0.0)
        if probability >= THRESHOLD:
            return bucket, probability
    highest = max(probabilities.values(), default=0.0)
    return "uncertain", highest


def read_buckets(answers: dict[str, dict], claims: list[str]) -> list[dict]:
    """One verdict per claim, in the order the claims were asked."""
    verdicts: list[dict] = []
    for index, claim in enumerate(claims):
        answer = answers.get(claim_id(index))
        if not isinstance(answer, dict) or "probabilities" not in answer:
            raise JevError(f"no Choice answer came back under {claim_id(index)!r}")
        bucket, probability = bucket_for(answer["probabilities"])
        verdicts.append({"claim": claim, "bucket": bucket, "probability": round(probability, 4)})
    return verdicts


class JevClient:
    """The judgement half, pinned to one model id so two runs can be compared."""

    MODEL_ID = "jev-1.13.0"

    def __init__(
        self,
        api_key: str,
        model_id: str = MODEL_ID,
        endpoint: str = ENDPOINT,
        sleep=time.sleep,
    ) -> None:
        self.api_key = api_key
        self.model_id = model_id
        self.endpoint = endpoint
        self.sleep = sleep

    def ask(self, state: str, questions: dict[str, dict]) -> dict[str, dict]:
        """One request, one answer per question. Raises `JevError` on anything else."""
        payload = json.dumps(
            {"state": state, "model": self.model_id, "questions": questions}
        ).encode("utf-8")
        for attempt in range(RETRIES + 1):
            try:
                return self._post(payload)
            except urllib.error.HTTPError as failure:
                if failure.code not in RETRY_STATUSES or attempt == RETRIES:
                    raise JevError(f"POST {self.endpoint} returned {failure.code}") from failure
                self.sleep(BACKOFF_SECONDS * 2**attempt)
            except (urllib.error.URLError, OSError, ValueError) as failure:
                raise JevError(f"POST {self.endpoint} failed: {failure}") from failure
        raise JevError(f"POST {self.endpoint} kept returning a retryable status")

    def _post(self, payload: bytes) -> dict[str, dict]:
        request = urllib.request.Request(
            self.endpoint,
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            body = json.loads(response.read().decode("utf-8"))
        answers = body.get("answers")
        if not isinstance(answers, dict):
            raise JevError(f"POST {self.endpoint} returned no answers map")
        return answers


# --- the runner's result ----------------------------------------------------------


def run_directory(trace_path: str) -> Path:
    """The kept working directory a run's `tracePath` sits under.

    The runner writes the trace to `out/trace.jsonl` inside the directory it ran the case
    in, so the run directory is the trace's grandparent.
    """
    return Path(trace_path).resolve().parent.parent


def resolve_in_run(run_dir: Path, relative: str, label: str) -> Path:
    candidate = run_dir / relative
    if candidate.is_file():
        return candidate
    matches = sorted(run_dir.glob(f"*/{relative}"))
    if len(matches) == 1:
        return matches[0]
    raise SidecarError(f"no {label} at {candidate} (is the run directory still on disk?)")


def scored_cases(aggregate_path: Path) -> list[tuple[dict, dict, dict]]:
    """Every (case, sidecar config, run) triple the aggregate carries a config for.

    A case with no `sidecar.json` beside its `case.yaml` is skipped, not failed.
    """
    aggregate = json.loads(aggregate_path.read_text(encoding="utf-8"))
    suite_root = Path(aggregate.get("suite", {}).get("root", aggregate_path.parent))
    triples: list[tuple[dict, dict, dict]] = []
    for case in aggregate.get("cases", []):
        config_path = suite_root / case.get("dir", "") / "sidecar.json"
        if not config_path.is_file():
            continue
        config = json.loads(config_path.read_text(encoding="utf-8"))
        for runs in case.get("arms", {}).values():
            for run in runs:
                if not run.get("tracePath"):
                    raise SidecarError(
                        f"{aggregate_path}: a run of case {case.get('name')!r} has no tracePath, "
                        "so its kept directory cannot be derived"
                    )
                triples.append((case, config, run))
    return triples


def grouped_cases(aggregate_path: Path) -> list[tuple[dict, dict, list[dict]]]:
    """The same triples, with every run of one case gathered under it."""
    groups: dict[str, tuple[dict, dict, list[dict]]] = {}
    for case, config, run in scored_cases(aggregate_path):
        group = groups.setdefault(case.get("name", ""), (case, config, []))
        group[2].append(run)
    return list(groups.values())


# --- scoring ----------------------------------------------------------------------


def score_run(config: dict, run: dict) -> dict:
    """The deterministic half for one run: its claims, and which the state already states."""
    run_dir = run_directory(run["tracePath"])
    output_path = resolve_in_run(run_dir, config["output"], "output")
    source_path = resolve_in_run(run_dir, config["source"], "source")
    claims = read_output_claims(output_path, config.get("split", "sentences"))
    state = read_source_state(source_path)
    present, unmatched = exact_match(claims, state)
    return {"claims": claims, "state": state, "present": present, "unmatched": unmatched}


def score_output(config: dict, run: dict, client: JevClient, scorings: int) -> dict:
    """One run's output, scored `scorings` times. `JevError` leaves it for the caller."""
    deterministic = score_run(config, run)
    unmatched = deterministic["unmatched"]
    questions = build_questions(unmatched)
    readings = [
        read_buckets(client.ask(deterministic["state"], questions), unmatched)
        for _ in range(scorings)
    ]

    reported = readings[0]
    counts = {bucket: 0 for bucket in BUCKETS}
    counts["present"] = len(deterministic["present"])
    for verdict in reported:
        counts[verdict["bucket"]] += 1

    def drift(bucket: str) -> list[dict]:
        return [
            {"claim": verdict["claim"], "probability": verdict["probability"]}
            for verdict in reported
            if verdict["bucket"] == bucket
        ]

    return {
        "score": run.get("score"),
        "unscored": False,
        "claims": len(deterministic["claims"]),
        "buckets": counts,
        "added": drift("added"),
        "contradicted": drift("contradicted"),
        "scorings": len(readings),
        "rubric_bits": [
            all(verdict["bucket"] not in ("added", "contradicted") for verdict in reading)
            for reading in readings
        ],
    }


def disagreement(values: list) -> float | None:
    """One minus the share of the readings holding the most common value."""
    if not values:
        return None
    return round(1 - max(Counter(values).values()) / len(values), 4)


def judge_grader_name(case: dict, config: dict) -> str | None:
    """The `llm` grader whose pass bit the judge spread is taken over.

    A case is capped at one `llm` grader, so naming it in `sidecar.json` is only needed
    where that cap does not hold.
    """
    named = config.get("judge_grader")
    if named:
        return named
    llm = [g.get("name") for g in case.get("graders", []) if g.get("type") == "llm"]
    return llm[0] if len(llm) == 1 else None


def judge_bits(runs: list[dict], name: str | None) -> list[bool]:
    if not name:
        return []
    bits: list[bool] = []
    for run in runs:
        for grader in run.get("graders", []):
            if grader.get("name") == name:
                bits.append(bool(grader.get("passed")))
    return bits


def score_case(case: dict, config: dict, runs: list[dict], client: JevClient, scorings: int) -> dict:
    entries: list[dict] = []
    for run in runs:
        try:
            entries.append(score_output(config, run, client, scorings))
        except JevError as failure:
            entries.append({"score": run.get("score"), "unscored": True, "error": str(failure)})

    rubric_bits = [bit for entry in entries for bit in entry.get("rubric_bits", [])]
    grader = judge_grader_name(case, config)
    return {
        "name": case.get("name"),
        "judge_grader": grader,
        "judge_spread": disagreement(judge_bits(runs, grader)),
        "sidecar_spread": disagreement(rubric_bits),
        "runs": entries,
    }


def report(aggregate_path: Path, client: JevClient, scorings: int = SCORINGS_PER_RUN) -> dict:
    cases = [
        score_case(case, config, runs, client, scorings)
        for case, config, runs in grouped_cases(aggregate_path)
    ]
    return {
        "model": client.model_id,
        "threshold": THRESHOLD,
        "scorings_per_run": scorings,
        "rubric_bit": RUBRIC_BIT,
        "spread": SPREAD_DEFINITION,
        "aggregate": str(aggregate_path),
        "cases": cases,
    }


# --- the table --------------------------------------------------------------------


def _spread(value: float | None) -> str:
    return "—" if value is None else f"{value:.2f}"


def markdown_report(report_data: dict) -> str:
    """The same numbers as a Markdown table that pastes into an issue comment."""
    lines = [
        "### Sidecar — claim drift beside the gate",
        "",
        f"Model `{report_data['model']}` · option threshold {report_data['threshold']:.2f} · "
        f"{report_data['scorings_per_run']} scorings per run.",
        f"Rubric bit: {report_data['rubric_bit']}. Spread is {report_data['spread']}.",
        "",
        "| case | run | score | claims | present | contradicted | added | uncertain |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for case in report_data["cases"]:
        for index, run in enumerate(case["runs"], start=1):
            score = "—" if run.get("score") is None else f"{run['score']:.2f}"
            if run["unscored"]:
                lines.append(f"| {case['name']} | {index} | {score} | unscored | — | — | — | — |")
                continue
            counts = run["buckets"]
            lines.append(
                f"| {case['name']} | {index} | {score} | {run['claims']} | {counts['present']} | "
                f"{counts['contradicted']} | {counts['added']} | {counts['uncertain']} |"
            )

    lines += [
        "",
        "| case | judge spread | sidecar spread |",
        "| --- | ---: | ---: |",
    ]
    for case in report_data["cases"]:
        lines.append(
            f"| {case['name']} | {_spread(case['judge_spread'])} | "
            f"{_spread(case['sidecar_spread'])} |"
        )

    drift = [
        (case["name"], bucket, entry)
        for case in report_data["cases"]
        for run in case["runs"]
        for bucket in ("contradicted", "added")
        for entry in run.get(bucket, [])
    ]
    if drift:
        lines += ["", "| case | bucket | probability | claim |", "| --- | --- | ---: | --- |"]
        for name, bucket, entry in drift:
            claim = entry["claim"].replace("|", "\\|")
            lines.append(f"| {name} | {bucket} | {entry['probability']:.2f} | {claim} |")
    return "\n".join(lines) + "\n"


def unscored_outputs(report_data: dict) -> int:
    return sum(1 for case in report_data["cases"] for run in case["runs"] if run["unscored"])


def main(argv: list[str], client_factory=None) -> int:
    if len(argv) != 2:
        print(f"usage: {Path(argv[0]).name} <results-stamp>/aggregate-result.json", file=sys.stderr)
        return 2

    api_key = os.environ.get(API_KEY_ENV)
    if not api_key:
        print(
            f"sidecar: {API_KEY_ENV} is not set, so nothing was scored and no file was written."
        )
        return 0

    aggregate_path = Path(argv[1]).resolve()
    client = client_factory() if client_factory else JevClient(api_key)
    report_data = report(aggregate_path, client)

    destination = aggregate_path.parent / "sidecar.json"
    destination.write_text(json.dumps(report_data, indent=2) + "\n", encoding="utf-8")

    print(markdown_report(report_data), end="")
    holes = unscored_outputs(report_data)
    if holes:
        print(f"\nsidecar: {holes} output(s) went unscored; see {destination}.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
