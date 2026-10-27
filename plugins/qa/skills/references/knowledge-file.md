# The `KNOWLEDGE.md` file

The format of a page's knowledge file: what a user sees on one page and when, what the user can do
and when, the data states behind both, and the questions nobody has answered yet. It is a tester's
file, written in user words only.

Three skills share it: **`qa:build-knowledge` is its only writer** — it derives the file, regenerates
it, and fills one answer on demand — and **`qa:setup-states` and `qa:prove-branch` read it**. The
one write `qa:prove-branch` makes is `build-knowledge`'s own update mode, applied when a developer
answers an open question during a run; it never derives or regenerates a row. This
file is the only definition of the format. No skill restates a column list; each points here
(`../references/knowledge-file.md`). No project edits the format.

## Where it lives

**One per page folder**, beside that folder's `CONTEXT.md`. Never for a component, a hook or a
sub-folder: the folder is the route, and the file is the folder's. A knowledge file belongs to a
page, not to a feature — the page outlives every ticket, and a diff that touches the page folder is
what reopens its file.

The file is tracked in the project's repository once the project adopts it. During a trial it may
sit in the repository's local exclude file (`.git/info/exclude`). **A route folder whose name
carries brackets needs them escaped in an exclude pattern**, since an unescaped bracket is a
character class: `app/\[orgId\]/plans/KNOWLEDGE.md`, never `app/[orgId]/plans/KNOWLEDGE.md`.

## Shape

A header and exactly four tables, in this order. Nothing else: no prose outside the header, no notes
section, no other heading.

```markdown
# <page name, in user words>

Route: <the page's route pattern>
Purpose: <one sentence, in user words>
Derived at: <short sha> · <YYYY-MM-DD>
Environment: <a behaviour that differs between staging and prod, stated as a fact, or `none`>
Backend read: <repo name>, <repo name> · <YYYY-MM-DD>

## What the user sees

| Section | Role | Shows when | State | Origin |
|---|---|---|---|---|

## What the user can do

| Action | Role | Allowed when | Result the user sees | Origin |
|---|---|---|---|---|

## States

| Id | State, in user terms | Env | Known account | Seeder (for a human) | Origin |
|---|---|---|---|---|---|

## Open questions

| Id | Question | Blocks | Answer | Origin |
|---|---|---|---|---|
```

### Header lines

| Line | Holds |
|---|---|
| `Route:` | the page's route pattern |
| `Purpose:` | one sentence, in user words |
| `Derived at:` | the short commit sha the derivation read and the date, as `<short sha> · <YYYY-MM-DD>` |
| `Environment:` | any behaviour that differs between staging and prod, stated as a fact ("payments on staging go to a test processor and never charge a card"). A cell saying "staging only" tells a new person nothing on its own, so the difference lives here, in full. `none` when nothing differs |
| `Backend read:` | the backend repos read and the date, as `<repo name>, <repo name> · <YYYY-MM-DD>`. **Present only when a backend read was done**; absent otherwise |

### `## What the user sees`

`Section | Role | Shows when | State | Origin`

One row per section of the page, **including loading, error and redirect behaviour**. `Role` is the
role in user words. `Shows when` is the condition in user words. `State` names the state ids from
`## States` the row needs, comma-separated, or `any`.

### `## What the user can do`

`Action | Role | Allowed when | Result the user sees | Origin`

One row per button, link, drawer, icon or keyboard action. `Allowed when` is the condition in user
words. `Result the user sees` is what changes on screen, in user words.

### `## States`

`Id | State, in user terms | Env | Known account | Seeder (for a human) | Origin`

- `Id` runs `S1`, `S2`, … with no gaps.
- `Env` is `staging`, `prod` or `both`.
- `Known account` reads `accounts.md` when that file holds a row for this page and state, or
  `none known`. It is a pointer and never a copy: the proving ids live only in `accounts.md`, whose
  format is [`accounts-file.md`](accounts-file.md). When the two disagree, `accounts.md` wins.
- `Seeder (for a human)` names the project's own data-creation command or task as a hint for a
  human, or `none known`. No skill runs it. It is the fast path for a state this app cannot make on
  its own — one set in another application, one that needs time to pass, one that needs a payment
  failure — and never a default.

### `## Open questions`

`Id | Question | Blocks | Answer | Origin`

- `Id` runs `Q1`, `Q2`, … with no gaps.
- `Blocks` names the state ids the question blocks, comma-separated.
- `Answer` and `Origin` read `—` until the question is answered. An answered question keeps its row,
  with both cells filled.

**Open questions are the honest border, not a defect.** A page answers everything about what shows
and when. The questions that remain are of two kinds only:

1. **a backend rule the page reads as a yes or no** — the page asks the API whether the user may
   cancel, and the rule behind the answer lives in a backend repo;
2. **a staging fact no repo holds** — which org on staging has a plan in that state.

A file with no open questions on a page that reads permissions from an API is a file that guessed.

## Rules for every cell

**No code words anywhere.** No file, component, hook, flag, field, capability, prop, enum, function
or status-constant names. User and product words only: "the plan is cancelled", "the paying
contact's account was deleted", "the plan still has a balance".

**Two exceptions, and only two:**

- the `Seeder (for a human)` column may name a command or task;
- the `Origin` column may name a repo.

A technical fact that has no product word is paraphrased ("the app answers 'not found'"), never
copied. A few technical words will always sit at the border between the page and its API; a short
paraphrase of one is allowed there, and a copied identifier is not.

**One fact per row.** A row that needs "and" to state two conditions for two outcomes is two rows.

## `Origin`

Every row of every table carries one origin:

| Origin | The fact came from |
|---|---|
| `code` | the page's own code: its render conditions, permission reads and data reads |
| `backend-repo (<repo name>)` | a locally cloned backend repo, named |
| `observed in run <short sha>` | what a `prove-branch` run at that SHA saw on the target |
| `developer, <YYYY-MM-DD>` | a developer's answer, on that date |

A row whose fact came from more than one source carries a **comma-separated combination**, in the
order above: `code, backend-repo (billing-api)`.

**A rule that came from a backend repo** is written into the `Shows when` or `Allowed when` cell that
uses it, in product words, with the question id kept in brackets as provenance, and that row's
origin gains the repo:

| Action | Role | Allowed when | Result the user sees | Origin |
|---|---|---|---|---|
| Cancel a fee | Organiser | the registrant is not on the waitlist [Q3] | the fee leaves the list | code, backend-repo (billing-api) |

**`(likely)`.** A backend answer read with confidence `likely`, rather than `confirmed`, ends with
`(likely)` — in the question's `Answer` cell and in every cell it is written into. A rule that lives
in a repo not read (a registration system, a payment processor) is answered as far as the repos go
and says where the rest lives.

## Regenerate

A run of `build-knowledge` on a page that already has a `KNOWLEDGE.md` regenerates it:

- **It rewrites rows whose origin is exactly `code`**, and adds and removes `code` rows to match the
  page as it now is.
- **Every other row stays byte-intact** — any row whose origin names a backend repo, an observed run
  or a developer, alone or in a combination. A human-supplied fact is never rewritten by a
  regenerate.
- **It re-derives the `Derived at:` line** from the commit it read.
- **It reconciles state and question ids** so every reference stays valid: a state or question that
  still exists keeps its id, a new one takes the next free id, and when a removal leaves a gap the
  ids are renumbered and **every cell in the file that cites one is rewritten to match** — the
  `State` column, `Blocks`, and the bracketed question ids in a condition. A renumbered state id is
  printed, since `accounts.md` rows cite state ids and `build-knowledge` never writes that file.
- **Open questions never block a regenerate.**
