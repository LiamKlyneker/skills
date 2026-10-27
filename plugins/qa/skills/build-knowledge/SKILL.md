---
name: build-knowledge
description: Derive a page folder's `KNOWLEDGE.md` from the page's code — what the user sees and when, what the user can do and when, the data states behind both, and the open questions — in product words only; regenerate it without touching rows a human or a backend repo supplied; read locally cloned backend repos (`--repo <path>`) for the rules behind the page's yes-or-no permission reads; and fill one answer on demand (`--fact "<question id>: <answer>"`). It never runs the app, never signs in, never reads staging or `accounts.md`, and commits nothing. Invoke /qa:build-knowledge <page folder> [--repo <path>]... [--fact "Q<n>: <answer>"].
disable-model-invocation: true
---

# build-knowledge

**Derive what a page does, in a tester's words, from the page itself.** The output is one file, the
page folder's `KNOWLEDGE.md`, whose format is [`knowledge-file.md`](../references/knowledge-file.md).
Read that file first, every run: it is the only definition of the header, the four tables, their
columns, the origins, the no-code-words rule and the regenerate rule. This skill restates none of
it, and where this skill and that file seem to disagree, that file wins.

**This skill is the file's only writer.** `qa:setup-states` and `qa:prove-branch` read it; neither
writes it.

**It reads code and nothing else.** It never runs the app, never signs in, never opens a browser,
never reads staging, and **never reads or writes `accounts.md`** — that file is the observed layer
and this skill observes nothing ([`accounts-file.md`](../references/accounts-file.md) → *Writers*).
It writes exactly one file, the page folder's `KNOWLEDGE.md`, and **commits nothing**: no `git add`,
no `git commit`, no change to an exclude file. Whether the file is tracked is the project's call.

## Arguments

| Argument | Meaning |
|---|---|
| `<page folder>` | required; the route folder whose `KNOWLEDGE.md` this run writes |
| `--repo <path>` | optional, repeatable; a locally cloned backend repo to read for the rules behind first-kind questions (`## The backend read`). Its name, wherever the file cites it, is the repo folder's name |
| `--fact "<question id>: <answer>"` | optional; the update mode (`## Update mode`). It runs alone |

Pick the mode from the arguments and the folder:

| Arguments | `KNOWLEDGE.md` in the folder | Mode |
|---|---|---|
| `--fact` | present | **update** — `## Update mode`, nothing else |
| `--fact` | absent | stop: there is no question to answer; print the derive command for the folder |
| `--fact` with `--repo` | — | stop: the update mode runs alone; say so and print the two commands separately |
| no `--fact` | absent | **derive** — `## Deriving`, then `## The backend read` for each `--repo` |
| no `--fact` | present | **regenerate** — `## Regenerate`, then `## The backend read` for each `--repo` |

**Stop** on a folder that does not exist, a `--repo` path that does not exist, or a folder that is
not a page — one with no route entry file that the framework renders as a page. A knowledge file
belongs to a page folder and never to a component, a hook or a sub-folder; name the nearest page
folder above the one given, if there is one, and stop. Never write a file into a folder that is not
a page.

## Project facts

The project adapter at `<repo-root>/.claude/project/adapter.md` is optional for this skill. When it
exists, read two things from it and nothing else:

- `## Commands`, for where the project's end-to-end suite lives and how its data-creation commands
  or tasks are registered. With no such row, search the repository for the suite.
- `## Sources of truth` → the **project explorer agent**, for help locating a component or a data
  client the page imports from far away. `Explore` where it says None.

No adapter row changes the format, and no adapter row is a source for a cell.

## What the run reads

