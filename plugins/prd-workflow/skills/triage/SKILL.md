---
name: triage
description: PRD-scoped triage — take the [FINDING] comments manual-qa logged on a PRD's PR, confirm each against the PRD/issues/decision-lock and the code, pinpoint root cause via a cheap subagent, then file cold-runnable GitHub issues (in this repo, or in the related repo that owns the contract boundary) that work-on-prd/work-on-issue can execute with no plan mode. Invoke /prd-workflow:triage to promote a PRD's PR QA findings into executable issues.
disable-model-invocation: true
---

# triage

The **investigate + promote** half of the PRD QA loop. `manual-qa` — the capture phase — composes a run's pass from what landed on the branch, drives it flow by flow, and logs each failure as a self-contained `### [FINDING]` comment on a PRD's PR; `triage` *confirms, roots-causes, and promotes* the survivors into **cold-runnable issues** — one per finding — that `work-on-prd` (or `work-on-issue`) executes later with zero re-research. It is the PRD-scoped specialization of the generic triage pattern: it never reads a deploy-preview comment stream, it reads a PRD.

Its edge over a generic triage is **decision context**: it loads the PRD, its child issues, the touched `CONTEXT.md`, and the locked decisions — so it can tell a real defect from a gap that was **deferred on purpose**, and route a finding to the repo that actually owns it.

Project facts (repos, commands, verify ladder) come from the **project adapter** at `<repo-root>/.claude/project/adapter.md` — read it; never hardcode them here.

## Two non-negotiables

