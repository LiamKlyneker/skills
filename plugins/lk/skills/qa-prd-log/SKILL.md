---
name: qa-prd-log
description: Capture manual-QA findings for a specific PRD/PR one at a time during a testing pass — confirm, classify, route, and post each as a self-contained comment on the PRD's PR. Capture only, no fixing. Invoke /lk:qa-prd-log while manually testing a PRD's build to log findings one-by-one against its open PR.
disable-model-invocation: true
---

# qa-prd-log

Log what you find while **manually testing one PRD's build** — **one finding at a time** — as self-contained comments on that PRD's PR. This is the *capture* phase of a human QA loop: notice → confirm → classify → route → post, then move on. Triage (promote to issues / fix) happens **later, in a separate session** via the `triage-prd` skill.

This skill is deliberately **PRD-scoped**. It loads the PRD's context first so it can tell a real bug from a decision made on purpose — e.g. a placeholder that's deferred-by-design reads as a bug on screen but is not one. (`triage-prd`, its promote-to-issues sibling, is PRD-scoped too.)

Project facts (repos, commands, verify ladder) come from the **project adapter** at `<repo-root>/.claude/project/adapter.md` — read it; never hardcode them here.

## Two non-negotiables

1. **Capture, don't solve.** See `<the-line>` for exactly where investigation stops.
2. **Every comment is self-contained.** A cold triage session (or a teammate) reads only the comment, not this conversation. Each carries: symptom, evidence, a `file:line` pointer, a labeled root-cause *hypothesis*, classification, and repro. No context that only lives in this chat.

## Context loading (once, up front)

Before the first finding, establish scope:

- **Which PRD/PR.** Ask if not given. Resolve the PR number (`gh pr list` / the branch's PR). All comments go there.
- **Read the PRD issue** (`gh issue view <n>`) — especially its cross-repo dependencies, deferred/out-of-scope notes, and explicit decisions.
- **Read the relevant `CONTEXT.md`** for the feature dir(s) under test (use the `scoped-context` skill if available — it walks up to the enclosing feature root).
- **Note what's deferred-by-design.** Skim code comments in the touched files for "deferred", "later slice", "no resolver yet", placeholder notes. This is what lets you classify a scary-looking screen as *known gap*, not *bug*.

Hold this context for the whole session.

## Cadence (one finding per turn)

The user reports a finding, usually with a screenshot. For each:

1. **Confirm it's real** — reproduce it, or run *one* quick check.
2. **Classify** — bug · deferred-by-design · works-as-intended · enhancement. Cross-check against the loaded PRD/CONTEXT before calling it a bug.
3. **Route** — which repo/layer owns it (see `<routing>`).
4. **One decisive probe** only if it changes classification or routing (see `<the-line>`).
5. **Post** a self-contained comment on the PR (see `<comment-template>`).
6. **Report back** the permalink + a one-line recap, then wait for the next finding.

Do not batch. One at a time. Loop until the user says they're done; then give a short session summary (count + one line each + all permalinks) so the later triage pass has an index.

<the-line>
## Where investigation stops

> **Investigate only far enough to classify and route — never to solve.**
> *One decisive probe, not a full investigation.*

**In bounds (do at capture):**
- Confirm the symptom (saw it, or one quick check).
- **One decisive probe** *when it changes classification or routing* — e.g. a single `curl` against the open API endpoint to prove a bug is server-side vs client-side. That probe earns its place because it routes the finding to the right repo.
- Grab the **`file:line`** where the symptom surfaces.
- Check PRD/CONTEXT/code comments for **deferred-on-purpose**.
- One **root-cause hypothesis**, clearly labeled as hypothesis, kept separate from observed facts.

**Out of bounds (defer to `triage-prd`):**
- Tracing the full call graph to pin the exact broken line.
- Reproducing many permutations beyond the one that decides routing/severity.
- Reading another repo's handler to find the precise fix.
- Writing or testing a fix.
- Spawning code-exploration subagents. If a finding needs a deep code dive just to be *understood*, that's the signal it belongs in triage-prd.
</the-line>

<routing>
## Routing (which repo/owner)

- **This-repo bug** → the finding is a real defect in the code of the repo under test. Post to the PR; triage-prd will open an issue here.
- **Contract-boundary bug** → the symptom is in this app but the cause sits on the other side of the API boundary, in the repo named by the adapter's `## Repo → Related repos`. Prove it with the one decisive probe when feasible (curl the open endpoint), and say so explicitly — triage-prd investigates over there and files the issue in that repo, cross-linked back per the adapter's `## Repo discipline`. Do **not** fix or file across the boundary from here.
- **Deferred-by-design** → not a bug. Say what was deferred, cite the code comment/PRD note, and what the follow-up slice needs. Triage decides whether to promote the follow-up.
- **Works-as-intended / enhancement** → capture the desire, mark it as not-a-defect.

If the adapter says "None" for related repos, there is no contract boundary to route to — everything is a this-repo finding.
</routing>

<comment-template>
## Comment template

Keep it lean — the canonical minimum is repro / expected / actual; the rest earns its place. Structure:

```
### <emoji> QA finding: <one-line symptom>

**Symptom:** what the user sees.

**Classification:** bug (this repo) · bug (contract boundary) · deferred-by-design · works-as-intended · enhancement
**Severity:** low / med / high   (severity = technical impact, independent of priority)

**Evidence:** the one decisive probe / screenshot description / log — the thing that removes ambiguity.

**Where:** `<path>:<line>` — where the symptom surfaces.

**Root-cause hypothesis:** *(labeled as hypothesis, separate from the facts above)*

**Repro:** numbered, exact steps.
```

- Screenshots the user pastes can't be embedded via `gh` (they're local) — describe them in words instead. If the user wants the image inline, they drag it into the comment on GitHub themselves.
- Post with `gh pr comment <n> --body-file <path>` (write the body to the scratchpad first; avoids shell-escaping issues).
</comment-template>

## Handoff to triage-prd

The PR comments are this skill's only output; a later `triage-prd` session investigates them and promotes survivors into issues.
