---
name: setup-env
description: Prepare a web project's staging environment for qa:prove-branch, once per project — open the adapter's Staging URL in a visible browser, where the developer signs in and the skill saves the session; ask one question, what must exist before a tester can use this app and where it is made; and, when the project permits staging writes, learn that one recipe from the code, the screens and the developer, show one approval gate for the item, make it with one drive under the write rules, and only then save the recipe and its made-items row in the project's QA folder. An answer of "nothing", or a project that forbids staging writes, ends with the saved session alone. Run it again only when the project gets a new app or a new role; prove-branch never needs it to have run. Runs on user invocation only. Invoke /qa:setup-env with no argument.
disable-model-invocation: true
---

# setup-env

**Sign in once, and prove the first recipe.** A developer runs `/qa:setup` once to write the
adapter, `/qa:setup-env` once to sign in to staging and make the first item, and then
`/qa:prove-branch` on each implemented branch. This skill is the middle command. It runs once per
project, and again only when the project gets a new app or a new role.

**It points at `prove-branch` and restates none of it.** The session, the recipe learner, the gate's
items, the arrange driver, the write rules and the made-items rows are each defined once, in
[`../prove-branch/SKILL.md`](../prove-branch/SKILL.md). This skill reads the sections it names there
and applies them as a `prove-branch` run would, with only the differences this file states. Where
this file and a section it names seem to disagree on anything else, that section wins. The file
formats are [`recipe-file.md`](../references/recipe-file.md) and
[`made-items-file.md`](../references/made-items-file.md).

**It is never a precondition.** `prove-branch` runs on a project where this skill never ran: its
first run signs in and learns its recipes itself. This skill only moves that work to a quiet moment,
before a branch depends on it.

**It runs on user invocation only.** No loop and no other skill invokes it.

## Arguments

None. Anything typed after the command is not read.

## Project facts

The project adapter at `<repo-root>/.claude/project/adapter.md` is required. This skill reads its
`## QA` section and nothing else, by row name:

| Row | What for |
|---|---|
| *Staging URL* | the base URL of this app's staging environment: where the developer signs in, and the origin of a drive in this app |
| *Credential environment variables* | the role labels, read as `prove-branch` → `## Project facts` says. Only the labels are used: every sign-in here is in a visible window, so no variable is read |
| *Staging writes* | `yes` lets this skill learn and make the one item; absent or any other value reads as `no` |
| *QA folder* | where the recipe and the made-items file go, as `prove-branch` → `### The QA folder` finds it |
| *Sibling apps* | the other apps of the product, read and written only through the `prove-branch` sections this file names |
| *Browser automation consent* | read as [`browser-readiness.md`](../references/browser-readiness.md) → *Consent* says |

**These are stops**, each before any browser opens, and each prints the command alone on its line:

- no adapter, or an adapter with no `## QA` section: say so;
- a `## QA` section with no *Staging URL* row: say that this skill signs in on staging and the
  adapter names none.

```
/qa:setup
```

The *Session method* row is not read. **The developer signs in in a visible window, whatever that
row says**, so no password passes through the chat. A later `prove-branch` run reuses the session
by its own cover test and signs in by the row only when that test fails.

## The roles of this app

The roles this skill signs in are the roles of this app: each label of the *Credential environment
variables* row that no *Sibling apps* entry lists under `roles:`, or one role, `default`, when the
row lists none (`prove-branch` → `### Which role and which app`). A role of a sibling app is signed
in only when the one item is made in that app (`## The one recipe`).

## The session

**For each role of this app, settle a session on the staging host**, by `prove-branch` →
`### Reuse or capture`, with the *Staging URL*'s host as the one host of this run:

- Before the first write, prepare the scenario directory exactly as `### The scenario directory`
  says: the exclude line, `umask 077`, and both checks, where `git status --short` must show
  nothing this skill wrote.
- A session that passes the cover test is reused, and no window opens. Say so.
- **A capture is always *`manual` — one login in a visible window***, against the *Staging URL*:
  propose the command, wait for a yes, name the role to sign in as, and wait for the window to
  close. Then confirm the host accepts the new session, as `### Reuse or capture` step 1 says.
- Write each role's `scenario.md` as `### The scenario directory` describes it.
- `### No credential value leaves the shell` holds in full.

A role whose capture fails, or whose new session the host does not accept, is a stop that names the
role and the host. Nothing after the session runs without one.

**On a project that forbids staging writes, the run ends here.** When the *Staging writes* row is
not `yes`, no drive can prove a recipe, so none is learned and nothing is written to the QA folder.
Ask no question, and go to `## The print`.

## The one question

Ask the developer **one question**, in these words or close to them:

> What must exist before a tester can use this app — a team, an account, a first item — and where
> is it made: in this app, or in another app (its name, and its repo folder beside this one)?

- **"Nothing"**, or any answer that names no item, ends the run with the saved session alone. Go to
  `## The print`.
- **An item** is the one item this skill learns. Write its name in kebab case, as a recipe file is
  named. A variant the answer names — "a team with two members" — is an option of the item, by the
  option names `recipe-file.md` gives; otherwise the item takes no option.
