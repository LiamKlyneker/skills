---
name: setup-states
description: Find the page states a branch needs in the staging org and record them in the project's `accounts.md` — observe the org first and write a row for every state it already holds, then guide the developer through creating each missing state in the app the way a tester would, verify it, and write its row; for a missing state the page's `KNOWLEDGE.md` knows nothing about, offer once to search the code for how it is made, through `qa:build-knowledge`'s chain mode and its read-only `qa:qa-chain-searcher` agent, and print the chain it finds as numbered steps; a rerun re-verifies the rows already listed and marks a vanished one stale, and never searches. Interactive; drives the browser in this session through the Playwright MCP tools, never creates data itself, never runs a seeder, never dispatches a `qa:qa-driver`, and writes `accounts.md` plus `KNOWLEDGE.md` and the adapter's *Sibling apps* row only through the chain mode. Invoke /qa:setup-states [<page folder>] [S<n>...] — state ids, a page folder for every state of that page, or nothing to re-verify every listed row.
disable-model-invocation: true
---

# setup-states

**Find the states a page needs in the staging org, and record where they are.** The output is rows
in the project's `accounts.md`, whose format is
[`accounts-file.md`](../references/accounts-file.md). The states themselves are defined in each
page's `KNOWLEDGE.md`, whose format is [`knowledge-file.md`](../references/knowledge-file.md). Read
both files first, every run: they are the only definition of the columns, the origins, the stale
mark and the only-grows rule. This skill restates none of it, and where this skill and those files
seem to disagree, those files win.

**It observes, and it guides; it never creates.** It looks for each state in the org through the
app, as a tester signed in with a saved session would. A state the org lacks, the developer creates
in the app by following this skill's steps; this skill then looks again. For a missing state the
page's `KNOWLEDGE.md` has no chain for, it offers one search for how the state is made, and prints
the chain the search finds as steps. It never presses a control that changes data, never runs a
seeder or any end-to-end command, never touches a database, an admin console or an API that writes,
and never dispatches a `qa:qa-driver` or a `qa:qa-grader` — it drives the browser itself, in this
session, because it grades nothing and talks to the developer throughout.

**It dispatches one agent, and only through the chain mode**: the read-only `qa:qa-chain-searcher`,
started by applying `qa:build-knowledge`'s chain mode (`## Guide second` → *The search offer*).

**It writes `accounts.md`.** It writes `KNOWLEDGE.md` and the adapter's *Sibling apps* row **only
through the chain mode**, which is `qa:build-knowledge`'s write and follows that skill's rules, the
way `qa:prove-branch` writes a knowledge file only through the update mode. It never commits, and
writes nothing else into the project tree. The scenario directory the session machinery creates is
excluded from git, as `## Signing in` says.

## Arguments

| Form | Mode | States in scope |
|---|---|---|
| `S4 S5` | **scoped** | the named states of one page |
| `<page folder> S4 S5` | **scoped** | the named states of that page |
| `<page folder>` | **thorough** | every state in that page's `KNOWLEDGE.md` |
| nothing | **rerun** | every `## States` row `accounts.md` already lists for the org |

A state id is a token of the form `S<n>`. Any other token is a page folder; more than one is a stop
that prints the three forms above.

**Resolve state ids to one page** — the page whose `KNOWLEDGE.md` defines them:

1. the page folder given, when there is one;
2. otherwise the page folders the branch touches that hold a `KNOWLEDGE.md` — `git diff --name-only
   <default branch>...HEAD`, each changed path's nearest folder with a `KNOWLEDGE.md` — when that is
   exactly one;
3. otherwise the project's only `KNOWLEDGE.md`, when there is exactly one.

**Stop**, before anything else is read or asked, when:

- no `KNOWLEDGE.md` exists for the page, or in the project at all: name the folder, or say none was
  found, and print `/qa:build-knowledge <page folder>` — that skill writes the file, this one never
  does;
