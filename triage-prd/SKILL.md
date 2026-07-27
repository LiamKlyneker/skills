---
name: triage-prd
description: PRD-scoped triage — take the QA-finding comments logged on a PRD's PR (qa-prd-log output), confirm each against the PRD/issues/decision-lock and the code, pinpoint root cause via a cheap subagent, then file cold-runnable GitHub issues (in this repo, or in the related repo that owns the contract boundary) that work-on-prd/work-on-issue can execute with no plan mode. Use when the user says "triage-prd", passes a PRD/PR to triage, or wants a PR's QA findings promoted to executable issues.
---

# triage-prd

The **investigate + promote** half of the PRD QA loop. `qa-prd-log` *captures* findings as self-contained comments on a PRD's PR; `triage-prd` *confirms, roots-causes, and promotes* the survivors into **cold-runnable issues** — one per finding — that `work-on-prd` (or `work-on-issue`) executes later with zero re-research. It is the PRD-scoped specialization of the generic triage pattern: it never reads a deploy-preview comment stream, it reads a PRD.

Its edge over a generic triage is **decision context**: it loads the PRD, its child issues, the touched `CONTEXT.md`, and the locked decisions — so it can tell a real defect from a gap that was **deferred on purpose**, and route a finding to the repo that actually owns it.

Project facts (repos, commands, verify ladder) come from the **project adapter** at `<repo-root>/.claude/project/adapter.md` — read it; never hardcode them here.

## Two non-negotiables