- **Where it is made** is the developer's answer to `prove-branch` → `### The app question` for this
  item: this app, or the app the answer names with its folder. Ask that question later only for what
  this answer left open, such as a sibling app's staging URL.

A recipe file for the item that the QA folder already holds with no `Failed` line, and with a row
for every option named, is not learned again. Say so, and go to `## The print`: `prove-branch` makes
the item from that recipe when a flow needs it.

## The one recipe

**Learn the item by `prove-branch` → `## Learning a recipe`**, from *What is learned* through *When
nothing is learned*, as a run would learn one item for one flow, with these differences:

- **No flow and no page.** Where the searcher's input asks for the route of the page and the state
  it needs from a `KNOWLEDGE.md`, give the developer's answer in their words, and say that this app
  needs the item before a tester can use it.
- **No criteria.** *Made in and Seen in* takes no criterion as a source. `Seen in` names this app,
  because the question asked what this app needs; the code read says how the item is opened there.
- **The run folder** is the arrange folder alone, at
  `.qa-scenarios/runs/<short HEAD>-<UTC timestamp, YYYYMMDDTHHMMSSZ>-arrange/`, made as
  `prove-branch` → `## Driving` → *The run folder* says for that folder. There is no flow folder
  beside it. The draft goes to `recipes/<item>.md` inside it.
- **Before the screen read**, run `## Driving` → *Playwright MCP readiness*. The screen read
  dispatches `qa:qa-driver` as *The agent types* says, with the prompt *Dispatching the drivers*
  lists.
- **A role of a sibling app** that the recipe signs in as is captured by `## Scenarios` → *A session
  for each host*, which also records the role on the app's entry.
- **A `Needs` item** is resolved and learned to the end of its chain by `## Arranging` → *The `Needs`
  chain*, and a `fresh` made-items row of a needed item is checked by *Checking a made item* before
  it is used again.

**Before the gate this skill only reads.** Nothing is written to staging, and nothing reaches the QA
folder.

**When nothing is learned**, ask once for a link to an existing item in its place. A link is
recorded and checked as `prove-branch` → `### A link from the developer` says, with origin
`developer`. No link ends the run with the saved session alone.

## The gate

Show the one item **before anything is written to staging**, because the write rules apply to it:

- the staging URL of each app the drive opens;
- the item, with its whole `Needs` chain in the order of making, each shown as `prove-branch` →
  `## The approval gate` shows **the items to make**, and each item learned here shown as it shows
  **the steps of each new recipe**, with the source of every step;
- each *Sibling apps* entry or role this run recorded;
- that the drive creates items only, types only names that start with `qa-setup`, changes or
  removes nothing it did not create, enters no payment details, and removes nothing afterwards
  (`## Driving` → *The write rules*);
- that the recipe is saved to the QA folder only after its drive made the item.

The developer may change a step, which edits the draft and the drive proves the edit; remove the
item, which ends the run with the saved session alone and saves no draft; or say go. **No driver
that writes starts without go.**

## The drive

After go, **make the item by `prove-branch` → `## Driving` → *Arrange drivers***: one `qa:qa-driver`
per item of the chain, one at a time, in `Needs` order, after *Playwright MCP readiness*. That
section saves a learned draft into the QA folder once its drive made the item, after excluding the
folder by `## Knowledge` → `### The QA folder`, and writes each item's row by *Recording made items*,
with these two values:

- `Role`: the recipe's `Role`, since no flow starts from the item;
- `Origin`: `run <short HEAD>`, the commit checked out when the skill ran.

A drive that fails is handled by *A recipe that fails*: no second attempt, nothing saved for a
draft, and every item the drive created before it reported by its `qa-setup` name and id.

## The print

The print follows `../_shared/final-prints.md`:

- for each role and host: whether its session was reused or captured, and the session file that
  serves it;
- each exclude line written, and each *Sibling apps* entry or role recorded;
- the answer to the one question, or that the project forbids staging writes;
- the recipe saved, with its options and their `Last proved` dates, and the made-items row; or the
  link recorded; or why nothing was saved — "nothing", a recipe already there, an item not learned
  and its reason, the item removed at the gate, a failed drive with its failing step;
- after a failed drive, every item it created, by its `qa-setup` name and id, since no run removes
  one;
- the arrange folder's path, when the run made one.

The last line is the next command, alone on its line:

```
/qa:prove-branch
```

## Never

- Never ask for, read, type or print a credential value, and never read a session file into the
  conversation.
- Never write to staging before go, never drive an item twice, and never retry a drive with a
  changed input.
- Never write anything but the scenario directory and what goes into it, the two exclude lines, a
  saved recipe and its made-items rows in the QA folder, and the adapter's *Sibling apps* entries
  and roles that the `prove-branch` sections named here write. No `KNOWLEDGE.md`, no tracker write,
  and no commit.
- Never run a seeder, an end-to-end command, a database query or a writing API.
- Never install anything into the project.
- Never invoke `qa:prove-branch` or `qa:build-knowledge`.