- the ids resolve to more than one page: list the candidate folders and print the command again
  with a folder in front of the ids;
- a named id is not in the page's `## States`: print the ids that exist, each with its state in user
  terms.

A state whose `Env` is `prod` is out of scope for this skill: say so for each one named, and carry
on with the rest.

## Project facts

The project adapter at `<repo-root>/.claude/project/adapter.md` → `## QA`, by row name:

| Row | What for |
|---|---|
| *Session method* | the `Session method` cell of a new `## Orgs` row, and how a session is captured (`## Signing in`) |
| *Credential environment variables* | the roles a session may sign in as — names only, never a value |
| *Browser automation consent* | read as [`browser-readiness.md`](../references/browser-readiness.md) → *Consent* says |
| *Preview basic auth* | optional: read as [`browser-readiness.md`](../references/browser-readiness.md) → *Preview Basic Auth* says |
| *Known accounts* | where the file is; `<repo-root>/.claude/project/accounts.md` when no row names a path |

**A missing `accounts.md` is a stop**: print `/qa:setup`, which writes the empty skeleton. This
skill never writes the skeleton.

**The environment is `staging`.** Every row this skill reads or writes has `Env` `staging`. A target
the adapter or the developer names as production is a stop: prod rows are read-only, and no skill
writes them yet.

## The org

Read `## Orgs` for a `staging` row.

- **One row**: that is the org, and its `Role` is the role this run signs in as.
- **Several rows**: use the one the developer names in this session; otherwise the first, and say
  which.
- **No row** — the first run. **Ask for one org id, once, and nothing else**: the message is that one
  question, with one line saying why, and it is the only question this message asks. End the turn
  and wait. Nothing is signed in, opened or written before the answer.

When the developer answers, write the `## Orgs` row: `staging`, the org id as given, the role — the
one role the *Credential environment variables* row lists, or the first of several, and say which —
the *Session method* value (`api` or `manual`), and today's date (`date +%F`). Then carry on. Never
ask for the org again on a later run; never ask for a URL, a plan id, an order number or any other
id — finding those is this skill's job.

## Readiness

Before any browser is driven, read [`browser-readiness.md`](../references/browser-readiness.md) and
apply it: the *Consent* row, *Preview Basic Auth* on the first request against the target, then
*Playwright MCP readiness*. It is the same text `qa:prove-branch`
reads. Its rule for one browser context per driver does not apply here: this skill drives one browser
itself and dispatches no driver. When readiness stops, the remedy it names ends with running
`/qa:setup-states` again with the same arguments.

## Signing in

Sign in as the org's role through **the same scenario machinery `qa:prove-branch` uses**: read
[`../prove-branch/SKILL.md`](../prove-branch/SKILL.md) → `## Scenarios` and follow its subsections
as written — *The scenario directory*, *Reuse or capture*, *`api` — one sign-in call*, *`manual` —
one login in a visible window* and *No credential value leaves the shell*. That section is the only
definition of where a session lives, when it is reused, how it is captured and how a credential
stays out of the conversation; this skill restates none of it. Where it names `/qa:prove-branch` in
a remedy, read `/qa:setup-states`.

**The target** is the URL the developer names in this session; otherwise the origin on the role's
`scenario.md` *Captured against* line. With neither, stop and ask the developer to run again naming
the staging URL — this is the one case a URL is asked for, and only because no session has ever
been captured.

Then open the page's route in the browser. A page that shows the sign-in screen, or a request that
answers `401` or `403`, means the browser did not load the role's session: stop, and name the
role's `session.json` path and the readiness remedy for loading it.

## Observe first

For every state in scope, before any question and before any guidance:

1. **Recognise the state by the page.** The `## What the user sees` rows whose `State` cell cites
   the state are what makes it visible: the state is there when those sections show as their `Shows
   when` cell says. `## What the user can do` rows that cite it confirm it, never establish it.