| Source | Read for |
|---|---|
| the page's route entry file | the page's sections, its early returns (loading, error, redirect, not found) and its route pattern |
| every component the page renders, transitively, as far as it renders on this page | each section, each control, and the condition guarding each |
| the hooks and data clients those components read | which request each fact comes from, and which values the page reads from the server as a yes or no |
| the feature-flag configuration | every flag a render condition reads, and its value per environment |
| the folder's `CONTEXT.md` | the page's purpose, in the words the team uses |
| the project's end-to-end suite | the **names** of its data-creation commands or tasks, for `Seeder (for a human)`. Nothing else in it is a source: a test asserting a behaviour is never a substitute for the condition in the page |
| the current commit and today's date | `git rev-parse --short HEAD` and `date +%F`, for `Derived at:` |

It reads nothing else. Not the wider codebase, not documentation, not tickets, not a running app.

## Deriving

**Derive, never copy.** Walk the render conditions and the permission reads yourself, from the
page's entry file down. **Write no row you did not trace to a condition in the code you read** — not
from a component's name, not from `CONTEXT.md`, not from a test, not from what such a page usually
does. A row with no condition behind it is a guess, and a guess in this file is worse than a gap,
because the pass will trust it.

### The walk

1. **Start at the route entry file.** Record every early return in order: the redirect for a
   signed-out visitor, the loading view, the error view, a not-found view. Each is a row in `## What
   the user sees`.
2. **Follow every rendered component.** For each element on screen, record the condition that
   guards it: a role check, a data condition ("the list is empty"), a flag, a permission the server
   answers. A section rendered with no condition is a row with `Shows when` stating that it always
   shows once the page has loaded.
3. **Follow every control.** Each button, link, drawer, menu item, icon action and keyboard shortcut
   is a row in `## What the user can do`: the condition that shows or enables it, and what changes
   on screen when it is used, read from the handler and what the page renders after it.
4. **Classify each condition.** It is one of:
   - **decided on the page** — a comparison, a role check, an empty list, a number of days, a flag.
     The page answers it in full; write the rule itself into the cell, in product words.
   - **a yes or no the server answers** — the page reads a permission or eligibility value from a
     response and shows or hides on it. The page cannot say what the rule is. Write the cell as
     "the app says the member may …", cite a first-kind question in brackets, and open that
     question.
5. **Name the data states.** Every data condition the rows depend on is a state in `## States`,
   phrased as what is true of the data in user terms ("the team has a shelf archived more than 90
   days ago"). Cite the states in each row's `State` column, or `any` when the row shows whatever
   the data is.
6. **Find a seeder hint per state** in the end-to-end suite: a command or task whose name says it
   creates that data. Write its name in `Seeder (for a human)`, or `none known`. A hint is never a
   default, and no skill runs it.
7. **Ask of every state whether a tester can make it in this app, now.** A state that needs time
   to pass (anything "more than N days ago"), is set in another application, or needs a payment
   failure cannot be made that way. Each such state opens a second-kind question.

**One row per section and one row per action**, the format's one-fact-per-row rule applied: a
section that shows under two conditions with two different outcomes is two rows; a section whose one
outcome needs two conditions is one row stating both.

**One row per control, even when two controls do the same thing.** A button and the keyboard
shortcut that opens the same drawer are two rows; never merge them into one row named for the
result. Name each action row by the control itself, with the text on its label quoted ("New shelf"
button, the N key), so a tester can find it on screen.

**Size.** A complex page is about thirty-five sections, twenty actions, twenty states and a dozen
questions, in under 130 lines. A small page is far smaller. A file far over that size has split rows
the format would keep whole; a file far under it on a busy page has merged or skipped conditions.

### Words

Every cell is in product words, and the format's two exceptions are the only ones: `Seeder (for a
human)` may name a command or task, and `Origin` may name a repo.

Translate as you write, never after. The condition `plan.permissions.can_cancel` is "the app says
the member may cancel this plan"; `invoice.days_late > 30` is "an invoice is more than 30 days
late"; `!session` is "the visitor is not signed in"; `isError` is "the app could not fetch the
plans". A visible label is a product word — quote the text the user sees.

**Name a thing with the word the page shows for it, every time.** When the page's own text calls
something a loan, every cell calls it a loan — in a rule the backend read writes too — never a
synonym the page does not use. One thing, one word, across the four tables.

**Before writing the file, check every cell** outside `Seeder (for a human)` and `Origin` for an
identifier's shape — camelCase, snake_case, a joined capitalised name, a constant in capitals, a
file name or extension, a path in the codebase, a backticked term — and paraphrase each one you
find. A seeder cell names the command or task and never the file it is registered in.

### Open questions

**Exactly two kinds, and nothing else is a question:**

1. **A backend rule the page reads as a yes or no** — opened for every condition step 4 classified
   as server-answered. One question per distinct permission or eligibility value, cited in brackets
   in every cell that depends on it.
2. **A staging fact no repo holds** — opened for every state that cannot be made quickly in the app
   itself: one that needs time to pass, one set in another application, one that needs a payment
   failure. The question asks which team, org or account on staging holds it.

**Phrase each question as the fact being asked for, never as a question about the page.**

- A first-kind question names the rule: "What rule decides whether a member may archive a shelf?
  The page only asks the app yes or no." It uses the verb on the control's own label — purge, not
  "permanently delete" — and never reads "whether the app lets …", which asks what the page does.
- A second-kind question names the holder: "Which team on staging has a shelf archived more than
  90 days ago?"

A question about what the page shows is not open: the page answers it, so derive it. A question
about why a rule exists is not open: the file records what, never why.

`Blocks` names state ids and nothing else — never `any`, never `—`. A second-kind question blocks
the state it asks for. A first-kind question blocks the states in the `State` cells of the rows
that cite it; where every such row reads `any`, the control shows whatever the data is, so it blocks
every state in `## States`. `Answer` and `Origin` read `—`.

