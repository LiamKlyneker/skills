---
name: create-ui-component-lab
description: >
  In a library repo, install the UI component lab — the small app that renders a proposed
  component with the library's real styles — or upgrade the one already there. Fetches the lab's
  generic part at a pinned version, writes the wiring for this library by reading its code, proves
  with one demo entry that the lab renders the library's real styles, and registers the lab in the
  project adapter so design-component can find it. Asks two questions at start (where, and
  tracked or local), never installs a dependency and never commits.
  Invoke /figma-tools:create-ui-component-lab.
disable-model-invocation: true
metadata:
  author: liam
  version: "1.0.0"
---

# Create UI component lab

**Install the lab once, by reading the library — never by asking about it.** A **UI component
lab** is a small Vite + React app inside a library repo that renders a proposed component with the
library's real styles: a specimen, its usage code, and an inspector. `design-component` writes
entries into the lab; this skill is what puts the lab there. It copies the lab's generic part at a
pinned version, writes the wiring that loads *this* library's styles, proves the wiring with one
demo entry, and registers the lab in the adapter. Run on a repo that already has a lab, it upgrades
the generic part and touches nothing else.

```
/figma-tools:create-ui-component-lab        → the lab, the demo entry, the adapter row
/figma-tools:figma-to-brief <figma-url> <ticket> → a brief
/figma-tools:design-component <brief-path>  → an entry in the lab
```

## The pin

**The skill fetches exactly one version of the lab, named here, and nothing else.** All three move
together when the skill is released:

| | |
|---|---|
| Repository | `https://github.com/LiamKlyneker/ui-component-lab` |
| Tag | `v0.1.1` |
| Commit | `31f7ef524faa070e5bfec29b2f3dfb357f1db365` |

**It never follows a branch and never takes "latest".** A tag that resolves to any other commit is
a stop, never a warning: a moved tag means the code is not the code this skill was released
against.

**It copies files out of the fetched copy and runs nothing from it** — no install, no script, no
build in the clone. The copied stage then runs inside the library's own dev tooling, with the
library's own dependencies, so the pin is the only thing that makes the copied code a known
quantity.

## What it addresses

- **The adapter**, `<repo-root>/.claude/project/adapter.md` → `## Design system`: the `Repo role:`
  row, and the one row this skill writes, in this exact shape:

  ```
  - UI component lab: `<path>` · start: `<command>` · url: `<url>` · guide: `<path to the entry guide>`
  ```

  `<path>` is the lab folder from the repo root **with a trailing slash**, `lab/`, so two installs
  write the same row; the guide is `<path>GUIDE.md`, `lab/GUIDE.md`. **The row goes directly after
  the last top-level row of `## Design system`** — before the section's first `###` subsection if
  it has one, at the end of the section only if it has none — and nothing else in the file
  changes. A `UI component lab:` row that already exists means upgrade mode, never a second row.
- **The library repo it runs in** — read freely, written only inside the write boundary below.
- **The lab repository at the pin** — the generic part, the `PROJECT.md` template, and the
  reference wiring under `wiring-examples/`.

**The lab is a Vite + React app, and this skill may say so. Everything about the library is
discovered, never assumed** — its styling system, its helpers, its paths, its package manager. Do
not treat any styling system as the default.

## The run, in order

1. Preflight blockers 1 and 2.
2. Decide the mode from what is on disk.
3. Create: ask the two questions, then preflight blocker 4 against the chosen folder.
4. Fetch at the pin, then preflight blocker 3 against the lab folder.
5. Record the baseline (below).
6. Create or upgrade.
7. Verify.
8. Create only: register the row, as *What it addresses* places it.
9. Final report. Delete the temporary directory.

**The baseline.** Before the first write, record `git status --porcelain`, and run each check
the library runs over the whole repo — the scripts in the package manifest, and the commands its CI
runs, that lint, type-check or format-check and only *read* the repo; never a script that writes (a
fixer, a formatter in write mode), and never tests — recording which pass and, for each that
fails, the files it names. Verify compares against this record, so a check that already failed is
not blamed on the lab. A check may write its own cache, such as an incremental type-check's
build-info: that is the library's behaviour, not a write by this skill, and git status is what the
comparison uses.

## Preflight

**A blocker stops the run with a message that names the fix.** There are four:

1. **No adapter, or no `## Design system` section in it** → _run `/figma-tools:setup` first._
2. **`Repo role:` is not `library`, where an absent row means `consumer`** → _a lab belongs in the
   repo that is the design system._
3. **The library cannot run the stage.** The authority is `README.md` in the clone, section *Getting
   it into a library*: follow its list and its version rules, which at this pin are `react` and
   `react-dom` 18, `vite` with the `@vitejs/plugin-react` whose `vite` peer range includes it,
   `typescript` 5.0 or later, `@types/react` and `@types/react-dom` 18, and `@types/node`. Each must
   be declared in a manifest of the library and installed where Node resolves it from the lab
   folder: read `node_modules/<package>/package.json` in the nearest ancestor, of the path the lab
   folder will have, that has one, and its `version`. → _name each package that is missing,
   undeclared, not installed or at a version outside the rule, and stop._ **The skill never adds a
   dependency and never edits the package manifest**: a missing dependency is the user's decision.
   Declared but not installed → say to run the library's own install.