2. **Walk the org's data through the app.** Open the page's route — with the org id in place of the
   org parameter when the route has one — and follow the links the page shows into the items it
   lists, as far as a tester would to see the state. Read each screen with `browser_snapshot`.
3. **Observation is read-only.** Navigate, read, follow links, switch a tab or a filter. Never press
   a control whose `Result the user sees` in `KNOWLEDGE.md` saves, changes or removes anything, and
   never submit a form.
4. **Name the proving ids.** The ids the app shows for the items that make the state true — in a
   link, a label or a heading — each named in user words, as the format's `Ids` column says (`shelf
   s-11 · shelf s-12`). When the state belongs to the org itself and no item carries an id, write
   what on screen proves it, in user words (`overdue banner, 2 loans`).

**For each state found, write its `## States` row** with no question: `staging`, the org id, the
page's `Route:` line, the state id, the proving ids, today's date in `Last verified`, and origin
`setup-states <today's date>`. Write the row as soon as the state is seen; a later stop loses
nothing already found.

**A state that already has a non-stale row** for this org and page is re-verified instead of
searched for (`## Rerun`). A state whose only rows are stale is searched for as if it had none.

## Guide second

For each state in scope still not found, decide whether a tester can make it in this app, now. Read
the page's `## How a state is made` table first (a file with no such table holds no chain for any
state), and classify each state in this order.

**1. It cannot, and no search is offered** when its `State, in user terms` cell says it needs time
to pass ("more than 90 days ago", "more than 14 days overdue") or needs a payment to fail — or when
an unanswered open question of the second kind, one asking which org or team on staging holds it,
blocks it. For each such state, say which of the two it is (or that an open question blocks it),
give its `Seeder (for a human)` hint from `KNOWLEDGE.md` as the fast path for a human — the name as
written, or `none known` — and say that it **stays `none known`**. Give no steps for it, offer no
search and write no row.

**2. It can, by the page's own steps** when the page's `## What the user can do` rows make it. Print
**numbered steps a tester follows in the app**, built from those rows and the `Result the user
sees` each one gives.

**3. Otherwise the chain table decides:**

| The chain table holds | The state |
|---|---|
| numbered steps for the state | can be made: print the chain (*Printing a chain*) |
| a step `none` row for the state | cannot be made: print the row's reason, no steps, no row |
| nothing for the state | is unknown: a search is offered (*The search offer*) |

The state cell is read for time and payment only; the table is the only record of where else a state
is made.

Every printed step names three things:

- **the screen** — the page by the name its `KNOWLEDGE.md` heading or the app gives it, with its
  route (`the Shelves page, /shelves`);
- **the control** — by the text on its label, quoted (`press "New shelf"`);
- **the input** — exactly what to type or choose, quoted; a name the developer types starts with
  `qa-setup` so anyone on staging can tell it from real data (`type "qa-setup archived" in the name
  box`).

**Steps make new items and leave existing ones alone.** An item already in the org may be another
row's proof, or someone's test data, so no step archives, edits or removes an item the developer did
not create in these steps: to get an archived shelf, the steps create a `qa-setup` shelf and archive
that one. Steps run as the org's role. A step whose control the role may not use, by its `Allowed
when` cell, names the role that may.

### Printing a chain

A state with chain steps prints them in order, as the page's own steps print. Each printed step
names, from its row: the app, the role, the screen with its route, the action with its quoted inputs,
and the result the user sees that confirms the step. Every name the developer types starts with
`qa-setup`. The steps are the developer's to follow in each app; nothing here signs in to a sibling
app or presses a control in one.

A state with a step `none` row prints that no tester can make it and the row's reason, as written. It
gets no steps and no row. A reason ending `(likely)` is printed with that word: it is a search that
found no answer, not a proof.

### The search offer

After observation, for the states classed unknown by rule 3, **ask once**, in the same message as
the print: how many states, which ones by id and in user terms, and the expected cost — one read-only
code search by an agent over this repo's other pages for those states, and a second question before
any sibling app is read. Say that nothing on staging is touched. **End the turn and wait.**

- A state observation found is never in the offer: it has its row.
- A rerun with no arguments never makes the offer and never starts a search (`## Rerun`).
- This is the only question the offer asks. The chain mode asks its own, separate question about
  sibling apps while it searches; this skill neither asks it first nor repeats it.

