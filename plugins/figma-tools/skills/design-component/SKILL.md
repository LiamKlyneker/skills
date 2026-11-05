---
name: design-component
description: >
  In a library repo, turn a design brief into a component the user can see and steer. Classifies
  every fact in the brief as component, API or example, builds the proposed component in the
  library's UI component lab with the recommended decision applied to every ledger row, then takes
  the user's changes in plain language while the page reloads. Writes only inside the lab and to
  a blueprint the later grill and the implementation read. Asks one question at start (resume)
  and stops once, at approve. Invoke /figma-tools:design-component <brief-path>.
disable-model-invocation: true
metadata:
  author: liam
  version: "1.0.0"
---

# Design component

**See a proposal, then respond — never answer questions, then see.** A brief from a library repo
can carry dozens of ledger rows, each already holding a recommendation. Asked as text, they are
questions about a component nobody can see, and nobody can judge an API, a variant or a slot
composition from a wall of text. This skill applies every recommendation as a default, renders
the result in the library's **UI component lab** — the lab, a small app inside the library repo
that renders with the library's real styles and tokens — and lets the user direct changes until
the design is right.

```
/figma-tools:figma-to-brief <figma-url>... <ticket> → the brief
/figma-tools:design-component <brief-path>         → the lab entry + the blueprint
/lk:grill <blueprint-path>                         → the integration questions, not the rows
```

The output is a **blueprint**, `<repo-root>/.claude/briefs/<ticket>/blueprint.md`, where
`<ticket>` is the brief's filename stem. Its shape is `references/blueprint-template.md`.

## What it addresses

Three things, and never one of them by a project-specific name:

- **The brief** — the argument.
- **The adapter**, `<repo-root>/.claude/project/adapter.md` → `## Design system`: the `Repo role:`
  row, the optional `Provisional marker:` row, and the `UI component lab:` row, in this fixed
  shape — named for its kind, because a repo may register other kinds of lab, each on its own row:

  ```
  - UI component lab: `<path>` · start: `<command>` · url: `<url>` · guide: `<path to the entry guide>`
  ```

- **The entry guide** that row points at. **The lab owns its entry format; this skill owns
  only the method.** Read the guide and follow it for where an entry lives, how its files are
  named, how controls are declared, how an example is addressed by URL and how the entry is
  registered. This skill states no file layout, framework, bundler or styling system of its own —
  the same doctrine as a project gate: the adapter names it, the skill follows the pointer.

## Preflight

**A blocker stops the run with a message that names the fix.** There are three:

1. **No `UI component lab:` row, or its path or guide does not exist** → _the lab is not built in
   this repo; run `/figma-tools:create-ui-component-lab`, which builds it and registers the row._
2. **The repo role is not `library`** — in the brief's header or in the adapter, where an absent
   row means `consumer` → _this skill designs components in the repo that is the design system; a
   consumer repo grills the brief instead._ Name which of the two failed.
3. **The brief has no component set with axes under `## Component states`** → _there is nothing to
   design; a brief of recipes and loose parts goes to the grill._

**Everything else is a warning, printed once in the opening report, and the run continues:** an
in-scope state with no design screenshot; a ledger or token row with no code equivalent (it
becomes a stand-in); a row where the brief says its sources disagree; a `## Scope` marked
`⚠ inferred`.

## Resume — the only question at start

| Found | Do |
|---|---|
| no entry and no blueprint | start a new design |
| a blueprint with `Status: draft` | say what exists and when it last changed; ask: **continue** (default) or **start again** |
| a blueprint with `Status: settled` | say the component is approved; ask: **reopen** it (`Status:` back to `draft`) or **stop** |
| an entry with no blueprint | say so; ask: **continue** (write the blueprint from the entry and the brief) or **start again** |

**"Start again" deletes the entry and the draft blueprint — that is why it asks.** On continue,
compare the blueprint's pin line with the brief's: a different pin is a warning that the ledger
rows may have changed since the design was made. Never a stop.

**On continue, the blueprint's header is the authority for where the entry is and what the
component is called.** The brief keeps the design's names; a component named differently from the
brief is a recorded decision, never a reason to rebuild or to ask. That holds only because **a
rename during a session moves the entry and updates the blueprint's header, `## Component` and
`## Decisions` in the same step** — so the next session finds the entry where the header says.

**Continue brings an older entry up to the current guide.** The lab is upgraded independently of
the entries in it, so an entry written against an older guide silently lacks whatever the page has
gained since. After reading the blueprint's header, compare the entry with the guide's current
entry format and fill every field it offers that the entry leaves empty, under the same rule as a
new entry (*The method*, step 3), before the first reply; the opening report says what was filled.

## The unit of a run