**Both kinds are checked on every page.** Step 4 opens the first kind and step 7 the second; a file
whose states include one that needs time, another application or a payment failure, with no
second-kind question for it, is incomplete.

**A page that reads a permission from the server and ends with no open questions has guessed.**
Recheck step 4 before writing such a file.

### Ids and the header

States run `S1`, `S2`, … and questions `Q1`, `Q2`, …, contiguous. On a derive they number in order
of first appearance in the file. On a regenerate, every state and question that matches an old one
keeps the old id, whether its row is kept or derived (`## Regenerate`, step 5). Write the header lines as the format defines them: `Route:` from the route pattern, `Purpose:`
from the page and its `CONTEXT.md` in one user-words sentence, `Derived at:` from the commit and
date read above, `Environment:` from any render condition that reads the environment, stated as a
fact, or `none`. No `Backend read:` line unless `## The backend read` ran.

**`Known account` is `none known` on every state this skill creates.** This skill never reads
`accounts.md`, so it cannot know otherwise. The format says `accounts.md` wins wherever the two
disagree, so the cell is a pointer the readers resolve, never a fact this skill establishes.

## The backend read

Runs after a derive or a regenerate, once per `--repo`, for every **first-kind** question whose
`Answer` is `—`. Second-kind questions are never answered from a repo: no repo holds staging data.

For each such question:

1. **Find where the value is produced** in the repo: the response field the page reads, back to the
   code that computes it. Follow it through the repo's own policy, permission or eligibility code.