**On a yes**, apply `qa:build-knowledge`'s chain mode exactly as `/qa:build-knowledge <page folder>
--chain S<n>...` would: read [`../build-knowledge/SKILL.md`](../build-knowledge/SKILL.md) → `## Chain
mode` and apply it to the page folder for those state ids, touching nothing that mode does not
touch. Name that command in the print. Then classify the same states again from the rewritten table
and print each result by *Printing a chain*.

**On a no**, the states stay unknown. Print `/qa:build-knowledge <page folder> --chain S<n>...` for
them, and write nothing.

### Waiting for the developer

Print every state's steps, every cannot-make state and the search offer, when there is one, in one
message, then **end the turn and wait**. Never press a control on the developer's behalf, and never
write a row for a state that has not been seen.

**When the developer says a state is done, observe again** by `## Observe first`. Write the row only
when the state is visible, with origin `setup-states <today's date>`. When it is still not visible,
say what the page shows instead, give the steps again, and wait again.

## Rerun

Every row in scope is **re-verified**: open the page, find the row's ids the way `## Observe first`
reads them, and check the state is still what the page shows for them.

- **Still visible** — `Last verified` takes today's date. Nothing else in the row changes; its
  `Origin` stays as written.
- **Not visible** — `Last verified` reads `stale <today's date>`. The row stays; rows are never
  deleted.
- **Visible again** on a stale row — `Last verified` takes today's date, plain.

When a row's ids are gone but the state shows on other items, the old row goes stale and the other
items get a new row of their own. In rerun mode, a stale row is reported with the command that sets
the state up again — `/qa:setup-states <page folder> S<n>` — and no steps are given unless the
developer runs it.

A rerun with no arguments only verifies: it makes no search offer, starts no search and applies
no chain mode.

With nothing to re-verify — no `## States` row for the org — say so and print the two other forms
of the command.

## The print

End every turn with:

- the org and the role signed in as, and whether the scenario was reused or captured;
- each row written or refreshed in `accounts.md`, one line each: the state id, the state in user
  terms, the ids and the `Last verified` value;
- each row marked stale, with the command that sets the state up again;
- each state guided, with its numbered steps — the page's own or a chain's — then the line asking the
  developer to say when they are done;
- each state with a step `none` row: that no tester can make it, the row's reason, and no steps;
- each state this app cannot make because it needs time or a failed payment, which of the two it
  is, the seeder hint, and `stays none known`;
- the search offer, when there are unknown states and the run is not a rerun; after a yes, the
  `/qa:build-knowledge <page folder> --chain S<n>...` command the chain mode was applied as, and
  what it wrote; after a no, that command for the developer to run.

When nothing is missing, the print asks nothing.

## Never

- Never create, change or delete data, and never press a control that does.
- Never run a seeder, an end-to-end command, a database query, or an admin console.
- Never dispatch an agent but the chain mode's `qa:qa-chain-searcher`, and only through the chain
  mode. Never dispatch a `qa:qa-driver` or a `qa:qa-grader`.
- Never write any file but `accounts.md`, except `KNOWLEDGE.md` and the adapter's *Sibling apps* row
  through the chain mode. Never delete a row of `accounts.md`, never write `KNOWLEDGE.md` any other
  way, and never commit.
- Never offer or start a search on a rerun with no arguments, for a state observation found, or for
  a state that needs time or a failed payment.
- Never write a `## States` row for a state not seen on the target in this run.
- Never ask for an id the org's data can show. The questions this skill asks are the first org, the
  staging URL when no session was ever captured, and the one search offer. The chain mode's own
  question about sibling apps belongs to that mode, asked during a search the developer agreed to.