1. **Every issue is a cold-runnable fix plan.** A future `work-on-issue`/`work-on-prd` session (fresh, no memory of this chat) must fix it with **no plan mode and no re-investigation**. So each issue carries: root cause (confirmed, not hypothesized), exact files + prior art, the fix approach, and testable acceptance criteria — mirroring the `to-issues` child template so the worker consumes a bug identically to a planned child.
2. **Never fix.** triage stops at filed issues. No code changes, no fix-tests. The fix belongs to `work-on-prd`/`work-on-issue`. (Mirror of `manual-qa`'s `<the-line>`, one phase later.)

## Context loading (once, up front)

Establish PRD scope before the first finding, and hold it for the whole session:

- **Which PRD / PR.** Resolve the PRD, then its run's PR via the machine block's `PRD: #<n>` resume key in the PR body — the same key `manual-qa` uses to locate a run, matched as a whole line (`PRD: #12` is a prefix of `PRD: #127`). Ask if not given.
- **PRD issue** (`gh issue view <n> --json body,comments`) — the body for its cross-repo dependencies, deferred / out-of-scope notes, and explicit locked decisions. The same call's `comments` array carries `manual-qa`'s **receipt** from any pass that has run — which flows it walked and where it stopped. Read it as **context only, never matched**: it is free-form by design, nothing parses it, and it is not a source of findings. The findings are on the PR.
- **Child issues** + the PR's **Closes map** (#c1…#cN → their file areas) — this is the *owning-slice* attribution map, near-free.
- **Touched `CONTEXT.md`** for the feature dir(s) under test (use the `scoped-context` skill if available), plus code comments in those files marked "deferred", "later slice", "no resolver yet", placeholder. Together with the PRD body and the children, this is what powers the gap classification below — there is no QA comment to read, and a PRD whose run landed only refactors or bumps has no QA artifact at all, which is normal rather than a gap. The PRD's `needs-qa` label is worth noting — it means no pass has completed yet — but it does not change the classification.

## Input

**The `### [FINDING]` comments on the PRD's PR.** That marker is a **parse contract**, hardcoded in both skills and deliberately absent from the adapter: `manual-qa`'s `## Findings` is its normative writer, this is the only matcher, and there is **no fallback for any older marker** — a comment predating it is pasted in by hand, which is what ad-hoc input already handles at zero cost.

Read them in one call, and keep each `url` — *Marking the finding comment triaged* needs it to write back:

```bash
gh pr view <pr-number> --json comments --jq '.comments[] | {url, body}'
```

Take **one per turn**; if the user pastes several, queue the rest. Ad-hoc paste (a finding not yet on the PR) is allowed — treat it identically.

### Skip anything already triaged

**A `### [FINDING]` comment whose body contains `**Triaged:**` is skipped outright** — before the cadence, before any subagent, before any tracker search. Publishing writes that line onto the comment as soon as the issue exists (*Marking the finding comment triaged*), so its presence means a previous pass already promoted this one.

- **A skip is not a reject.** It is not filed, not closed, not carded, and not reported as a duplicate. Say in one line which findings were skipped and which issues they already point at (the line carries the number), then move on.
- It is a plain **substring check on a body you already fetched** — no API call, no fuzzy matching, no title comparison, so no false positives.
- It **replaces** the per-finding `gh issue list --search` for already-promoted findings rather than running alongside it; see step 4 for what that search is still for.

Without this, every finding surviving on the PR from an earlier pass gets a brand-new `[BUG]` filed and immediately closed as a duplicate — of the issue it produced itself — and the noise compounds each cycle.

<!-- Rejected alternatives, recorded so they are not re-proposed. (a) A reaction on the finding comment: one call and no edit, but it carries no *which issue*, so triage's own output would be unreadable without a hover, and re-triage could not report the link. (b) GitHub's "Resolve conversation": it exists only on **review** threads anchored to a file and line. `gh pr comment` posts to the conversation timeline, which has no resolve state and no threading at all, and plenty of findings have no owning line to anchor to. Neither is a substitute for a line in the body. -->

### Two fields `manual-qa` hands over

A finding written by the driver carries two fields worth **consuming rather than re-deriving**:

| Field | Example | Use it for |
|---|---|---|
| `**From:**` | `**From:** #75 #80` | the **owning slice**, lifted by `manual-qa` from the `(#N)` suffixes on the commits the flow exercises — no derivation from the Closes map |
| `**Step:**` | `**Step:** flow 3 ("search and filter"), sub-step 2` | **pass provenance**: which flow of the pass, and which sub-step of it, failed. No permalink — the pass is composed in `manual-qa`'s session and posted nowhere, so there is nothing to link to |

**Both are absent on an ad-hoc finding**, which has no flow and no attribution. That is the normal case for a pasted finding, not a defect in it: fall back to the PR's Closes map for the owning slice (step 3), and say the finding has no pass provenance rather than inventing one.

## Cadence (one finding per turn — clone of grill / `manual-qa`)

For each finding: **capture → validate (gap classification) → investigate (subagent) → dispose → show card → user confirm/correct → next.** Loop until the user says done, then **board → publish**. Never batch.

## Per-finding process

### 1. Capture

Record the finding + its source (PR comment permalink, `file:line`, author). **`manual-qa` already did the classification + hypothesis + evidence — inherit them as the warm start; do not re-derive.** Same for the two handover fields: `**From:**` is the owning slice and `**Step:**` is the pass provenance, both taken as written. Hold the comment's **permalink** for the whole finding — publishing writes `**Triaged:** #N` back to it.

### 2. Validate + gap classification (HARD GATE — before filing anything)

`manual-qa` labels root cause as *hypothesis*. triage's first job is to decide what the finding **is**, using the loaded decision context. Resolve from PRD/issues/CONTEXT/code before asking the user:

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
- **Warm start:** hand it `manual-qa`'s hypothesis + `file:line`. Its job is **confirm + plan**, not discover-from-scratch.
- **Job:**
  1. **Confirm the root cause** on the current branch — trace the call path; for a contract-boundary finding, re-run the decisive `curl` against the live endpoint.
  2. **Attribute to the owning child slice** — always. **Where the finding carries `**From:**`, that *is* the attribution**: `manual-qa` lifted it from the `(#N)` suffixes on the commits the failing flow exercises, so take it as given and say you took it from the field. Derive from the PR's **Closes map** only when the field is absent (an ad-hoc finding), and say that too — the two are not equally authoritative, and a silent re-derivation can disagree with the field without anyone noticing.
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

- **Dedupe against the tracker** — `gh issue list --search "<keywords>" --state all` (right repo) before filing; a match makes this a `reject (duplicate)` pointing at it. **This search is no longer what catches a finding an earlier triage pass already promoted** — the `**Triaged:**` skip in `## Input` does that, without an API call, before this finding ever reaches the cadence. What is left for the search is the genuine case: a finding that duplicates an issue filed by some *other* route (a planned child, a hand-filed bug, a finding from a different PR).
- **Route** per the table below.
- **Mark the finding comment triaged.** Every disposition that ends in an issue number — a new bug, a deferred follow-up, an existing issue linked under *already planned*, a filed-then-closed reject, or a contract-boundary issue in the related repo — writes `**Triaged:** #N` back onto the finding comment once that number exists. That happens at publish (see *Marking the finding comment triaged*); what step 4 owes is knowing **which number** the line will carry. The one disposition that writes nothing is a finding closed out with no issue anywhere — *intentionally deferred, cited from the PRD or a code comment* — which has no number to point at and will surface again on the next pass. That is deliberate: a marker with nothing to link to would be worse than re-reading a one-line citation.

<dispositions>
| Kind | Title | Where | Labels | Picked by work-on-prd? |
|---|---|---|---|---|
| **Merge-blocker** | `[BUG] …` | this repo, linked as a sub-issue of PRD `#N` | `bug` + `ready-to-start` | yes — on the PRD branch, before merge |
| **Deferred / follow-up** *(after user OK)* | `[BUG] …` | this repo, linked as a sub-issue of PRD `#N` | `bug`/`enhancement` + `deferred` | no (not `ready-to-start`) — a known follow-up |
| **Contract boundary** | their style | **related repo**, "Discovered via …#PR" | `bug` (their style); local `blocked-external` pointer under the affected child's `## Blocked by` | n/a — no cross-repo auto-close; closed by hand |
| **Reject** (WAD / dup / invalid) | `[BUG] …` | this repo | file-then-close `duplicate`/`wontfix`/`invalid` + one-line rationale (cite the decision) | — |
</dispositions>

**An already-triaged finding gets no row here, because it never reaches this table.** The skip in `## Input` happens before the cadence: nothing is filed, nothing is closed, and it is not a `reject (duplicate)` — a reject is a *disposition of a finding being triaged*, and a skipped one is not being triaged at all.

Two things make a this-repo issue pickable, and both are required: the **sub-issue link** to
the PRD (what makes it a child at all) and the `ready-to-start` label (eligibility). A deferred
follow-up still gets the link — it is a real child, just not yet pickable, and an unlinked bug
is invisible to the promotion path however it is titled. The `[BUG]` prefix is a scanning
convention on top of that, not a filter. A related-repo issue takes **that** repo's title
convention, not this one's; the prefixes are a per-adapter fact and the other side has its
own.

### 5. Show the card, confirm, next

```
QA-<n>  [<classification> · <severity> · <disposition> → <label>]
Finding: <one-line symptom>
Owning slice: #<child> (<what that slice built>)
Root cause: CONFIRMED — <cause>; <path>:<lines>
Commit: <sha — only if a regression; else "n/a (introduced by the feature slice)">
Disposition: <repo + the PRD it links under + title prefix>
```

Print the card + recommended disposition, get confirm/correct, ask for the next finding.

## Board + publish

When the user says done:

1. **Board** — every finding with verdict / owning slice / disposition / target repo. Get approval before publishing.
2. **Publish** with `gh` (let it resolve the repo; use `--repo` for related-repo issues). Open issues for bugs/follow-ups; file-then-close for rejects. Follow-ups only if the user already said yes in step 2 of that finding.

   Every `[BUG]` filed **in this repo against a PRD** is then linked to that PRD as a **native
   GitHub sub-issue** — see *Linking a bug to its PRD* below. This applies to
   merge-blockers and deferred follow-ups alike (both are real children), and **not** to
   related-repo issues: an issue in another repo is not a sub-issue of a PRD here, and not to
   rejects, which are closed rather than parented.

   Then the `**Triaged:** #N` line **goes back onto the finding comment** the issue came from — see
   *Marking the finding comment triaged* below. That happens for every finding that came off
   the PR, including a reject; a pasted ad-hoc finding has no comment to write to.
3. **Report** created issue numbers grouped by disposition + repo, e.g.
   `ready-to-start: #61 #62 · deferred: #63 · <related repo>#NNN · closed: —`, plus a line for
   anything **skipped** as already-triaged and the issue each already points at.
4. **Remind** the human of the one external step triage can't do: the related-repo issue is tracked but **not** auto-closed by this repo's PR. Marking findings triaged is no longer on this list — step 2 writes `**Triaged:** #N` itself, and that line is what makes the next pass skip them. What is still worth saying out loud is any finding that ends with **no** issue at all (deferred-by-design, cited): it carries no marker, so the next pass will surface it again.

### Marking the finding comment triaged

One line, appended to the `### [FINDING]` comment, naming the issue it became:

```
**Triaged:** #92
```

**This is the only place in the chain where the finding → issue link is written down.** `triage` links the issue *up* to the PRD as a sub-issue, and nothing else links back down to the finding that produced it — so without this line a second pass has no way to tell a fresh finding from one it promoted last week.

**No contract amendment is needed for it.** The finding comment is `manual-qa`'s own artifact, authored by the same user, and carries no never-edit rule. Nothing on the PRD does either any more: the loop posts no QA comment, and `manual-qa`'s receipt is free-form output that nothing reads back.

Mechanics — the same operation class as `manual-qa`'s failure suffix, and the same rules apply:

1. **Get the REST comment id from the permalink, not from the API's `id` field.** `--json comments` returns the **GraphQL node id** (`IC_kwDO…`); passing it to `gh api` does not 400, it **404s**, which reads as "no such comment". The REST id is the numeric tail of the `url` you already have — `…/pull/91#issuecomment-5078204371` → `5078204371`. A PR's conversation comments are **issue** comments, so the endpoint is `…/issues/comments/<id>`.
2. **Fresh `GET` immediately before the write** — never `PATCH` from a body held in context since the session began.
3. **Pure append**: the fetched body, then a blank line, then the one line. Nothing else is touched, nothing is re-rendered from a model-held structure, and the existing fields keep their exact text.
4. **Read the `PATCH` response back** and confirm the line is there before moving to the next finding. `PATCH` returning is not evidence the write landed.

```bash
gh api repos/<owner>/<repo>/issues/comments/<comment-id> --jq .body > <scratch>/finding.md
printf '\n**Triaged:** #92\n' >> <scratch>/finding.md
gh api repos/<owner>/<repo>/issues/comments/<comment-id> -X PATCH -F body=@<scratch>/finding.md --jq .body
```

For a contract-boundary finding the number is the related repo's, written in full — `**Triaged:** <owner>/<repo>#123` — plus the local `blocked-external` pointer if one was filed. The skip in `## Input` keys on `**Triaged:**` alone, so any of those forms suppresses a re-triage.

### Linking a bug to its PRD

Right after filing a `[BUG]` in this repo against a PRD, link it to that PRD as a native
sub-issue, and confirm the link landed before you file the next bug. Three calls per bug:

```bash
# 1. Resolve the bug's INTERNAL numeric id — not its issue number
id=$(gh api repos/<owner>/<repo>/issues/<bug-number> --jq .id)

# 2. Write the link
gh api repos/<owner>/<repo>/issues/<prd-number>/sub_issues -X POST -F sub_issue_id="$id"

# 3. Read the PRD's sub-issues back and confirm <bug-number> is in the list
gh api repos/<owner>/<repo>/issues/<prd-number>/sub_issues --jq '.[].number'
```

**`sub_issue_id` takes the internal numeric issue `id`, never the issue number.** There are
three plausible-looking values for one issue and only one of them works:

| Value | Where it comes from | What happens |
|---|---|---|
| **Internal numeric `id`** | `gh api repos/<owner>/<repo>/issues/<n> --jq .id` | correct — the only one the endpoint accepts |
| Issue number (`<n>`) | the thing you have in hand | bare `404 Not Found` — **indistinguishable from "that issue does not exist"** |
| GraphQL `node_id` | `gh issue view <n> --json id` | wrong value; the `id` field there is the base64 node id, not the REST `id` |

So when a link call 404s, suspect this before you suspect a missing issue.

Two rules, both non-negotiable:

- **Verify every link after writing it** (step 3 above) and report it — one line per bug naming
  the bug and that it now appears under the PRD. `POST` succeeding is not evidence the bug is
  parented; reading the PRD's sub-issue list back is. **The link is the only thing discovery
  reads** (`../_shared/prd-eligibility.md`), and the body carries no `## Parent` section to fall
  back on — there is no text-search safety net, so a silently failed link is an invisible child.
- **Write links one at a time — never fan them out.** File → link → verify one bug, then start
  the next. GitHub warns that creating or removing sub-issues "too quickly" trips secondary rate
  limiting, and publishes no threshold to aim under.

Use `gh api` for this. Do **not** use `gh issue create --parent`: that flag needs
`gh >= 2.94.0`, this machine runs `2.89.0`, and `gh api` works on both.

**Scope: this repo's PRD children only.** A contract-boundary issue filed in a related repo is
not a sub-issue of a PRD here — skip the link entirely and leave the `blocked-external` pointer
issue as the only local trace. A reject is filed-then-closed, not parented, so it gets no link
either.

## Issue template (mirror the `to-issues` child so work-on-prd eats it identically)

```
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

Title: **`[BUG] <one-line symptom>`**.

`[BUG]` is **shorthand for the adapter's *Title prefixes* row** at
`<repo-root>/.claude/project/adapter.md`, written out for readability; if that row names a
different prefix, it wins. Nothing filters on it — the sub-issue link is what makes a bug a
child — so the prefix is a human scanning convention: a triaged finding reads as one in the
issues tab, next to the `[TASK]`s it sits among.

Severity = technical impact, independent of priority; both live in the issue body (no GitHub
labels for them).

## Boundary / handoff

- triage = **investigate + decide + file**. It does **not** fix, and it does **not** need a separate "fix the bugs" skill: a bug filed in this repo, **linked to that PRD as a native sub-issue** and labelled `ready-to-start`, **is a PRD child** — `work-on-prd` (re-entrant, cold-start) discovers it from the PRD's sub-issue list and works it on the PRD branch with no new machinery. Those two are the whole requirement; the `[BUG]` title prefix is a scanning convention and changes nothing about discovery. The link is what makes it a child at all: a bug filed but never linked is invisible before eligibility ever runs. See `../_shared/prd-eligibility.md`.
- Deferred (`deferred` label) issues sit as known follow-ups until promoted (relabel `ready-to-start`).
- Related-repo issues are executed by that repo's own `work-on-issue`.
