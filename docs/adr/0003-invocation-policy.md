# ADR 0003 — Invocation is the isolation boundary

- **Status**: Accepted
- **Date**: 2026-07-30
- **Context**: PRD #52, implemented by #54

## Context

Packaging decides where a skill *comes from*. It does not decide whether the model may
fire it on its own. Those are separate axes, and conflating them produces a specific bad
outcome: a skill that writes to a tracker auto-invoking in a session wired to a different
project, which is a write to the wrong tracker with no human in the loop.

Before this PRD, invocation had been decided ad hoc, and in more places than the PRD
noticed. **Three** skills already carried `disable-model-invocation: true` — `grill`,
`deep-grill`, and `figma-tools`' `figma-to-spec`, which has had the flag since
`a0c7b04` and was never touched by this branch — plus `scoped-context` on the inverse
flag. So four of eighteen skills had a deliberate invocation decision; the other
fourteen were model-invoked because that is the default, not because anyone chose it.

`figma-to-spec` matters to this record precisely because nobody coordinated it: a third
skill, in a different plugin, was reasoned to the same conclusion independently, a week
before the policy existed. That is evidence the rule was already latent in the repo
rather than invented for it.

## Decision

**Every skill in this repo is either user-invoked or model-invoked, and which one is
decided by a rule rather than skill by skill.** Isolation is enforced by **invocation**,
not by packaging. (The rule does not yet explain every existing case — the gap is named
below rather than papered over.)

The test, applied in both directions:

- **It drops to user-invoked** (`disable-model-invocation: true`) if it **writes to a
  tracker**, or if it is a **run-once bootstrap**. Both are actions whose cost of firing
  unasked is much higher than the cost of not firing — a stray comment on someone else's
  PR, or a project's adapter rewritten out from under it.
- **It stays model-invoked** if it is a **guardrail**. A guardrail you have to remember to
  invoke is not a guardrail; it is a suggestion. Anything whose entire value is catching
  the case you did not notice has to be able to fire without being asked.

## The skills the policy speaks to

Nine of the eighteen skills across the five plugins — which is exactly everything outside
the two workflow plugins. Seven of the nine carry an explicit invocation flag; the last two
are deliberate keeps, listed because they would otherwise read as oversights.

The other nine — every skill in `prd-workflow` and `ado-workflow` — are model-invoked **by
design, not by omission**: they are the loop, and a loop step you have to remember to type
is not much of a loop. Handing `work-on-prd` a PRD and having it reach `next-prd-issue` on
its own is the entire product. None of them is a candidate for the drop test, even though
most of them write to a tracker, because a tracker write inside a loop the user started is
the thing they asked for.

| Skill | Invocation | Why |
|---|---|---|
| `qa-prd-log` | user-invoked | writes findings as comments on a PR |
| `triage-prd` | user-invoked | files GitHub issues |
| `install-skills` | user-invoked | run-once bootstrap; writes a project's adapter |
| `figma-to-spec` | user-invoked | pre-existing, since `a0c7b04` — files an ADO `[DESIGN-SPEC]` and escalated gaps as PBIs in its Phase D |
| `grill` | user-invoked | pre-existing — see the gap below; it writes nothing anywhere |
| `deep-grill` | user-invoked | pre-existing — same |
| `pinpoint` | model-invoked | a cheap read-only lookup; useful precisely when unprompted |
| `how-i-write` | model-invoked | guardrail — the failure it prevents is drafting in a generic assistant tone, which nobody thinks to ask about |
| `scoped-context` | model-**only** | guardrail — it exists to read a `CONTEXT.md` before an edit that was already going to happen |

The three that moved in #54 are `qa-prd-log`, `triage-prd` and `install-skills`. The flag
is placed after `description`, matching `grill`/`deep-grill`'s prior art.

**`scoped-context` is the inverse case and must not be described as the same one.** It
carries `user-invocable: false`, not `disable-model-invocation: true` — model-only rather
than user-only. There is nothing useful to type: its whole job is to fire on its own
before a file is modified. It is in the table because the policy has to answer for it, not
because it moved.

## Where the test is incomplete, stated rather than hidden

The two drop clauses were derived from the three skills #54 moved, and they hold up
against a case nobody consulted: `figma-to-spec` files ADO work items in its Phase D, so
**the tracker-write clause predicts it correctly** — the flag it has carried since
`a0c7b04` is what the policy would have assigned anyway.

They do **not** predict `grill` and `deep-grill`. Neither writes to a tracker; neither
writes anything at all. They are interviews, and what actually justifies the flag on them
is a third property the policy never wrote down: **they seize the conversation.** An
interview that begins unasked is indistinguishable from a malfunction, and there is no
"cost of not firing" to weigh against it because the user was going to type the command
that instant anyway.

So the drop test as stated is two clauses covering four of the six user-invoked skills.
That is a gap in the policy, not a gap in the table, and it is recorded here rather than
patched into the rule — a third clause invented inside an ADR would be law nobody agreed
to. Whoever needs it can add it, at which point this record is superseded rather than
edited.

## The mechanism, measured

The flag is not advisory. A fresh session was asked to list every skill it could invoke
matching the five names #54 touched or deliberately left alone — `qa-prd-log`,
`triage-prd`, `install-skills`, `how-i-write`, `pinpoint`. It returned `lk:how-i-write` and
`lk:pinpoint`, and stated explicitly that the other three were **not in its skill list**.
The same probe run before #54 had returned `install-skills:install-skills`.

So `disable-model-invocation: true` demonstrably removes a skill from the model's list
while leaving it typeable. That is the mechanism the whole policy rests on, and it was
checked against a real session rather than assumed from the field name.

## Consequence: user-invoked descriptions lose their triggers

A user-invoked skill's `description` stops being a trigger, because there is nothing left
to trigger. The three descriptions changed in #54 dropped their "Use when the user says
…" tails and now close by naming what to type — `/lk:qa-prd-log`, `/lk:triage-prd`,
`/install-skills:install-skills`.

This is recorded here, as a **consequence of the policy**, rather than as a separate
prose-style rule to remember. Trigger phrasing on a skill the model cannot invoke is dead
text that still costs always-on tokens in every session, and the only reader left is the
human deciding whether to type the command. Deriving it from the invocation decision means
it cannot be forgotten independently: whoever flips the flag has already been told what to
do with the description.
