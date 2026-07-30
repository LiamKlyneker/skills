# ADR 0003 — Invocation is the isolation boundary

- **Status**: Accepted
- **Date**: 2026-07-30
- **Context**: PRD #52, implemented by #54

## Context

Packaging decides where a skill *comes from*. It does not decide whether the model may
fire it on its own. Those are separate axes, and conflating them produces a specific bad
outcome: a skill that writes to a tracker auto-invoking in a session wired to a different
project, which is a write to the wrong tracker with no human in the loop.

Before this PRD, invocation had been decided ad hoc — `grill` and `deep-grill` carried
`disable-model-invocation: true` because someone thought about it once, and everything
else was model-invoked because that is the default.

## Decision

**Every skill in this repo is either user-invoked or model-invoked, and which one is
decided by a rule rather than per skill.** Isolation is enforced by **invocation**, not by
packaging.

The test, applied in both directions:

- **It drops to user-invoked** (`disable-model-invocation: true`) if it **writes to a
  tracker**, or if it is a **run-once bootstrap**. Both are actions whose cost of firing
  unasked is much higher than the cost of not firing — a stray comment on someone else's
  PR, or a project's adapter rewritten out from under it.
- **It stays model-invoked** if it is a **guardrail**. A guardrail you have to remember to
  invoke is not a guardrail; it is a suggestion. Anything whose entire value is catching
  the case you did not notice has to be able to fire without being asked.

## The two sides, as of #54

| Skill | Invocation | Why |
|---|---|---|
| `qa-prd-log` | user-invoked | writes findings as comments on a PR |
| `triage-prd` | user-invoked | files GitHub issues |
| `install-skills` | user-invoked | run-once bootstrap; writes a project's adapter |
| `grill` | user-invoked | already was, before this PRD — unchanged |
| `deep-grill` | user-invoked | already was, before this PRD — unchanged |
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

## The mechanism, measured

The flag is not advisory. A fresh session asked to list every skill it could invoke
matching those names returned `lk:how-i-write` and `lk:pinpoint`, and stated explicitly
that the other three were **not in its skill list**. The same probe run before #54 had
returned `install-skills:install-skills`.

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
