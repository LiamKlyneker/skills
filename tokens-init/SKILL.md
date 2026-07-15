---
name: tokens-init
description: Bootstrap a repo's semantic token system from Figma seed nodes (foundations frame, type specimen, or representative component). Harvests color variables and typography text styles via the Figma MCP, classifies primitive/semantic tiers, emits CSS variables + Tailwind theme mapping, and generates the repo's ui-profile skill. Use when a repo has no token system yet, the user says "init tokens", "bootstrap tokens from Figma", or "/tokens-init <node-url>".
---

# Tokens Init

Seed a repo's token system from Figma. **Color and typography live in different Figma objects**, and neither is a single read:

- **Color lives in variables.** `get_variable_defs` is **node-scoped** and answers *which* variables the seed uses — but it returns **flat resolved values and silently drops the alias graph** (a semantic aliasing a primitive comes back as the primitive's hex, indistinguishable from a raw value). `use_figma` (Plugin API) answers *how those variables are shaped* — alias targets, scopes, modes, collection membership — file-wide.
- **Typography lives in text styles**, which the variable APIs **cannot see at all**. `getLocalVariableCollectionsAsync()` returns an empty type ramp even when the specimen is sitting on the canvas, because a text style is not a variable. Text styles need their own read (§3) — and a file may bind *some* of a style's fields to variables, so both reads matter.

The seed nodes remain the **scope selector**: they decide what gets emitted. The Plugin API supplies the structure. The better the seeds, the more complete the system.

## What this skill chases

**Color and typography.** Both are *scale-shaped*: a ramp is coherent only when taken whole. You cannot accrete a type scale one component at a time without ending up with eleven arbitrary sizes. So these two get dedicated reads (§3), and the skill will **ask for a second seed** to complete the type ramp rather than ship it half-built (§2).

**Spacing and radius are emitted only if a seed scopes them in** — the seed selector governs, as always, and a `FLOAT` in the harvest emits like any other token. What the skill does *not* do is go hunting for them or ask for extra seeds to complete them: they're small sets that converge on their own, so the gaps accrete per-component through `figma-component`'s minting path and the ui-profile's minted log. A seed that scopes in no spacing is the **accrual boundary, not a defect** — report it (§6) and move on.

This skill is Phase 1 (Foundations) of the future `ui-foundation` skill, shipped standalone.

## Prerequisites

- Official Figma MCP connected (`get_metadata`, `get_variable_defs`, `get_screenshot`, **`use_figma`**). STOP if absent — `use_figma` is **not optional**, the alias graph is unrecoverable without it.
- **Load the `/figma-use` skill before *every* `use_figma` call.** Figma mandates this.
- A paid Dev/Full seat on Figma Professional+ (free seats are rate-limited to uselessness). See `../figma-component/references/install.md`.

## Process

### 1. Preflight

- Detect an existing token system (Tailwind v4 `@theme` block, a `tokens.css`, populated `theme.extend` colors). If found → STOP: this skill bootstraps, it doesn't merge. Report what exists and point at `figma-component` (which resolves against existing tokens) or the future `ui-foundation` (migration).
- Detect Tailwind version → emission format: v4 `@theme` in CSS vs v3 `tailwind.config` `theme.extend`.
- Locate the CSS entry point.

### 2. Seed

Arguments are Figma node URLs — **accept more than one**. Colors and type specimens routinely live on separate frames, and because the seed is the scope selector, a run seeded only at the color frame emits **no typography at all** and never announces the omission.

If none passed, ask — normally the only question: "Paste your foundations/style-guide frame URL (the frame with the color swatches). If your type specimen is a separate frame, paste that too. No foundations page? Paste your most representative component."

If the seeds yield colors but **zero text styles** (§3), ask once for a type specimen node rather than shipping a color-only system in silence. Fold it into the §4 batched question — never trickle it.

### 3. Harvest

Two passes: **color from variables**, **typography from text styles**. Run both against every seed.

#### 3a. Color — variables

Three reads establish scope, then one establishes structure.

- `get_metadata` — map the node, record its name.
- `get_variable_defs` — **the scope set**: which variables the seed node uses. Treat the values as a cross-check only, **never as tier information** (see the hard rule below).
- `get_screenshot` — sanity-check against what's visible. Values on screen but missing from the defs mean raw, unbound fills.
- `use_figma` — **the structure**. Load `/figma-use` first, then run this read-only script (verified working; creates and mutates nothing):

```js
const collections = await figma.variables.getLocalVariableCollectionsAsync();
const out = [];
for (const c of collections) {
  const vars = [];
  for (const id of c.variableIds) {
    const v = await figma.variables.getVariableByIdAsync(id);
    const byMode = {};
    for (const m of c.modes) {
      const val = v.valuesByMode[m.modeId];
      if (val && val.type === 'VARIABLE_ALIAS') {
        const t = await figma.variables.getVariableByIdAsync(val.id);
        byMode[m.name] = { kind: 'ALIAS', target: t ? t.name : null, targetId: val.id };
      } else {
        byMode[m.name] = { kind: 'RAW', value: val };
      }
    }
    vars.push({ name: v.name, id: v.id, resolvedType: v.resolvedType, scopes: v.scopes, byMode });
  }
  out.push({ collection: c.name, id: c.id, modes: c.modes.map(m => m.name), varCount: c.variableIds.length, vars });
}
return { collectionCount: collections.length, totalVars: out.reduce((n, c) => n + c.varCount, 0), collections: out };
```

It iterates **every mode**, not just `modes[0]` — light/dark is the common case and a single-mode read silently discards the other modes' values.

#### 3b. Typography — text styles

**The variable harvest above cannot see typography.** A text style is not a variable; `getLocalVariableCollectionsAsync()` will never return one, and `get_variable_defs` has no text-style equivalent. Skipping this pass reports "no typography variables — raw values found" while the type ramp sits untouched on the canvas. That is a silent structural miss, not a finding.

Same split as the color pass, both halves inside one `use_figma` call: **scope** from walking the seeds' TEXT nodes, **structure** from resolving each style. Load `/figma-use` first, then run this read-only script (verified working; creates and mutates nothing):

```js
const seedIds = ['2:2', '31:2']; // from each URL's node-id — dash → colon
const usedIds = new Set(), unstyled = [], seen = [];

for (const seedId of seedIds) {
  const seed = await figma.getNodeByIdAsync(seedId);
  if (!seed) { seen.push({ seedId, error: 'NOT_FOUND' }); continue; }
  const texts = seed.type === 'TEXT'
    ? [seed]
    : ('findAllWithCriteria' in seed ? seed.findAllWithCriteria({ types: ['TEXT'] }) : []);

  let styled = 0;
  for (const t of texts) {
    if (t.textStyleId === figma.mixed) { unstyled.push({ seedId, node: t.name, why: 'MIXED' }); continue; }
    if (!t.textStyleId) { unstyled.push({ seedId, node: t.name, why: 'RAW' }); continue; }
    usedIds.add(t.textStyleId); styled++;
  }
  seen.push({ seedId, name: seed.name, textNodes: texts.length, styled, unstyled: texts.length - styled });
}

const styles = [];
for (const id of usedIds) {
  const s = await figma.getStyleByIdAsync(id);
  if (!s) continue;
  const bound = {};
  for (const [field, alias] of Object.entries(s.boundVariables ?? {})) {
    const v = await figma.variables.getVariableByIdAsync(alias.id);
    bound[field] = { target: v ? v.name : null, targetId: alias.id };
  }
  styles.push({
    name: s.name, remote: s.remote,
    fontName: s.fontName, fontSize: s.fontSize,
    lineHeight: s.lineHeight, letterSpacing: s.letterSpacing,
    bound,
  });
}

const local = await figma.getLocalTextStylesAsync();
return { seen, styles, unstyled, unstyledCount: unstyled.length, localNames: local.map(s => s.name) };
```

Four things this leans on:

- **`getStyleByIdAsync` resolves remote styles too**, not just local ones — `s.remote` flags them. This is why typography does *not* inherit the variables' "library-backed → structure unknown" dead end: a published type ramp still reads.
- **`boundVariables` is the alias graph, and it returns IDs — not names.** A raw read gives `{ type: 'VARIABLE_ALIAS', id: 'VariableID:30:7' }`; you cannot emit `var(--font-size-xl)` from that. Resolve every alias to `v.name`, exactly as the color pass does. This is the step that connects a text style to the §3a primitives.
- **Mind the two namespaces.** Styles hang off the `figma` global (`figma.getStyleByIdAsync`), variables off `figma.variables` (`figma.variables.getVariableByIdAsync`). Crossing them throws `no such property`.
- **Node ids in URLs use a dash** (`node-id=31-2`); the Plugin API wants a colon (`31:2`).

**`seen` is the diagnostic that matters.** Per seed it reports `textNodes` / `styled` / `unstyled`. A seed with many text nodes and `styled: 0` is a foundations frame whose type is hardcoded — it is not a type specimen, no matter what it's called. That's the §2 "ask for a specimen" trigger, and reading it off `seen` beats inferring it from an empty `styles` array.

**Hard rule: never infer an alias by matching values.** If a semantic's target isn't in the harvest, say so — do not guess from a value that happens to match. Value-matching looks correct on seeds where every primitive value is unique and fails silently everywhere else: two primitives sharing a value make the match ambiguous, and it cannot represent an alias at all. **A wrong `var()` reference is worse than an honest finding**, because it collapses a tier with no error.

This rule covers **both** alias graphs: a variable's `byMode[mode].target` and a text style's `boundVariables`. A `13px` text style sitting next to a `13px` `font/size/sm` primitive is exactly the trap — only `boundVariables.fontSize` says whether they're actually linked.

**Reconcile the sources** before classifying. Variables:

| Case | Meaning | Action |
|---|---|---|
| In defs **and** harvest | Normal | Emit, using the harvest's structure. |
| In harvest, **not** in defs | Exists in the file but the seed doesn't use it | Out of scope — **except** when it's the alias target of an in-scope semantic (next row). |
| Alias target **not** in the seed's defs | Semantic points at a primitive whose swatch isn't in the seed | **Pull the primitive in and emit it.** Emitting the semantic without its target is what silently collapses the tier. Note it in the report. |
| In defs, **not** in harvest | Variable is **not local** — it comes from a published library | `getLocalVariableCollectionsAsync()` returns local variables only. **Report it; do not guess its structure.** Consider `get_libraries`. |

Text styles:

| Case | Meaning | Action |
|---|---|---|
| Used in a seed, `remote: false` | Normal, local | Emit. |
| Used in a seed, `remote: true` | Library-backed | `getStyleByIdAsync` still resolved it — **emit it**, and note the origin. Unlike variables, this is not a dead end. |
| In `localNames`, unused by any seed | Exists in the file, out of the seed's scope | Skip. Don't widen scope to the whole file. |
| `textStyleId === figma.mixed` | One text node carrying several styles | **Report; never guess** which style is the specimen's subject. |
| No `textStyleId` (`why: 'RAW'`) | Text with unbound font properties | **Usually the frame's own chrome** — section headers, swatch labels, spec captions — and expected on a documentation frame. **Report the count, never a row per node**; specimens run ~10:1 chrome to subject, so enumerating buries the five tokens that matter. It's a genuine hygiene finding on *component* nodes, which is `figma-component`'s job, not this skill's. |
| `boundVariables` empty | Style's values are literal; no primitive tier beneath it | Emit as semantic with literal values, and **report the missing tier**. Do not invent primitives to sit under it. |
| Zero text styles across all seeds | Seed has no type on it at all | Ask for a type specimen node (§2). Don't emit a color-only system silently. |

### 4. Classify tiers

Per `../_shared/ui-standard.md`. Tier comes from **collection membership + alias structure in the harvest first**, and naming only to corroborate: a variable whose modes are all `RAW` is a primitive; one that `ALIAS`es another is semantic. Figma naming usually agrees — palette-style (`color/brand/green-500`) → primitive; usage-style (`color/surface/primary`) → semantic — and **when naming and structure disagree, that disagreement is itself a finding**, not something to resolve silently.

Figma modes → light/dark overrides. A collection with one mode has no overrides to emit; don't invent them.

**Typography tiers.** The same two-tier shape, expressed in different objects:

- **The text style *is* the semantic tier** — the role a component consumes (`text-label`), never a raw size. There is no separate "semantic type variable" to look for.
- **`boundVariables` are its aliases down to tier 1**: `boundVariables.fontSize` → `font/size/sm`. Those `font/size/*` and `font/lineHeight/*` variables are the primitives, and they come from the §3a variable harvest — the two passes meet here.
- **Weight is not a token.** Figma keeps it in `fontName.style` (`"Semi Bold"`), part of the composite style and bound to nothing. Emit it literal. Tokenising it **invents a tier the Figma file does not have** — the same sin as guessing an alias.
- **Role-based names survive a redesign; size-based names don't.** `heading/lg` keeps meaning when the number changes from 20 to 22; `text-20` becomes a lie. If the file's style names are size-based, raise it at the checkpoint — never silently rename.

Batch ALL ambiguities into ONE question set with recommended answers (e.g. "`green-2` is used directly as a fill in the seed — primitive exposed by mistake, or intentionally semantic?"). Do not trickle questions.

### 5. Emit

- `tokens.css` (or the repo's CSS entry): primitives + semantic aliases as CSS custom properties; mode overrides if Figma modes exist. Each semantic's `var()` target comes from the harvest's `byMode[mode].target` — **never from a value match**.
- The Tailwind mapping, in the detected format.
- The **ui-profile** project skill at `.claude/skills/<repo>-ui/SKILL.md` per `../figma-component/references/ui-profile.md`, seeded with the Figma → code token map.

**Converting harvested values.** The Plugin API returns colors as `{r, g, b, a}` floats in **0–1**, not hex — `get_variable_defs` was doing that conversion for you and no longer is. Convert with `Math.round(channel * 255)` per channel. Keep alpha: `a: 1` → 6-digit hex; `a < 1` → emit `rgb(... / <a>)` or 8-digit hex rather than dropping the channel silently. Other `resolvedType`s (`FLOAT` for spacing/radius, `STRING` for font family) come back as plain values and need units applied at emit — a `FLOAT` of `8` is `8px`, not `8`.

**Tailwind v4 note.** When semantic tokens reference primitives defined outside the theme block, use `@theme inline` so utilities compile to the primitive reference (`var(--neutral-0)`) rather than snapshotting the value at `:root`. Without `inline`, mode-scoped overrides silently stop working, because the theme var computes against `:root`'s value rather than the override's.

**Typography emission (Tailwind v4).** One Figma text style = one `text-*` utility. The shape, and the trap that dictates it:

- **Type primitives stay in `:root` — NOT in `@theme`.** Tailwind's `--font-*` namespace generates font-***family*** utilities, so a `--font-size-xs` entry inside the theme block mints a bogus `font-size-xs` family utility. Keep `--font-size-*` / `--font-line-height-*` in `:root` and reference them from the theme block. This bites every naive implementation.
- **Text styles go in `@theme inline`** as `--text-<role>` plus its modifiers. Font families are the one type token that *does* belong in `--font-*`.

```css
:root {
  --font-size-sm: 13px;          /* tier 1 — the `typography` collection */
  --font-line-height-sm: 18px;
}

@theme inline {
  --font-sans: Inter, system-ui, sans-serif;

  --text-label: var(--font-size-sm);                     /* boundVariables.fontSize */
  --text-label--line-height: var(--font-line-height-sm); /* boundVariables.lineHeight */
  --text-label--font-weight: 500;                        /* literal — fontName.style */
}
```

One utility, `text-label`, carrying size, line-height and weight together.

**Converting text-style values.** The Plugin API hands these back raw, like the colors:

- `lineHeight` `{unit:'AUTO'}` → `normal`, **not a number**. `PIXELS` → `px`. `PERCENT` → unitless ratio (`value / 100`).
- `letterSpacing` `PERCENT` → **`em`** (percent-of-font-size is exactly what `em` means). `PIXELS` → `px`. Omit when `0` rather than emitting `0px`.
- `fontName.style` blends weight *and* italic into one string (`"SemiBold Italic"`). Resolve it through a named map — Thin 100, ExtraLight 200, Light 300, Regular 400, Medium 500, SemiBold 600, Bold 700, ExtraBold 800, Black 900 — plus `font-style: italic` when present. It's a lookup, not a parse; Figma's spelling varies (`"Semi Bold"` vs `"SemiBold"`).

### 6. Report

- Token inventory table: Figma name → CSS var → Tailwind utility, grouped by tier, **with each semantic's alias target shown** — this table is where a collapsed tier becomes visible.
- **Type ramp table**: Figma text style → Tailwind utility → font / size / line-height → **bound-to targets**. Same purpose as the alias column above — a style with an empty `Bound to` cell is a type token with no primitive under it, visible at a glance.
- Gap/hygiene findings vs the designer contract (`../_shared/ui-standard.md`): e.g. "3 fills bound to raw hex, not variables". Report unstyled text **as a count** (`52 of 57 text nodes carry no text style — specimen chrome`), not as a list. Spacing/radius the seeds didn't scope in are the **accrual boundary, not a defect** — name them so the next component knows they're coming, don't treat them as a gap this run failed to fill.
- **Harvest reconciliation findings** (from the tables in §3), each stated plainly rather than resolved silently:
  - alias targets pulled in from outside the seed's scope,
  - variables in the defs but absent from the local harvest (**library-backed — structure unknown**),
  - text styles resolved as `remote: true` (library-backed, but emitted — note the origin),
  - text styles with empty `boundVariables` (**literal values, no primitive tier**),
  - text nodes that were `MIXED` or carried no style at all,
  - any variable or style whose naming contradicts its structure.
- Next step: `/figma-component <component-node-url>`.

Leave the working tree **uncommitted**.