4. **The target folder exists and is not a lab** (it has no `stage/VERSION`) → _name the folder,
   change nothing._

## The mode — decided by what is on disk

**The mode comes from the repo, never from an argument.** Look for the adapter row, and for a lab
folder anywhere in the repo outside `node_modules`: a folder holding `stage/VERSION` and `GUIDE.md`.

| Found | Mode |
|---|---|
| no row and no lab folder | **create** |
| the row, and `stage/VERSION` in the row's folder | **upgrade** |
| the row, and no lab in its folder | half-state: say the row exists and the folder does not; ask whether to complete it — create at the row's path, then replace the row only if its start, url or guide changed |
| a lab folder, and no row | half-state: name the folder and its version; ask whether to complete it — run the upgrade steps if the versions differ, verify, then write the row from that lab's `PROJECT.md` |

## The two questions — create only

**Two questions, each with a default, asked together in one message, and no others.**

1. **Where?** Default `lab/` beside the library's package manifest — the repo root, in a
   single-package repo. The folder must sit outside everything the library publishes or builds.
   Read the manifest's `files`, `exports` and `main`, any `.npmignore`, the tsconfig the build
   script uses (its `include` and `rootDir`), and any bundler entry globs. Refuse a location one of
   them would sweep in, and name the config that would catch it. A manifest that is not `private`
   and has no `files` list publishes every folder: say so, name `package.json`, and stop — the fix
   is outside the lab and is the user's.
2. **Tracked or local?** Default **local**: a lab is a personal tool until a team decides
   otherwise. Local adds the lab folder to `.git/info/exclude` — find it with
   `git rev-parse --git-path info/exclude`, add one line `/<lab>/` — and never to `.gitignore`,
   which is a tracked file. Tracked adds nothing to any ignore file; the user commits the folder
   themselves. **Either way the skill never stages and never commits.**

## Fetch at the pin

```
tmp=$(mktemp -d)        # outside the library repo; keep the absolute path for later steps
git -c advice.detachedHead=false clone --quiet --depth 1 --branch <tag> <repository> "$tmp/lab"
git -C "$tmp/lab" rev-parse HEAD     # must equal the pinned commit
cat "$tmp/lab/stage/VERSION"         # must equal the tag without its `v`
```

**A different commit, a missing `stage/VERSION`, or a version that does not match the tag is a
stop.** A clone that fails for lack of access is a stop that says so. A warning that the tag `is
not a commit` is expected for an annotated tag in a shallow clone; the `rev-parse` line decides.
Nothing in `$tmp/lab` is ever run.

## Create

1. **Copy the generic part unchanged**: in local mode, add the `.git/info/exclude` line first, so
   the folder never shows as untracked; then copy `stage/`, `index.html` and `GUIDE.md` from the
   clone into the lab folder. **Never edit a copied file, then or later** — an upgrade replaces
   them, and a local edit is lost without a trace.
2. **Write the wiring by reading the library**, per `references/wiring.md`. **The lab must load the
   library's styles the way the library's own preview tooling does, or what it renders is not the
   library.**
3. **Write `PROJECT.md`** from the clone's `PROJECT.md` template, per `references/wiring.md` →
   *PROJECT.md*. **A fact the code does not answer is written as an explicit unknown and listed in
   the final report — never guessed.**
4. **Keep the library's checks green.** If a whole-repo check from the baseline would pick up the
   lab folder, it must not start failing because of it. A fix that is a file inside the lab folder
   is written — a legacy-format ESLint config there, for one. **A fix that needs an edit outside the
   lab folder is never made**: print the exact edit and why, and the user decides. That is the write
   boundary applied to its one hard case. `references/wiring.md` → *The library's checks* has the
   usual cases.
5. **Write one demo entry**, by following the copied `GUIDE.md` and the new `PROJECT.md` exactly as
   `design-component` will — below. Verify, the row and the final report follow, per *The run, in
   order*.

### The demo entry

**The demo entry proves that the wiring loads the library's real styles, and it is the worked
example the guide points at.** It proposes nothing and gets no blueprint.

- Slug `demo`. It renders **one existing, simple library component, unchanged**: one whose look
  depends on the library's tokens (a button, a badge, a tag), that needs no data and no network,
  and that the library's own preview already shows, so the two can be compared.
- One part, class `reused`, with `uses` naming the component and its path. All parts are reused, so
  the entry has no `component/` folder. The part has no `locate`: the library component carries no
  part mark and its source is never edited, so the row does not respond to hover — that is expected.
- One or two of the component's real props as `controls.props` — a variant or size union as a
  `select`, or a boolean — and no example controls. A control lists the values the library
  documents as current; deprecated aliases are left out. `usage` imports from the library's
  published package path and changes with the controls.