2. **Return, per answer**: the rule in product words, the repo it came from (the folder's name), and
   a confidence of `confirmed` — the rule is read end to end in this repo — or `likely` — the rule
   is read but some step is inferred, such as a name match between the field and the code.
3. **When the rule continues outside the repo** — the code asks another service, an external
   processor, a registration system — answer as far as this repo goes and **name where the rest
   lives**, by the service's own name as the repo calls it. That is the answer, not a gap: write it.
4. **When the repo holds nothing about the value**, leave the question open for the next repo.

Write each answer into the file:

- the question's `Answer` cell: the rule in product words, ending with ` (likely)` when the
  confidence is `likely`; its `Origin`: `backend-repo (<repo name>)`;
- **every cell that cites the question**: replace the "the app says …" wording with the rule itself,
  keep the question id in brackets as provenance, and end with ` (likely)` when the answer does;
- each such row's `Origin` gains `backend-repo (<repo name>)`, in the order the format gives;
- the `Role` cell of an action row whose rule names a role is rewritten to that role;
- the header gains or extends `Backend read: <repo name>, … · <YYYY-MM-DD>`.

A question that two passed repos both answer takes the repo that produces the value the page reads.

## Regenerate

On a folder whose `KNOWLEDGE.md` exists, apply the format's `## Regenerate` rule in full. This
section says how, never what.

1. **Read the existing file** and sort its rows into **kept** — every row whose `Origin` is anything
  other than exactly `code` — and **derived** — the rest. An **unanswered question** (`Origin` `—`)
  is derived: the derivation opened it, and the derivation closes or keeps it.
2. **Derive the page from scratch**, by `## Deriving`, without looking at the derived rows.
3. **Match** each newly derived row to a kept row describing the same section, action, state or
   question. **A kept row wins its match**: write it back byte for byte and drop the derived one.
   Never reword, re-order the cells of, re-date or re-origin a kept row, even when the derivation
   now phrases it differently.
4. **Replace every derived row** with the newly derived rows that matched no kept row. A newly
   derived row that states the same fact as an old derived row is written in the old row's words,
   so a regenerate changes the text only where the code changed. A derived row the code no longer
   supports is removed. A derived state row keeps its old `Known account` cell when it matches an
   old state, since this skill has no source for that cell.
5. **Reconcile ids** as the format says: a state or question that still exists keeps its id — an
   unanswered question re-derived in step 2 is the same question when it asks about the same
   permission or the same staging fact, and takes the old id, never a fresh one by order — a new
   one takes the next free id, and a removal that leaves a gap renumbers and rewrites every cell
   that cites the old id. A kept row's citation is rewritten for a renumber and nothing else.
6. **Re-derive `Derived at:`**. Every other header line stays as it was unless this run's derivation
   or backend read changed it.

**Open questions never block a regenerate.** A kept row the new code contradicts stays as it is;
print it under the run's summary as a row for a human to check, and do not change it.

## Update mode

`--fact "<question id>: <answer>"` fills one answer and touches nothing else.

1. Find the question row by id. **Stop** when there is none, and print the ids that exist.
2. Write the answer into its `Answer` cell, **in product words** — paraphrase a code word the
   developer used — and set its `Origin` to `developer, <YYYY-MM-DD>` with today's date.
3. **Propagate**: in every cell in the file that cites the question in brackets, write the answer's
   rule in place of the "the app says …" wording or the old answer, keep the bracketed id, and
   append `developer, <YYYY-MM-DD>` to that row's `Origin`.
4. **Touch nothing else**: no other row, no header line, not `Derived at:`, no id. Run no derivation
   and no backend read.

An answered question can be answered again; the new answer replaces the old one in the same cells
and the origin's date moves.

## The print

End every run with:

- the path written and the mode run;
- the count of rows per table, and of rows kept byte-intact on a regenerate;
- **every renumbered state id**, old → new, since `accounts.md` rows cite state ids and this skill
  never writes that file;
- **every open question that remains**, one line each, with its id, the question, and **who or what
  can answer it**. A question the backend read answered only as far as the passed repos go remains,
  even with its `Answer` cell filled:
  - a first-kind question whose rule lives in a repo not passed → that repo by name, as `--repo`;
  - a first-kind question no passed repo could place → the developer, as the `--fact` command;
  - a second-kind question → the staging org: print `/qa:setup-states` with the state ids it
    blocks, literally, so the developer can run it.

## Never

- Never run the app, sign in, drive a browser, call an API, or read staging.
- Never read or write `accounts.md`.
- Never run a seeder or any end-to-end command.
- Never write any file but the page folder's `KNOWLEDGE.md`, and never commit.
- Never write a row not traced to a condition, and never a code word outside the two allowed columns.
- Never rewrite a row whose origin is not exactly `code`, except a renumbered id in it, or the
  cells `--fact` and the backend read propagate into.