1. **Every issue is a cold-runnable fix plan.** A future `work-on-issue`/`work-on-prd` session (fresh, no memory of this chat) must fix it with **no plan mode and no re-investigation**. So each issue carries: root cause (confirmed, not hypothesized), exact files + prior art, the fix approach, and testable acceptance criteria — mirroring the `to-issues` child template so the worker consumes a bug identically to a planned child.
2. **Never fix.** triage-prd stops at filed issues. No code changes, no fix-tests. The fix belongs to `work-on-prd`/`work-on-issue`. (Mirror of qa-prd-log's capture/solve line, one phase later.)

## Context loading (once, up front)

Establish PRD scope before the first finding, and hold it for the whole session:

- **Which PRD / PR.** Resolve the PR (`gh pr list` / branch's PR) and the PRD issue it runs (PR body's `Runs PRD #N` + `## Children`). Ask if not given.
- **PRD issue** (`gh issue view <n>`) — especially its cross-repo dependencies, deferred / out-of-scope notes, and explicit locked decisions.
- **Child issues** + the PR's **Closes map** (#c1…#cN → their file areas) — this is the *owning-slice* attribution map, near-free.
- **Touched `CONTEXT.md`** for the feature dir(s) under test (use the `scoped-context` skill if available).
- **QA doc** at the path the adapter's `## QA doc convention` defines, plus code comments in the touched files marked "deferred", "later slice", "no resolver yet", placeholder. This is what powers the gap classification below.

## Input

The `### <emoji> QA finding:` comments on the PRD's PR (qa-prd-log output). Take **one per turn**; if the user pastes several, queue the rest. Ad-hoc paste (a finding not yet on the PR) is allowed — treat it identically.

## Cadence (one finding per turn — clone of grill-me / qa-prd-log)

For each finding: **capture → validate (gap classification) → investigate (subagent) → dispose → show card → user confirm/correct → next.** Loop until the user says done, then **board → publish**. Never batch.

## Per-finding process

### 1. Capture

Record the finding + its source (PR comment permalink, `file:line`, author). qa-prd-log already did the classification + hypothesis + evidence — inherit it as the warm start; do not re-derive.

### 2. Validate + gap classification (HARD GATE — before filing anything)

qa-prd-log labels root cause as *hypothesis*. triage-prd's first job is to decide what the finding **is**, using the loaded decision context. Resolve from PRD/issues/CONTEXT/code before asking the user:

| Verdict | Evidence | Action |
|---|---|---|
| **Real defect** | behavior deviates from intent, still reproduces on the branch | → bug track (investigate + file) |
| **Already planned** | an open issue/child or a future-slice note already covers it | link it, **do not** dup |
| **Intentionally deferred / out-of-scope** | a PRD decision or code comment says so (e.g. *"no storage-base resolver exists yet"*) | cite it — **not a bug** |
| **Genuine unplanned gap** | nothing in PRD/issues/decisions covers it | **propose a follow-up issue and ASK the user** before creating |

- **Bugs** go to the board and are confirmed at publish time.
- **Follow-ups / enhancements / deferred gaps always ask first** — never auto-file a new feature slice. State the follow-up scope and let the user say create / link-existing / leave-noted.

### 3. Investigate — one subagent per finding

Spawn **one read-only subagent per finding** (the token-saver: the main session orchestrates + decides only, never greps/blames itself). Use the project explorer agent named in the adapter's `## Sources of truth`, or `Explore` where it says None.

- **Model:** **Sonnet-class** by default (it authors a fix plan). Drop to **Haiku-class** for a trivial/mechanical finding; **never Opus**. Speak in tiers per `../_shared/model-effort-heuristics.md`; for exact ids defer to `claude-api`.
- **Warm start:** hand it qa-prd-log's hypothesis + `file:line`. Its job is **confirm + plan**, not discover-from-scratch.
- **Job:**
  1. **Confirm the root cause** on the current branch — trace the call path; for a contract-boundary finding, re-run the decisive `curl` against the live endpoint.
  2. **Attribute to the owning child slice** (from the Closes map) — always, it's cheap.
  3. **Introducing commit `@<sha>` — only when it earns its place:** run `git blame` / `git bisect run <repro>` **only for a regression** (worked before, broke) or when the diff reveals deliberate intent. For a never-worked / net-new-feature bug or a deferred gap, **skip the archaeology** — the `file:line` + owning slice already localize it.
  4. **Author the fix plan** — exact files, prior art to copy, the change, and testable acceptance criteria. This is what makes the issue cold-runnable.
- **Return contract:** confirmed root cause · owning slice · `@sha` (only if a regression) · fix plan · files/prior-art · acceptance criteria · which repo owns the fix.

<cross-repo>
### Contract-boundary findings — investigate and file in the related repo

The adapter names both halves: `## Repo → Related repos` says which repo owns the other side of the API boundary, and `## Sources of truth → Contract-boundary explorer agent` names the read-only agent that owns it (API handlers, contract spec, data layer). For a finding whose root cause is across that boundary:

- **Spawn that explorer agent** instead of the project one. It reads the actual handler code to confirm the cause, plus that repo's scoped `CONTEXT.md` and its own issue conventions.
- It files the issue **in the related repo**, native to **their** house style, so their own `work-on-issue` can execute it — with a **"Discovered via `<this-repo>#<pr>`"** back-link.
- **This side:** carry a `blocked-external` pointer issue, named under `## Blocked by` on whichever child needs the fix. **Cross-repo auto-close does not fire** (`Closes` is same-repo only) — the local pointer is closed by hand when the other fix ships.
- If the adapter says "None" for either field, there is no boundary to route across: file the issue here and say plainly that the boundary is unmodelled, rather than guessing a repo.

Both repos work in synergy; the issue just lands where the fix lands.
</cross-repo>

### 4. Dispose + dedupe

- **Dedupe against the tracker** — `gh issue list --search "<keywords>" --state all` (right repo) before filing; a match makes this a `reject (duplicate)` pointing at it.
- **Route** per the table below.

<dispositions>
| Kind | Where | Labels | Picked by work-on-prd? |
|---|---|---|---|
| **Merge-blocker** | this repo, `## Parent` → PRD `#N` | `bug` + `ready-to-start` | yes — on the PRD branch, before merge |
| **Deferred / follow-up** *(after user OK)* | this repo, `## Parent` → PRD `#N` | `bug`/`enhancement` + `deferred` | no (not `ready-to-start`) — a known follow-up |
| **Contract boundary** | **related repo**, "Discovered via …#PR" | `bug` (their style); local `blocked-external` pointer under the affected child's `## Blocked by` | n/a — no cross-repo auto-close; closed by hand |
| **Reject** (WAD / dup / invalid) | this repo | file-then-close `duplicate`/`wontfix`/`invalid` + one-line rationale (cite the decision) | — |
</dispositions>

### 5. Show the card, confirm, next

```
QA-<n>  [<classification> · <severity> · <disposition> → <label>]
Finding: <one-line symptom>
Owning slice: #<child> (<what that slice built>)
Root cause: CONFIRMED — <cause>; <path>:<lines>
Commit: <sha — only if a regression; else "n/a (introduced by the feature slice)">
Disposition: <repo + parent ref + title prefix>
```

Print the card + recommended disposition, get confirm/correct, ask for the next finding.

## Board + publish

When the user says done:

1. **Board** — every finding with verdict / owning slice / disposition / target repo. Get approval before publishing.
2. **Publish** with `gh` (let it resolve the repo; use `--repo` for related-repo issues). Open issues for bugs/follow-ups; file-then-close for rejects. Follow-ups only if the user already said yes in step 2 of that finding.
3. **Report** created issue numbers grouped by disposition + repo, e.g.
   `ready-to-start: #61 #62 · deferred: #63 · <related repo>#NNN · closed: —`
4. **Remind** the human of the external steps triage-prd can't do: (a) close resolved qa-prd-log PR comments / mark them triaged, (b) the related-repo issue is tracked but **not** auto-closed by this repo's PR.

## Issue template (mirror the `to-issues` child so work-on-prd eats it identically)

```
## Parent

<owner>/<repo>#<PRD-number>

## Blocked by

None — can start immediately.   (or #NNN for a real blocker, e.g. a contract-boundary dep)

## External steps

None — fully fixable from the editor.   (or the `- [ ]` steps a human must do)

## What to fix

<the fix plan — current vs expected, and the change to make>

## Root cause

Confirmed: <the actual cause, traced — not a hypothesis>.
Owning slice: #<child> (<what that slice built>).
Introduced by: `<sha>` — <one line>.   ← ONLY if a regression / reveals intent; omit otherwise.

## Worker context

- **Files**: <exact paths to touch>.
- **Read first**: <scoped CONTEXT.md>.
- **Prior art**: <the pattern/example to copy>.
- **Verify**: the adapter's `## Verify ladder` — L2 floor always; **L3** (boot + screenshot) if user-visible.
- **User-visible**: y/n.

## QA notes

<how to verify the fix in the running app — concrete steps>.

## Acceptance criteria

- [ ] <testable exit condition — the behavior, phrased as a check>
- [ ] <verify ladder step green>
```

Title: **`[QA] <one-line symptom>`** — the bracket prefix distinguishes triage-prd bugs from planned children at a glance (`work-on-prd` ignores the prefix). Severity = technical impact, independent of priority; both live in the issue body (no GitHub labels for them).

## Boundary / handoff

- triage-prd = **investigate + decide + file**. It does **not** fix, and it does **not** need a separate "fix the bugs" skill: a bug filed in this repo with `## Parent → #N` + `ready-to-start` **is a PRD child** — `work-on-prd` (re-entrant, cold-start) discovers it via `in:body "#N"` and works it on the PRD branch with no new machinery. See `../_shared/prd-eligibility.md`.
- Deferred (`deferred` label) issues sit as known follow-ups until promoted (relabel `ready-to-start`).
- Related-repo issues are executed by that repo's own `work-on-issue`.