- `designWidth: 320`, since the demo reproduces no design. `status: "settled"`, `ticket` and
  `brief` `null`, no screenshots, an empty axis map and no examples. Wrap the render as
  `PROJECT.md` → *Render wrapper* says.
- **Keep it minimal.** It is not a showcase of the stage's features.

## Upgrade

1. **Report the installed version** (`<lab>/stage/VERSION`) **and the pinned one**, and whether the
   lab is tracked or local (`git check-ignore -v <lab>/GUIDE.md` names `info/exclude` for a local
   lab). Equal versions → say so and stop. Installed newer than pinned → say the plugin is older
   than the lab and stop.
2. **Move the old generic part aside** into the temporary directory, then copy the pinned `stage/`,
   `index.html` and `GUIDE.md` into the lab folder. Deleting `stage/` before the copy is what removes
   a file the new version dropped.
3. **Leave `entries/` and every wiring file alone.**
4. **Compare `##` headings**: list every heading in the pinned `PROJECT.md` template that the
   library's `PROJECT.md` lacks. Report each, with the template's *Fill in:* line. Never write them.
5. **Verify**, as for create. An entry other than the demo that no longer type-checks is reported by
   name, with the error, and left alone: `design-component` brings an entry up to the current guide
   when it continues it. A failure in the stage or the wiring that cannot be fixed inside the write
   boundary restores the old generic part from the temporary directory, and says why.

## Verify

**Verification runs before the row is written, and a failure is fixed, not reported as success.**

- **Type-check**: the *Type-check command* in `PROJECT.md` is clean.
- **Start**: check the port first (`lsof -iTCP:<port> -sTCP:LISTEN`). **If the port is taken, say so
  and stop** — never kill what holds it, and never move to another port without saying so. Start
  the *Start command* in the background and wait until the URL answers.
- **Routes**: `/`, `/demo` and `/_specimen/demo` answer 200. The server answers every path with the
  page, so a 200 proves only that it runs; also request `/entries/demo/entry.tsx`, which must
  answer `Content-Type: text/javascript`. A `text/html` answer
  means the module was not found; a 500 means an import did not resolve. The dev server's output
  has no error.
- **The render.** The demo's specimen must show the library component **styled**. Where the session
  has a browser tool — one that is available but not yet loaded counts; load it — open
  `/_specimen/demo` and look at it: compare it with how the library's own preview shows that
  component, where that preview is already running, or else read the computed styles of the
  component's root element and check that the font family and at least one token-driven property — a
  colour, a radius, a padding — have the library's values and not the browser's defaults. **Where
  the session has no browser tool, say plainly that the render was not seen, ask the user to open
  the URL, and never claim that the styles load.**
- **The library's checks**: each whole-repo check from the baseline gives the same result as before.
  A new failure that needs an edit outside the lab is printed (Create, step 4) and stays in the
  final report until the user has applied it; the skill asks once whether they have, and runs the
  check again if so.
- **Git**: `git status --porcelain` matches the baseline — exactly, in local mode; apart from the
  untracked lab folder, in tracked mode.
- **Stop the server the skill started**, unless the user asks to keep it.

## The write boundary (HARD RULE)

**Writes go to three places only**: the lab folder; `.git/info/exclude`, one line, in local mode;
the one adapter row. Never library source, the package manifest or a lockfile, any tracked config
outside the lab folder, a commit, a branch or a dependency install. The temporary directory is
outside the repo and is deleted at the end.

## Final report

Per `../_shared/final-prints.md`:

- the mode, and the version — installed and pinned, on upgrade;
- where the lab is, and whether it is tracked or local;
- what was written: the generic part, and each wiring file with the one fact that drove it;
- every unknown left in `PROJECT.md`, and on upgrade every heading the library's `PROJECT.md` lacks;
- every edit outside the lab the user must decide on, each with the exact text and why;
- each preview stylesheet and preview-head script left out of the wiring, and why;
- every fact where the adapter and the repo disagreed, that the skill followed the repo, and that
  the adapter's other rows were left untouched;
- every entry that no longer type-checks, on upgrade;
- whether the render was seen;
- the lab's URL — the one URL;
- the next step: a brief comes from `/figma-tools:figma-to-brief`, and then

```
/figma-tools:design-component <brief-path>
```

## What it never does

- **Never edits a copied generic file** — `stage/`, `index.html`, `GUIDE.md`.
- **Never edits library source, the package manifest, a lockfile or a tracked config outside the
  lab.** It prints the edit instead.
- **Never installs a dependency.**
- **Never commits, stages or creates a branch.**
- **Never follows a branch or an unpinned tag**, and never continues past a tag that moved.
- **Never runs anything from the clone.**
- **Never guesses a `PROJECT.md` fact.** An unknown is written as one and reported.
- **Never claims the styles load without having seen the render.**
- **Never kills a process holding the port.**
- **Never designs a component.** That is `design-component`.
