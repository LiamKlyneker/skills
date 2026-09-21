#!/usr/bin/env python3
"""Score a finished eval run's claims against the state the run was given.

    python3 plugins/prd-workflow/evals/sidecar.py <results-stamp>/aggregate-result.json

A case opts in by carrying `sidecar.json` beside its `case.yaml`:

    {"output": "issue.md", "source": "issue.md", "split": "sentences"}

`output` and `source` are paths inside the run's kept working directory. The output's
`## Changes` section becomes one claim per sentence (`split: sentences`) or per line
(`split: lines`); the source contributes the state those claims are checked against. A
claim whose normalised text occurs in the normalised state is `present`. Everything else
is handed to the Jev stage, which reads a judgement out of a pinned model.

The sidecar sits beside the gate and never inside it: it never edits the runner's JSON
and never writes into a case directory. See ADR 0016.
"""

from __future__ import annotations

import json
import os
import re
import sys
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


class JevClient:
    """The judgement half, pinned to one model id so two runs can be compared."""

    MODEL_ID = "jev-1.13.0"

    def __init__(self, api_key: str, model_id: str = MODEL_ID) -> None:
        self.api_key = api_key
        self.model_id = model_id

    def judge(self, claim: str, state: str) -> bool:
        raise NotImplementedError("the Jev request is not wired yet")


def adjudicate(unmatched: list[str], state: str, client: JevClient | None) -> dict[str, list[str]]:
    """Hand the claims exact match could not settle to the model, when there is one."""
    if client is None:
        return {"supported": [], "unsupported": [], "unscored": list(unmatched)}
    supported: list[str] = []
    unsupported: list[str] = []
    for claim in unmatched:
        (supported if client.judge(claim, state) else unsupported).append(claim)
    return {"supported": supported, "unsupported": unsupported, "unscored": []}


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


def score_run(config: dict, run: dict) -> dict:
    run_dir = run_directory(run["tracePath"])
    output_path = resolve_in_run(run_dir, config["output"], "output")
    source_path = resolve_in_run(run_dir, config["source"], "source")
    claims = read_output_claims(output_path, config.get("split", "sentences"))
    present, unmatched = exact_match(claims, read_source_state(source_path))
    return {"claims": len(claims), "present": present, "unmatched": unmatched}


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {Path(argv[0]).name} <results-stamp>/aggregate-result.json", file=sys.stderr)
        return 2

    if not os.environ.get(API_KEY_ENV):
        print(
            f"sidecar: {API_KEY_ENV} is not set, so nothing was scored and no file was written."
        )
        return 0

    aggregate_path = Path(argv[1]).resolve()
    for case, config, run in scored_cases(aggregate_path):
        result = score_run(config, run)
        print(
            f"{case['name']}: {len(result['present'])}/{result['claims']} claims present, "
            f"{len(result['unmatched'])} for the Jev stage"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
