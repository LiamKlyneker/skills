# Writing the wiring

How `create-ui-component-lab` writes a lab's project wiring. Every fact here is read from the
library's code. `<clone>` is the lab repository fetched at the pin; `<lab>` is the lab folder's path
from the repo root.

## Where the answers are

**The library's own preview tooling has usually already answered every wiring question.** Read it
first, in this order, and stop at the first that exists:

1. **A Storybook**: `.storybook/main.*` — its framework, `viteFinal` or `webpackFinal` (aliases,
   PostCSS, plugins); `.storybook/preview.*` — the global stylesheets it imports, in order, and its
   decorators (the *Render wrapper*); `.storybook/preview-head.html` — any `<link>` it adds. A
   `<script>` there that exists for the preview tool or for particular stories — an analytics stub,
   say — is not wiring: ignore it, and name it in the final report.
2. **Another preview or docs app in the repo** — its config, and the root layout or entry file that
   imports the library's global styles.
3. **No preview tooling**: the stylesheets the library ships for consumers (`exports` entries
   ending in `.css`, a `styles` field, the README's setup section), and the library's own build
   config for aliases and PostCSS.

Then confirm each answer against the library's files: a stylesheet or an alias target is real only
if it exists.

## `vite.config.ts`

**One call to `defineLabConfig`, exported as the default.** `stage/vite.ts` in the clone documents
every option; `<clone>/vite.config.ts` and `<clone>/wiring-examples/tailwind-library/vite.config.ts`
show the shape.

```ts
import path from "node:path";
import { fileURLToPath } from "node:url";

import { defineLabConfig } from "./stage/vite.ts";

const labRoot = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(labRoot, "<relative path from the lab folder to the repo root>");

export default defineLabConfig({ labRoot, repoRoot, styles: [/* … */] });
```

- **`repoRoot`** is the git repository's root, even where the library's package sits below it:
  brief and screenshot paths are relative to it.
- **`styles`**: absolute paths. Take the preview's global stylesheet imports **in their order**, and
  keep only those that carry the library's tokens, fonts or base styles; a stylesheet that only
  styles the preview tool's own chrome is left out, and the final report names each one left out and
  why. Then the lab's own white-canvas stylesheet, if there is one. A stylesheet the preview loads
  with a `<link>` goes into a wiring stylesheet in the lab folder as `@import url(…)`, listed first
  — `index.html` is generic and is never edited.
- **`alias`**: every alias the library's preview tooling defines, with the same target. An entry
  imports the library the way a story does, so what resolves for a story must resolve for an entry.
  None, where the preview defines none.
- **`postcssPlugins`**: the PostCSS plugins the library's styling needs, imported from the
  library's own installed packages, configured as its PostCSS config or preview configures them.
  Without them, CSS goes through no PostCSS plugin: the inline config stops Vite reading the
  library's own PostCSS config.
- **`plugins`**: a Vite plugin the library's source needs to load that is not a PostCSS plugin —
  a CSS-in-JS compiler, a styling system's own Vite plugin, an SVG-as-component loader — taken from
  the preview's config.
- **`port`**: leave it out to use 6100. Set another fixed port only when the library's own tooling
  is configured to use 6100.

**A package the wiring imports must already be installed in the library.** If it is not, that is
preflight blocker 3: name it and stop.

## `tsconfig.json`

Start from `<clone>/wiring-examples/tailwind-library/tsconfig.json`, which is generic despite its
folder: `include` everything in the lab, `exclude` `.vite-cache`, and `paths` mirroring every Vite
alias (relative to the lab folder; drop the `/*` line for an alias that names one file, and drop
`paths` when there are no aliases). Add to `types` each ambient type package the library's source
needs, such as a loader's client types; a test runner's globals are left out.

**The lab's type-check compiles every library file an entry imports, under the lab's options.**
Where the library's source fails under them but passes under its own tsconfig, align the option
that differs — `strict` and its siblings, `jsx`, `jsxImportSource`, a decorator flag — with the
library's own tsconfig. Never edit the library's source to make it pass.

## `.gitignore`

One line, `.vite-cache/`. `defineLabConfig` puts the dev server's cache in the lab folder. Write it
in both modes: it is what keeps the cache out of a tracked lab.

## Styling config

**Only where the library's styling system scans source files for the classes it generates.** The lab
must add `<lab>/entries/` to that scan, or a class an entry uses that the library itself never uses
is missing from the page.

- Write a config inside the lab folder that **extends the library's own** and adds the entries to its
  content, and point the PostCSS plugin or Vite plugin at it. Never change the library's config.
- For Tailwind CSS 3, `<clone>/wiring-examples/tailwind-library/tailwind.config.ts` is the worked
  form: it spreads the library's config, anchors the library's content globs to the repo root, and
  adds the entries. The library's class prefix comes with the spread.
- For a system that declares its sources in CSS, the same idea is a wiring stylesheet that imports
  the library's entry stylesheet and declares the entries as an extra source.

A styling system that does not scan — plain CSS, CSS modules, Sass, CSS-in-JS — needs no styling
config at all.

## White-canvas stylesheet

**Only where the library's own preview sets its page background from a token**: a stylesheet in
the lab folder, listed last in `styles`, that sets
`:root { --lab-canvas-white: var(<that token>, #ffffff); }`. The reference form is
`<clone>/wiring-examples/tailwind-library/lab.css`. Where the preview uses a literal colour or sets
no background, write no file and record the default, `#ffffff`, in `PROJECT.md`. A token with
"surface" in its name is not evidence; the preview's own background rule is.

## `PROJECT.md`

**Start from `<clone>/PROJECT.md`.** Keep its title and first paragraph; replace the template's
second paragraph with one line naming this library; keep **every `##` heading exactly**, because
`GUIDE.md` refers to the sections by name; drop each *Fill in:* line and write the answer in its
place. `<clone>/wiring-examples/tailwind-library/PROJECT.md` shows a filled copy for one kind of
library.

| Section | Where the answer is |
|---|---|
| Lab folder | The folder chosen at start. |
| Start command | The package manager's way to run an installed binary — read the lockfile: `pnpm exec`, `yarn`, `npx`, `bunx` — running `vite --config <path to the lab's vite.config.ts>`, and the folder to run it in: the one that holds the manifest declaring `vite`. |
| URL | `http://localhost:<port>`. |
| Type-check command | The same runner with `tsc -p <path to the lab's tsconfig.json>`, in the same folder. |
| Worked example | `entries/demo/`. |
| Library source | Every folder and file the library's components, tokens, icons and helpers live in. |
| Importing the library | A relative import from `entry.tsx` and from `component/<name>.tsx`, one real example each; every alias the wiring defines; and the published package path a consumer's import uses in `usage`, from the manifest's `name` and `exports`. |
| Styling system | What the library styles with, where its tokens live, and any class prefix. |
| Component conventions | Read three of the library's components: class naming, the variant helper (or "none"), the class-join helper and its module, `forwardRef` and `displayName` or not, the export style. |
| Render wrapper | The provider the preview wraps every story in — a Storybook decorator, a docs app's root layout — with its import; or "none". |
| Box-less wrapper | The literal that gives an element `display: contents` in this styling system: a utility class, a CSS-module class the library already has, or an inline `style={{ display: "contents" }}`. |
| Stand-in literals | How a value that stands in for a missing token is written in this styling system, in a `.ts` or `.tsx` file, with one example and the marker on the same line. Where the styling system keeps its values in stylesheets, the stand-in is a constant in the `.tsx` applied through `style`, as `<clone>/PROJECT.md` shows. |
| Stylesheets the stage loads | The `styles` list, in order. |
| White canvas | The token and the stylesheet that sets it, or "the default, `#ffffff`". |
| Wiring files | Every file this skill wrote in the lab folder except the generic part. |

**A section whose fact the code does not answer reads `Unknown — <what was looked at>.`** and is
listed in the final report. Never fill it with a plausible value.

## The library's checks

A whole-repo check that would pick up the lab folder must not start failing because of it.

| Check | Fix inside the lab | Edit outside the lab, printed for the user |
|---|---|---|
| ESLint, legacy `.eslintrc*` format | `<lab>/.eslintrc.json` with `{ "ignorePatterns": ["**/*"] }` | — |
| ESLint, flat `eslint.config.*` format | none: the root config decides what is linted | add `"<lab>/**"` to a global `ignores` entry — an object with `ignores` and no other key |
| A root tsconfig whose `include` covers the lab | none | add `"<lab>"` to `exclude`; where `exclude` is absent, the new list must also name what the default excluded — `node_modules` and the `outDir` |
| A format check | usually none: formatters read one ignore file, at the root | add `<lab>/` to the formatter's root ignore file |

**`.git/info/exclude` hides the lab from git, not from these tools**: none of them reads it. A local
lab needs the same fixes as a tracked one.
