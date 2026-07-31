# ADR 0004 — `_shared/` files are shared; skills are not

- **Status**: Accepted — a standing difference with prior art, with no end date
- **Context**: PRD #52 `## Further Notes`; the hard/soft rule applied in #55, enforced in #58

## Context

[`mattpocock/skills`](https://github.com/mattpocock/skills) forbids cross-skill file
references outright. This repo depends on them deliberately. Both rules are right, for
different repos, and this record exists so that neither gets "fixed" into the other.

`_shared/` holds eight documents. All five plugins carry a `skills/_shared` symlink to it;
four of them actually read documents from it today (`figma-tools` reads none, and keeps the
link for uniformity):

| Document | Read from |
|---|---|
| `_shared/model-effort-heuristics.md` | three plugins — `prd-workflow` (3 skills), `ado-workflow`, `lk` |
| `_shared/eligibility-policy.md` | `ado-workflow` directly, and transitively by `prd-workflow` and `lk` via the two dialect docs below |
| `_shared/prd-eligibility.md` | `prd-workflow` (3 skills) and `lk`'s `triage-prd` |
| `_shared/ado-eligibility.md` | `ado-workflow` (3 skills) |
| `_shared/ui-manifests.md` | the stack-neutral row schema, read by the skills that build those tables |

`eligibility-policy.md` is the clearest case this record's rule was written for. It is the
tracker-neutral core — eligible = open ∧ every blocker done, cycle detection, picking order,
never batch — and `prd-eligibility.md` and `ado-eligibility.md` are its two tracker dialects,
carrying only the `gh` and Azure DevOps mechanics that genuinely differ. The two loops decide
what to work on next by two entirely different sets of calls, but *what makes an item eligible
to start* is one argument. Three copies of it would have been three copies of that argument,
drifting apart with no test to catch them. As it stands, three of five plugins depend on one
file's definition.

(This paragraph used to cite `_shared/qa-item.md`, which was the same case until the two
trackers' QA rules stopped being one argument and the file was dissolved — ADR
[0006](0006-sub-issues-and-qa-as-a-prd-comment.md). The example moved; the rule did not.)

## Why the rules differ, rather than either one changing

**His constraint is correct for his shape.** A flat collection of independent skills, each
installed on its own, has no owner for a cross-reference: skill A reads a file belonging to
skill B, B gets edited or is not installed at all, and A degrades with no signal. Banning
the reference removes a whole class of invisible coupling at almost no cost, because in a
flat collection there is rarely anything genuinely common to share.

**This repo's shape is different.** It is five plugins, two of which are the *same
workflow* over two different trackers, plus a personal plugin that reuses pieces of both.
Three plugins needing one copy of the eligibility rule is a problem he does not have. The
alternative to sharing is three copies, and the copies would drift — silently, because the
thing that drifts is prose an agent executes rather than code a test covers. A `_shared/`
document is not one skill reaching into another's territory; it is a reference with a
single owner that several skills read.

## What makes the reference unambiguous is the layout, not a warning

**No project ever owns a `_shared/`.** Project facts live in
`<repo-root>/.claude/project/` instead. That single rule is what makes `../_shared/x.md`
from any skill mean exactly one thing — this repo's global reference — regardless of which
project the session is running in or which route the skill arrived by.

Inside a plugin the path is `skills/_shared`, a symlink to the one canonical directory,
which install dereferences into the cache copy. That copy is a regenerated build artifact,
not a project-side fork, and it does not make a project-owned `_shared/` any less of a
problem.

Because the layout removes the ambiguity, the skills carry **no** "you may have resolved
the wrong file" hedging, and must not grow it back. A hedge would be a worse version of the
guarantee the layout already gives.

Two mechanical checks in `.github/scripts/validate_skills.py` keep it honest:

- `check_shared_references()` fails any `../_shared/x.md` pointer that does not resolve. A
  dead pointer silently drops guidance, which is the same failure class as drift.
- **A symlink from one plugin into another is rejected.** Install would dereference it and
  publish one plugin's files inside another, so one edit would change two published
  plugins. Sharing goes through `_shared/`, which has one owner, or it does not happen.

## The price, and where it is paid

The version-bump gate (ADR
[0001](0001-version-the-plugins-and-enforce-the-bump.md)) counts a change under `_shared/`
as a change to **every** plugin that symlinks it, because install dereferences the link
into each cache copy — the edit really does change what those plugins publish, even though
`git diff` only ever names `_shared/…`. So one shared-doc edit demands up to five version
bumps. Demonstrated: editing `_shared/ui-manifests.md` made the gate demand a bump from
all four other plugins.

That is the honest cost of keeping one copy, and it is where the two ADRs meet. It is
accepted because the failure it replaces has no symptom: a shared-doc change that ships to
nobody, with a green build and a maintainer who believes it landed.

## The other half of the rule: hard vs soft dependencies

Taken from `mattpocock/skills` ADR 0001 and adopted here unchanged: **a skill names another
skill only where its output would be *wrong* without it.** Anything weaker than that is a
soft dependency and must not be written as a requirement.

This is not in tension with sharing files — it is the reason sharing files is the *only*
form of sharing allowed:

- A `_shared/` document **ships with the plugin**, dereferenced into the cache copy. A
  reference to it cannot fail on a consumer's machine.
- A skill in another plugin **does not ship with it**. Naming it asserts that the reader
  has installed something they may not have, and the assertion fails at read time with no
  error.

Applied in #55, and this is what the abstract rule looks like in practice: `to-spec`,
`to-prd`, `_shared/ui-manifests.md` and `prd-workflow`'s README all named
`grill-me`/`deep-grill` as hard dependencies. Nothing links a grill into the Schmiede
config at all, and `to-prd` has no business caring which skill produced its input — it
needs a resolved discussion, not a particular tool. Each reference was made skill-agnostic
while keeping the substance: `to-spec`'s abort message stopped saying "run
`/grill-me <work-item-url>`" and started saying that the design interview has to have
happened. `_shared/ui-manifests.md` kept the actual reasoning — that two skills resolving
the same manifest is two sources of truth — and dropped the names.

The soft direction is fine and stays: a grill may name the workflow it feeds, because
being wrong about that costs a suggestion rather than a broken skill.

## Why this one is an ADR

Because it is a **standing disagreement**, not a decision that will be settled. Both rules
stay true in their own repos indefinitely, and the reason to write it down is that the
difference looks like a defect from either side — a reader coming from his repo sees a
banned pattern in daily use here, and a reader here sees a needless restriction there.

If the two ever have to reconcile, that is a new record superseding this one. Not an edit
to this file.
