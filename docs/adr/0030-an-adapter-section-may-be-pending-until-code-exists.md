# ADR 0030 — An adapter section may be Pending until code exists

- **Status**: Accepted
- **Date**: 2026-11-21
- **Context**: PRD #345, from the `[IDEA]` #342

## Context

A repo that starts from a brainstorm holds a README and a first issue, and no code. The
`prd-workflow` and `ado-workflow` bundles declare `## Commands`, `## App facts` and
`## Verify ladder`, and on that repo none of the three has an answer yet. There is no manifest,
script or test suite to read, and the human does not know the answers either, because the stack
is an output of the grill that has not run.

The installer had no rule for this state. The interview asked questions with no answer, or the
sections kept their template placeholders and `doctor` reported `UNFILLED` on every run with no
route forward. The window that matters runs from "stack chosen" to "first code merged": the
first skill that needs a code section is `to-prd-tasks`, which copies the verify command into
each slice, followed by the workers that run L2.

## Decision

**An adapter section may be Pending.** When the interview's inference finds nothing for the
three code sections, `setup` asks one confirmation — *"No manifest, scripts or tests yet — is the
stack still undecided?"* — and on yes writes this literal as the whole body of each:

```
Pending: this repo has no code yet. Run /<plugin>:setup again after the first code lands.
```

`<plugin>` is the plugin whose `setup` wrote it. The adapter is then in **Pending mode**.
`doctor` reports each such section `PENDING`, as a warning and never as `UNFILLED`. Every skill
that reads the adapter tells the user it is in Pending mode, says whether that blocks the current
step, and names the command that leaves it. The rules live in
[`install/setup.md`](../../install/setup.md) steps 3 and 4 and in
[`install/interview.md`](../../install/interview.md).

### Only the three code sections

`## Commands`, `## App facts` and `## Verify ladder` are the sections whose answer is read from
code. Every other section has a true answer on a repo with no code: `## Project gates` defaults
to None, "nothing yet" is a true answer for `## Repo discipline`, and `## Repo` comes from the
tracker. Allowing the marker anywhere else would let a section that has an answer skip it, and
gap-fill never revisits a filled section, so that answer would never be asked for.

The existing rule that a repo with no test suite is a legitimate `## Verify ladder` answer stays
as it is. It records a permanent fact. Pending records a temporary one, with a named exit.

### The second never-delete exception

`setup` never overwrites an existing adapter; the fresh-copy exception in `install/setup.md` was
the only one. Pending mode adds a second. A section whose whole body is exactly the `Pending:`
literal is a gap, and a later `setup` run replaces it with real content. Any other content in
that section — a line added under the marker, an edited marker — makes it the project's own
work, and `setup` stops and asks.

The exception is safe for the same reason as the first: nobody filled the marker in. `setup`
wrote it, so replacing it destroys no one's work. Without the exception, leaving Pending mode
would need a hand edit that nothing prompts, and `doctor` would warn on every run after the code
exists.

### The literal is a parse contract, hardcoded

The installer, `doctor` and every consumer skill match the same literal. It is hardcoded in each
of them and never registered in the adapter, for the reason `### [FINDING]` is: a project free to
edit the marker would get consumers that silently stop recognising it, and a Pending adapter read
as a filled one sends a worker to run a verify command that does not exist. A fixed literal
also keeps the second never-delete exception exact: "the whole body is this string" is a check,
where "the whole body looks like a marker" is a judgement.

## Considered and dropped

**Option 2: consumers tolerate a partial adapter, with no marker.** Each skill would treat a
missing or placeholder-filled code section as "no code yet". Dropped because nothing could then
tell a repo with no code from an adapter someone forgot to fill. `doctor` would have to stop
reporting `UNFILLED` for those sections or keep reporting it forever, and a later `setup` run
could not tell a gap it may fill from a section a human half-wrote. The marker makes the state
explicit, written by one party and recognised by all of them.

**A repo-level "no code" interview mode.** Dropped for detection per section: the question is
asked only when the inference finds nothing for the three sections, so a prose-only repo with no
manifest still gets the normal interview when the human answers no.

**A worker writing the adapter once the scaffold lands.** Dropped: no worker writes the adapter.
The second `setup` run fills all three sections from the scripts that now exist.

## Consequences

- Existing projects see no change. Every new behaviour triggers only on the literal, which only
  the new `setup` writes.
- `doctor` gains the `PENDING` warning code, documented in the status table in
  `install/setup.md`.
- The literal now has several copies across the installer and the consumer skills. A drifted copy
  stops matching silently, so the copies are a validator's to keep identical, not a reviewer's.