**One run is one brief, and one lab entry per component set with axes under
`## Component states`.** Recipes and composed screens — a set whose states lay out other
components into a screen — are not designed; each goes under `## Not handled`. Where it is unclear
whether a set is a component or a recipe, treat it as a recipe and say so in the opening report;
the user can ask for an entry.

**A loose new part that is not a component set gets no design of its own.** It renders as plain
context where an example needs it, and goes under `## Not handled`. The user may ask for an entry
for one during the session.

## The method

### 1 — Classify every fact

The first step of the design, and the heart of it. Every fact in the brief that touches the set
falls into exactly one class:

| Class | Means | Lives in |
|---|---|---|
| **component** | what the library owns and the consumer cannot change: structure, spacing, tokens, truncation, structural glyphs | the component file |
| **API** | what the consumer sets: variant props, slots, children | the props, and the props control group |
| **example** | content that exists only to demonstrate: placeholder copy, placeholder icons, item counts | the examples, and the example control group |

**A Figma axis is not automatically a prop.** An axis whose values differ only in how much content
there is becomes **children**. An axis or boolean that toggles whether an element is present
becomes a **slot**. An axis that changes the component's own chrome becomes a **variant**. Record
every axis and boolean in the entry's axis map, and in the blueprint's `## Axis map`, with what it
became.

**Controls come out of the classes: one group for the component's props, one for example content,
and never a control for a design value.** A control for a padding or a colour offers a tweak the
consumer can never make. **A control's label says, in the words the user would use, what it
changes in the render** — never the variable's name or a fragment of it.

**Every token the component uses is classed too**, from the brief's `## Tokens` table and its
ledger rows: **`reused`** — the library has it; **`new`** — the design has a variable and the
library has no token, so a stand-in renders it; **`updated`** — the library has it with a
different value than the design binds. `updated` is rare, and is always also a line under
`## Questions for the designer`, because it changes other components.

### 2 — Defaults, not questions

**For every ledger row in the component's scope, apply the decision a grill would have
recommended** — the fidelity class and, for `DS with overrides`, the named override — and build
it. A row is in scope when its `States` cell names a state of the set, or its element is a part of
the set's anatomy.

- **Read the design screenshot as an image before deciding a row**, where the brief saved one. A
  decision written from the ledger's prose alone repeats the text, and the text already lost
  fidelity once.
- **Where the brief says its sources disagree, follow the render** and add a line to
  `## Questions for the designer`.
- **Build one API shape: the one you recommend.** Name the alternative in one line in the entry's
  usage section and in `## API`. Build the alternative in full only when the user asks.

### 3 — The entry

Written where and how the guide says. **An optional field in the guide's entry format is a feature
of the page; an entry that leaves one empty hides that feature from the user.** Fill every field
the format offers wherever the brief or the component gives it a truthful value, and name each one
left empty, with why, in the opening report. It holds:

- **The proposed component**, in its own file or files, which **import nothing from the lab**.
  The implementation copies these files into the library source; a lab import would break the
  copy. A mark the guide asks the component files to put on their parts is library code, not a
  lab import: it stays when the files are copied.
- **A marker on every stand-in.** Every literal used because a real token, type step or icon does
  not exist carries the adapter's `Provisional marker` form, or, where that row is absent,
  `PROVISIONAL(<id>): <what should replace it>` in the file's own comment syntax. The id is
  `<ticket>-<n>`, stable for the life of the blueprint. `grep` on the marker is the stand-in
  inventory, and it must match `## Stand-ins` line for line.
- **The two control groups** — props, and example content.
- **Usage code that follows the controls**, so what the user sets is what the code shows.
- **Examples**: every design variant in scope, plus stress examples — long text, every slot
  filled, minimum content.
- **A parts list**: each part `new`, `updated` (with its before and after) or `reused`, with its
  stand-ins. **One part per row** — every sub-component or distinct part is its own row, never
  several joined into one, because whatever the page lets the user do with a part, it does per
  row.
- **Every part addressable and switchable, where the format allows**: where it is in the render,
  and the control values that make it present and absent, for every part a control can toggle. A
  part no control can take away — the root always — is permanent: leave its absent state out.
- **The tokens, where the format has a place for them**: each with its class, the parts that use
  it and, for a `new` token, the stand-in that holds its place.

### 4 — The write boundary (HARD RULE)

**Write only inside the lab path and to the blueprint.** Never edit a library source file,
never run a token build, never commit, never create a branch. A proposed change to an existing
library component is a **copy inside the entry**, listed as `updated` in `## Parts`. The real
change is integration work, recorded under `## Integration`.

**The blueprint under `.claude/briefs/<ticket>/` is this skill's own file, and it is written even
where the guide confines writes to the lab** — the guide is written for entries and knows
nothing of the blueprint. Every other write follows the guide.

## Start and the opening report

Check whether the adapter's `url` answers. If it does not, run the `start` command in the background and
wait until it does. Build the entry and run the entry checks (see *The session*) before the report.
Then print **one** short opening report:

- what was found: the component sets, and what was set aside — recipes and loose parts;
- the warnings from preflight, each once, and that the guide names no entry check, where it names
  none;
- on continue, each field filled to bring the entry up to the current guide;
- each field of the entry format left empty, and why;
- the entry URL, as the guide forms it;
- **once, here only**: that the user says `approve` when the design is right.

**Never repeat the `approve` reminder in a later reply.** The user makes many small requests, and
a reminder on each one is noise.

## The session

**There are no rounds.** The user directs in plain language, and often pastes the lab URL
so the control state is known. For each message:

1. **Make the change in the entry.**
2. **Run the entry checks** (below), and fix a failure before going on.
3. **Update the blueprint** if a decision was made or changed. A purely visual nudge changes only
   the entry.
4. **Reply in a few lines**: what changed, and where to look.

**After every write to the entry, run the checks the entry guide names for handing an entry back
— the first build included — and fix a failing check before the reply, never report it as the
reply.** The user's only view of the work is the page, and a page that does not render shows them
nothing to respond to. Where the guide names no check, say so once in the opening report.

**Ask nothing**, unless an instruction is destructive or cannot be carried out.

**Research runs only when the user asks** — a name, a prop convention, what other libraries do —
through one web-research subagent (`web-researcher` where the session has one) on `model: sonnet`,
never inline. Bring back the answer in a few lines, and record a resulting decision.

**A request outside the scope is recorded, not carried out.** A recipe goes under `## Not
handled`; an edit to a library file goes under `## Integration`. Say so in one line.

**There is no pause command.** State is always on disk: the entry, and the blueprint at
`Status: draft`. Closing the session is the pause, and the resume table is the way back in.

## Approve — the only stop

When the user says `approve`:

1. **Print, once, every in-scope state that has no design screenshot**, each with its lab URL.
   The user may never have looked at them, and an approved row is never asked about again
   downstream. Where every state has a screenshot, say so in one line.
2. **Wait for the user's confirmation.** A change requested instead returns to the session.
3. **Set `Status: settled`**, complete the blueprint — every section present, `## Stand-ins`
   matching the markers, `## Fidelity decisions` covering every ledger row the entry renders —
   and print, per `../_shared/final-prints.md`, the blueprint's path and the next step:

   > Grill the blueprint, not the brief: `deep-grill` asks one question per ledger row of a brief
   > and does not read a blueprint yet, so handing it the brief re-asks what was just approved.

   ```
   /lk:grill .claude/briefs/<ticket>/blueprint.md
   ```

## The blueprint

**Updated throughout the session, never written only at the end.** It is the state that survives a
closed session. The section rules, briefly — `references/blueprint-template.md` has the shape and
the full rules:

- **Header** — `Status: draft | settled`, the brief's path, its pin line copied character for
  character, the entry path, the component file path(s), the last-updated date.
- **`## Component`** — the name and the exports.
- **`## API`** — props and slots, and the one-line alternative not built.
- **`## Axis map`** — every design axis and boolean, and what it became.
- **`## Parts`** — `new`, `updated` or `reused`, with the library component; one part per row.
- **`## Examples`** — name, source, usage code. These are the story candidates later.
- **`## Decisions`** — one line each, with one line of reason.
- **`## Fidelity decisions`** — in deep-grill's exact four-column table, only for the ledger rows
  the entry renders, each phrased as an instruction per `../_shared/fidelity-ledger.md` §1.
- **`## Stand-ins`** — id, the literal used, what replaces it.
- **`## Integration`** — what the implementation still owes: each stand-in replaced, tests,
  stories from the examples, package exports, keyboard and focus behaviour, and every real library
  change — a new type step, a change to an existing component, every `new` and `updated` token.
  These are the later grill's questions.
- **`## Questions for the designer`** — a list. This skill sends nothing to anyone.
- **`## Not handled`** — recipes and loose parts, by their ledger `Element` names.

**The blueprint does not restate layout facts in words.** The component file carries them, and a
second copy drifts the moment the user nudges the entry. The implementation starts as a copy of the
component files into the library source, then works through `## Integration`.

## What it never does

- **Never edits a library source file, runs a token build, commits or creates a branch.**
- **Never asks a ledger row as a question.** Each row is a default the user can see and change.
- **Never adds a control for a design value**, and never labels a control with a variable's name.
- **Never joins several parts into one row of the parts list.**
- **Never leaves a field of the entry format empty without naming it, and why, in the opening
  report.**
- **Never designs a recipe**, and never carries out a request outside the scope — it records it.
- **Never names a framework, bundler or styling system.** The entry guide owns the format.
- **Never repeats the `approve` reminder** after the opening report.
- **Never sends a designer question anywhere.**
- **Never researches inline.** One web-research subagent, on request.
