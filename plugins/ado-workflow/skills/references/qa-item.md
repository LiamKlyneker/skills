# The `[QA]` work item

What an orchestrated `work-on-spec` run produces at loop end so a human can run verify-ladder
**L5** against the branch before the pull request completes. Cited by `ado-workflow:work-on-spec`
at its `## Loop end`.

The plugin carries this file so the pointer resolves from inside any of its skills
(`../references/qa-item.md`) and from a marketplace install cache alike — no skill borrows a
reference out of a sibling skill's directory.

Its only consumer is the person running QA. **No skill parses it**, and nothing ever reads a
previous run's `[QA]` item, so "normative" here means the section order, the sources and the
earning rule are fixed — not that a parser depends on the wording.

The Azure DevOps **mechanics** — creating the work item, parenting it, composing the title, id
syntax, the HTML-escaping trap, and the linked-work-item lever — are `work-on-spec`'s and stay
at the call site. This file is the shape of the item.

## One per run, never one per `[SPEC]`

A run covers exactly the slice of `[TASK]`s that just landed. A second run against the same
`[SPEC]` creates a **second** `[QA]` work item and **never edits the first**.

This is the whole point of an item rather than a committed document. A document at a fixed path
accumulates every run's output, goes stale silently, and gives the human no way to tell which
half they already tested. A per-run item describes one testable slice, and it is closed by the
human once tested.

## What earns a step

**A landed `[TASK]` earns a step only if a human can exercise it in the running app.**

Dependency bumps, config changes, pure refactors, internal-only work and setup contribute
**nothing**: no step, and **no standalone "nothing to test here" line, paragraph or section**.
Those lines are the entire reason the committed QA documents this replaces reached 440 lines —
every landed item earned a section whether or not anybody could act on it, so the sections that
mattered were buried among the ones that didn't.

Such a `[TASK]` still gets its **one line in `## What landed`**, so a reader can see it shipped
and does not go hunting for the step it never had. That line may carry a short parenthetical —
`(nothing to test by hand)`, a few words, inline — and that is the *only* form the idea is
allowed to take. The moment it becomes its own line or section, the rule has been broken.

Applied honestly, most runs produce a `[QA]` item far shorter than the list of things they
landed. That is the intended shape, not a sign something was missed.

## Nothing testable in the whole run → create no item at all

If **no** `[TASK]` in the run produced anything a human can exercise, create **nothing**. An
empty `[QA]` item is worse than none: it is a thing a person has to open, read and close in
order to learn nothing.

Say so explicitly, in both places the item would otherwise have been named:

- the **final summary** — "no `[QA]` item: nothing in this run is manually testable", plus the
  list of `[TASK]`s the run landed;
- the **pull-request body**, where the `QA:` line would have gone — the same sentence.

Silence in either place reads as a forgotten step rather than a decision.

## The body

<qa-template>

<one line of run context: the `[SPEC]`, the pull request, how many `[TASK]`s landed>

## What landed

- <id> — <one line on what shipped>
- <id> — <one line>  (nothing to test by hand)

## Before you start

- <the thing that will look broken and is not, and why>

## Steps

1. <action to take in the running app> → expect <the observable result>  (<id>)
2. <action> → expect <result>  (<id>)

## Gotchas

- <edge case or deviation a worker flagged, and what it means for the tester>  (<id>)

</qa-template>

The rules below govern that template and are deliberately written **outside** the fence. Copy
the fence, not this prose — instructions pasted inside a body template ship to the reader as
work-item text.

- **`## Before you start` is conditional.** Include it only when something will look broken and
  is not — a dangling symlink a later `[TASK]` repairs, a migration the tester has to run first,
  a feature flag that is off. **Omit the heading entirely** otherwise. A "None" under it is the
  440-line habit in miniature.
- **`## Gotchas` is conditional** the same way. No deviations and no flagged edge cases means no
  heading.
- **`## What landed` and `## Steps` are always present** — a `[QA]` item exists because at least
  one `[TASK]` earned a step, so both always have content by construction.
- **Steps are numbered continuously across the whole run**, in the order a human would sit down
  and work through them, not grouped by `[TASK]` and not restarted per section.
- **Every step carries the id of the `[TASK]` it came from**, so a failure routes straight back
  to the work item that caused it.
- **Every step states an expected observable result.** A step whose expected result is "it looks
  right" is not a step — either name what the tester should see, or the change did not earn a
  step in the first place.

## Built from two sources, and only two

1. Each worker's **refined QA notes** — item 4 of the report contract. These are the steps. The
   `[TASK]`'s own `## QA notes` are what the worker refined, not a second source to merge back
   in.
2. Each worker's **deviation log** — item 3 — and the edge cases it flagged. These are the
   gotchas, and they are what `## Before you start` is built from when it appears at all.

Nothing else. Not the `[SPEC]`'s body, not the `[TASK]`s' acceptance criteria, not the diff. A
`[QA]` item assembled from the artifacts instead of the reports describes what was *planned*;
the reports are the only record of what was actually built.

## It must survive the pull request

The `[QA]` item is the gate the merge passes **through**, so nothing about completing the pull
request may close it. A QA pass that marks itself done the moment the branch lands is
indistinguishable from one a human ran, and it is silent — the failure surfaces only as nobody
ever having tested the release.

The invariant: **the item is closed by the human who ran it, and by nothing else.**

On this tracker the lever is the **linked-work-item list**, and it is armed by default — a pull
request's completion options transition every linked work item and `transitionWorkItems`
defaults to `true`. So the `[QA]` item is never attached to the pull request; `work-on-spec`'s
`### 2. Pull-request body` states the mechanism in full, including the `workItems` argument on
the create call that is the easiest way to attach one without noticing.
