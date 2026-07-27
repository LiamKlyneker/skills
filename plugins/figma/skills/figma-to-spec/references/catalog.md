# grimme-ui catalog (fingerprint: 41fa4c5e26be8f3e9883f5cbbab2c0a27efa9504 · generated: 2026-07-23)

Source: `~/schmiede-one/grimme-ui` (`@grimme/ui-components`). Existence catalog only —
for HOW to use a component, see `grimme-ui-components-best-practices`. Regenerate with
`/grimme-ui-catalog`.

Fingerprint covers: `package.json` `"exports"` block + the four
`theme/tokens/*.generated.css` files + `system_icons/_list.tsx`, hashed **content-only**
(`cat … | shasum`) so the stamp is identical on any machine and from any checkout path.

## Class prefix

**Every Tailwind class below is written in its consumer form — unprefixed.** That is the
form to spec against, because every downstream app consumes the library as a preset.

| Where | Form | Example |
|---|---|---|
| Consumer apps (Marketplace, products, mygrimme-frontend, grimme-website) | **unprefixed** | `text-h4` · `bg-surface-button-primary` · `text-primary` |
| grimme-ui's own `src/**` | `g-` prefixed | `g-text-h4` · `g-bg-surface-button-primary` · `g-text-primary` |

Why the split: grimme-ui's **root** `tailwind.config.ts` sets `prefix: "g-"`, but that
config governs only the library's own build (`content: ["./src/**/*.tsx", …]`). The
**exported** preset is a separate object — `"./tailwind-config"` →
`dist/lib/tailwind.config.mjs`, built from `src/tailwind.config.ts`, whose entire body is
`export { baseTailwindConfig as default } from "../base-tailwind.config"`. And
`base-tailwind.config.ts` declares **no `prefix` key**. The prefix therefore never
crosses the package boundary. Verified: `grep -n prefix base-tailwind.config.ts` → no
match; the built `dist/lib/tailwind.config.mjs` contains no `prefix` key either.

All four consumer apps import it the same way and set no prefix of their own:

```ts
import grimmeTailwindConfig from "@grimme/ui-components/tailwind-config";
const config: Pick<Config, "content" | "presets" | "theme"> = {
  presets: [grimmeTailwindConfig],   // note: "prefix" isn't even in the Pick
};
```

Consequences worth knowing when resolving a design against this catalog:

- A `g-`-prefixed class written **in a consumer app is dead** — it matches nothing and
  silently renders unstyled. Two such strays exist today in Marketplace
  (`app/[locale]/_components/grimme-layout/grimme-layout.tsx:211-212` —
  `g-text-body1`, `g-text-body2`, `g-not-italic`). Treat any `g-*` in app code as a bug.
- Conversely, an unprefixed DS class inside grimme-ui `src/**` is equally dead.
- The escape hatch is prefix-independent, because CSS custom properties are not Tailwind
  classes: `className="bg-[var(--g-color-brand-grimme-brand)]"` works in a consumer app
  exactly as `g-bg-[var(…)]` works in-library. The `--g-` in the *variable* name is not
  the Tailwind prefix.

## Sanity check (held)

- `chip` present (`./chip` export, `src/chip.tsx`, `chipVariants` cva).
- `tag` present (`./tag` export, `src/tag.tsx`, `tagVariants` cva).
- `badge` absent — no `./badge` export, no `src/badge.tsx`, no `Badge` symbol anywhere
  in `src/**`.

## Components

54 `"exports"` keys total. 48 are UI components (cross-checked against `src/*.tsx` and
`src/{inputs,layout,table,phone-input,toast,calendar}/*.tsx`); 6 are non-component
utility/config exports (`tailwind-config`, `tailwind-merge-config`, `styles.css`,
`utils`, `plausible`, `plausible/client`). Of the 48 component exports, **1 is stale**
(`typography` — see flag below), leaving **47 working components**. There is no barrel
file: `src/index.tsx` only does `import "../styles.css"`.

name · import subpath · cva variants/sizes · file

| Component | Subpath | cva variants / sizes | File |
|---|---|---|---|
| Accordion | `./accordion` | `variant`: primary \| negative | `src/accordion.tsx` |
| AlertDialog | `./alert-dialog` | — (no cva; composes `Button` variants for actions) | `src/alert-dialog.tsx` |
| Avatar | `./avatar` | `variant`: rounded \| square · `size`: sm \| md \| lg \| xl | `src/avatar.tsx` |
| Autocomplete | `./autocomplete` | — (no cva; wraps `BaseInput`) | `src/inputs/autocomplete.tsx` |
| MultiSelect | `./multiselect` | — (no cva; wraps `BaseInput`) | `src/inputs/multiselect.tsx` |
| Breadcrumb | `./breadcrumb` | `variant`: primary \| negative | `src/breadcrumb.tsx` |
| ButtonGroup | `./button-group` | `variant`: primary \| outline \| outline-negative \| glass \| text | `src/button-group.tsx` |
| Button | `./button` | `variant`: primary \| outline-black \| outline-white \| glass \| text-black \| text-white \| text-wrapped (deprecated aliases `outline`→outline-black, `outline-negative`→outline-white, `text`→text-black, runtime-mapped with a dev console.warn) · `size`: sm \| md \| lg · `loading`: true | `src/button.tsx` |
| IconButton | `./icon-button` | `variant`: primary \| outline \| outline-negative \| glass \| text \| text-negative · `size`: xs \| sm \| md \| lg · `loading`: true (+ separate `iconVariants` for inner icon sizing) | `src/icon-button.tsx` |
| Calendar | `./calendar` | — (no cva; single/range controlled via `mode` prop + DayPicker classNames) | `src/calendar.tsx` |
| Card | `./card` | `variant`: default \| primary \| glass \| drawer · `hoverable`: true | `src/card.tsx` |
| Carousel | `./carousel` | — (no cva) | `src/carousel.tsx` |
| ImagesCarousel | `./images-carousel` | — (no cva) | `src/images-carousel.tsx` |
| LightBox | `./light-box` | — (no cva) | `src/light-box.tsx` |
| Checkbox | `./checkbox` | — (no cva; states via Radix `data-state` + group selectors) | `src/checkbox.tsx` |
| Chip | `./chip` | `variant`: primary \| success \| warning \| error · `clickable`: true · `selected`: true · `size`: md \| sm | `src/chip.tsx` |
| CircularLoader | `./circular-loader` | — (no cva) | `src/circular-loader.tsx` |
| Collapsible | `./collapsible` | `variant`: primary \| negative | `src/collapsible.tsx` |
| Container | `./container` | — (no cva) | `src/container.tsx` |
| DateInput | `./date-input` | — (no cva; composes `BaseInput` + `Calendar`) | `src/inputs/date-input/date-input.tsx` |
| Dialog | `./dialog` | `size` (on `DialogContent`, via `dialogContentVariants`): sm \| md \| lg \| xl \| full | `src/dialog.tsx` |
| SideDialog | `./side-dialog` | — (no cva) | `src/side-dialog.tsx` |
| DropdownMenu | `./dropdown-menu` | — (no cva) | `src/dropdown-menu.tsx` |
| PhoneInput | `./phone-input` | `variant`: primary · `disabled`: true · `size`: md \| sm | `src/phone-input/phone-input.tsx` |
| Popover | `./popover` | — (no cva) | `src/popover.tsx` |
| RadioGroup | `./radio-group` | — (no cva) | `src/radio-group.tsx` |
| SegmentedControls | `./segmented-controls` | — (no cva) | `src/segmented-controls.tsx` |
| SearchInput | `./search-input` | — (no cva; wraps `BaseInput`) | `src/inputs/search-input.tsx` |
| Select | `./select` | `variant`: primary · `size`: sm \| md · `state`: success \| error | `src/select.tsx` |
| Separator | `./separator` | `variant`: primary \| secondary · `thickness`: thin \| thick \| thicker | `src/separator.tsx` |
| Slider | `./slider` | — (cva used only for static thumb classes, no variant axis) | `src/slider.tsx` |
| Skeleton | `./skeleton` | — (no cva) | `src/skeleton.tsx` |
| Switch | `./switch` | — (no cva) | `src/switch.tsx` |
| Table | `./table` | `variant`: default \| striped (also exports `TableHeadFilter` from `table-head-filter.tsx`) | `src/table/table.tsx` |
| Pagination | `./pagination` | `variant`: primary \| secondary | `src/pagination.tsx` |
| Tabs | `./tabs` | `variant`: primary \| secondary | `src/tabs.tsx` |
| Tag | `./tag` | `variant`: default \| primary · `size`: sm \| md | `src/tag.tsx` |
| Teaser | `./teaser` | — (no cva) | `src/teaser.tsx` |
| TextArea | `./text-area` | — (no cva) | `src/inputs/text-area.tsx` |
| TextInput | `./text-input` | — (no cva; wraps `BaseInput`, whose own `baseInputVariants` has `size`: sm \| md) | `src/inputs/text-input.tsx` |
| ToastProvider | `./toast` | `variant` (plain prop, not cva): info \| success \| warning \| error | `src/toast/toast.tsx` |
| Tooltip | `./tooltip` | — (no cva) | `src/tooltip.tsx` |
| Typography | `./typography` | **STALE — see flag below** | *(no source file)* |
| GrimmeHeader | `./grimme-header` | — (no cva) | `src/layout/grimme-header.tsx` |
| GrimmeHeaderNavigation | `./grimme-header-navigation` | — (no cva; `size` prop sm\|md on trigger/link, applied via `cn`) | `src/layout/grimme-header-navigation.tsx` |
| GrimmeHeaderUserMenu | `./grimme-header-user-menu` | — (no cva) | `src/layout/grimme-header-user-menu.tsx` |
| GrimmeContactAssistant | `./grimme-contact-assistant` | — (no cva) | `src/layout/grimme-contact-assistant.tsx` |
| GrimmeFooter | `./grimme-footer` | — (no cva; `size` prop sm\|md on nav link, applied via `cn`) | `src/layout/grimme-footer.tsx` |

Non-component exports (not counted above as components):

| Export | Subpath | Note |
|---|---|---|
| Tailwind preset | `./tailwind-config` | `base-tailwind.config.ts` build output |
| Tailwind-merge config | `./tailwind-merge-config` | tailwind-merge extension config |
| Compiled styles | `./styles.css` | `dist/lib/index.css` |
| Utils | `./utils` | `cn`, `OmitUnion`, `extensionFromUrl`, etc. |
| Plausible (RSC-safe) | `./plausible` | `createPlausibleClass` — pure, no `window` |
| Plausible (client) | `./plausible/client` | `createPlausibleTracker` — `'use client'`, `client-only` |

### Flag: `typography` export is stale

`package.json` still declares a `"./typography"` export, but **no `src/typography.tsx`
or `src/typography.ts` exists** (confirmed via `find src -iname "*typo*"` → only
`src/stories/typography.stories.tsx`, a Storybook file excluded from the `tsup` entry
glob). Git history shows the component was deliberately removed
(`"remove unneeded typography component"`), but the `exports` entry was never cleaned
up. `tsup.config.ts`'s entry glob is `src/**/*.tsx` + `src/**/*.ts`, so nothing produces
`dist/lib/typography.mjs` today — resolving `@grimme/ui-components/typography` would
fail. Treat "Typography" as **not available** as a component.

**The dead export does not mean text styles are unresolvable.** Typography moved from a
component to a set of Tailwind utility classes defined in `theme/typography.ts`, and
those classes are a real, closed, enumerable API — see
[Typography classes](#typography-classes-12--themetypographyts) below for the complete
set of 12. Existence-check text styling against that list, not against the `exports`
map.

## Tokens

276 total: 65 primitive + 66 alias + 110 semantic + 35 dimension — plus 12 typography
classes, which live outside the generated CSS (`theme/typography.ts`) and are listed
last. **Tailwind classes throughout this section are the consumer (unprefixed) form**;
prepend `g-` for the in-library equivalent (see [Class prefix](#class-prefix)). Only **Button** is
fully on the semantic layer today (per `theme/CONTEXT.md`); ~60+ other components still
consume the legacy primitive Tailwind palette (`theme.colors` in
`base-tailwind.config.ts`) directly, alongside these generated tokens. A "prefer
semantic token" check will legitimately fail for almost every non-Button component —
that's expected, not a bug. Upstream source of truth for these generated files is
`theme/figma-tokens/{primitives,alias,mapped,responsive}.json` (design-owned, Figma
export); resolve against the **generated** files below, which is what code consumes.
Regenerate: `yarn tokens:build`; verify: `yarn tokens:check`; pushback list:
`yarn tokens:report`.

### Primitive tokens (65) — `theme/tokens/primitives.generated.css`

CSS-var only, not meant to be consumed directly by components. Grouped by family;
every distinct name is listed (no truncation).

**Brand** (4): `--g-color-brand-grimme-brand` `#e1000f` · `--g-color-brand-grimme-light` `#dd3d49` · `--g-color-brand-grimme-dark` `#780009` · `--g-color-brand-marketing-yellow` `#ffca02`

**Grey** (8): `--g-color-grey-100` `#f1f6f8` · `--g-color-grey-200` `#d2d7d9` · `--g-color-grey-300` `#9aa2a5` · `--g-color-grey-400` `#6e777b` · `--g-color-grey-500` `#161819` · `--g-color-grey-450` `#474c4f` · `--g-color-grey-off-white` `#f7f7f9` · `--g-color-grey-white` `#ffffff`

**Alert** (5): `--g-color-alert-success-green` `#43bf58` · `--g-color-alert-error-red` `#f2616d` · `--g-color-alert-warning-orange` `#ef9e4e` · `--g-color-alert-warning-yellow` `#f2ce61` · `--g-color-alert-info-blue` `#619df2`

**Gold** (2): `--g-color-gold-dark` `#bea05c` · `--g-color-gold-default` `#d5b367`

**Transparencies** (46) — alpha-blended variants of the palette above, named `--g-color-transparencies-<base><alpha>`:
`--g-color-transparencies-50020` `#16181933` · `--g-color-transparencies-50010` `#16181919` · `--g-color-transparencies-50040` `#16181966` · `--g-color-transparencies-50060` `#16181999` · `--g-color-transparencies-50080` `#161819cc` · `--g-color-transparencies-grimme-brand-20` `#e1000f33` · `--g-color-transparencies-grimme-brand-10` `#e1000f19` · `--g-color-transparencies-40080` `#6e777bcc` · `--g-color-transparencies-40060` `#6e777b99` · `--g-color-transparencies-40040` `#6e777b66` · `--g-color-transparencies-40020` `#6e777b33` · `--g-color-transparencies-40010` `#6e777b19` · `--g-color-transparencies-30040` `#9aa2a566` · `--g-color-transparencies-30080` `#9aa2a5cc` · `--g-color-transparencies-30060` `#9aa2a599` · `--g-color-transparencies-30010` `#9aa2a519` · `--g-color-transparencies-30020` `#9aa2a533` · `--g-color-transparencies-20010` `#d2d7d919` · `--g-color-transparencies-20020` `#d2d7d933` · `--g-color-transparencies-20060` `#d2d7d999` · `--g-color-transparencies-20040` `#d2d7d966` · `--g-color-transparencies-20080` `#d2d7d9cc` · `--g-color-transparencies-10080` `#f1f6f8cc` · `--g-color-transparencies-10060` `#f1f6f899` · `--g-color-transparencies-10040` `#f1f6f866` · `--g-color-transparencies-10020` `#f1f6f833` · `--g-color-transparencies-10010` `#f1f6f819` · `--g-color-transparencies-white-10` `#ffffff19` · `--g-color-transparencies-white-20` `#ffffff33` · `--g-color-transparencies-white-40` `#ffffff66` · `--g-color-transparencies-white-60` `#ffffff99` · `--g-color-transparencies-white-80` `#ffffffcc` · `--g-color-transparencies-offwhite-80` `#f7f7f9cc` · `--g-color-transparencies-offwhite-60` `#f7f7f999` · `--g-color-transparencies-offwhite-40` `#f7f7f966` · `--g-color-transparencies-offwhite-20` `#f7f7f933` · `--g-color-transparencies-offwhite-10` `#f7f7f919` · `--g-color-transparencies-45010` `#474c4f19` · `--g-color-transparencies-45020` `#474c4f33` · `--g-color-transparencies-45040` `#474c4f66` · `--g-color-transparencies-45060` `#474c4f99` · `--g-color-transparencies-45080` `#474c4fcc` · `--g-color-transparencies-success` `#43bf5819` · `--g-color-transparencies-warning` `#f2ce610c` · `--g-color-transparencies-4505` `#474c4f0c` · `--g-color-transparencies-info` `#619df219`

### Alias tokens (66) — `theme/tokens/alias.generated.css`

Usage-agnostic named buckets, literal values (no runtime `var()` chain to primitives —
see `theme/CONTEXT.md` "Values are literals"). Full list:

`--g-primary-full-default` `#e1000f` · `--g-primary-full-300` `#dd3d49` · `--g-primary-full-700` `#780009` · `--g-neutral-full-white` `#ffffff` · `--g-neutral-full-off-white` `#f7f7f9` · `--g-neutral-full-100` `#f1f6f8` · `--g-neutral-full-200` `#d2d7d9` · `--g-neutral-full-300` `#9aa2a5` · `--g-neutral-full-400` `#6e777b` · `--g-neutral-full-500` `#161819` · `--g-warning-orange` `#ef9e4e` · `--g-neutral-full-450` `#474c4f` · `--g-warning-default` `#f2ce61` · `--g-error-default` `#f2616d` · `--g-neutral-shades-white-l-10` `#ffffff19` · `--g-neutral-shades-white-l-20` `#ffffff33` · `--g-neutral-shades-white-l-40` `#ffffff66` · `--g-neutral-shades-white-l-60` `#ffffff99` · `--g-neutral-shades-white-l-80` `#ffffffcc` · `--g-neutral-shades-offwhite-l-10` `#f7f7f919` · `--g-neutral-shades-offwhite-l-20` `#f7f7f933` · `--g-neutral-shades-offwhite-l-40` `#f7f7f966` · `--g-neutral-shades-offwhite-l-60` `#f7f7f999` · `--g-neutral-shades-offwhite-l-80` `#f7f7f9cc` · `--g-neutral-shades-100-l-80` `#f1f6f8cc` · `--g-neutral-shades-100-l-60` `#f1f6f899` · `--g-neutral-shades-100-l-40` `#f1f6f866` · `--g-neutral-shades-100-l-20` `#f1f6f833` · `--g-neutral-shades-100-l-10` `#f1f6f819` · `--g-neutral-shades-200-l-60` `#d2d7d999` · `--g-neutral-shades-200-l-80` `#d2d7d9cc` · `--g-neutral-shades-200-l-40` `#d2d7d966` · `--g-neutral-shades-200-l-20` `#d2d7d933` · `--g-neutral-shades-200-l-10` `#d2d7d919` · `--g-neutral-shades-300-l-40` `#9aa2a566` · `--g-neutral-shades-300-l-80` `#9aa2a5cc` · `--g-neutral-shades-300-l-60` `#9aa2a599` · `--g-neutral-shades-300-l-20` `#9aa2a533` · `--g-neutral-shades-300-l-10` `#9aa2a519` · `--g-neutral-shades-400-l-60` `#6e777b99` · `--g-neutral-shades-400-l-80` `#6e777bcc` · `--g-neutral-shades-400-l-40` `#6e777b66` · `--g-neutral-shades-400-l-20` `#6e777b33` · `--g-neutral-shades-400-l-10` `#6e777b19` · `--g-neutral-shades-450-l-80` `#474c4fcc` · `--g-neutral-shades-450-l-60` `#474c4f99` · `--g-neutral-shades-450-l-40` `#474c4f66` · `--g-neutral-shades-450-l-20` `#474c4f33` · `--g-neutral-shades-450-l-10` `#474c4f19` · `--g-neutral-shades-500-l-80` `#161819cc` · `--g-neutral-shades-500-l-60` `#16181999` · `--g-neutral-shades-500-l-40` `#16181966` · `--g-neutral-shades-500-l-20` `#16181933` · `--g-neutral-shades-500-l-10` `#16181919` · `--g-success-default` `#43bf58` · `--g-information-default` `#619df2` · `--g-marketing-default` `#ffca02` · `--g-primary-shades-default-l-10` `#e1000f19` · `--g-primary-shades-default-l-20` `#e1000f33` · `--g-success-shade` `#43bf5819` · `--g-error-shade` `#e1000f19` · `--g-warning-shade` `#f2ce610c` · `--g-neutral-shades-450-l-5` `#474c4f0c` · `--g-gold-default` `#d5b367` · `--g-gold-dark` `#bea05c` · `--g-information-shade` `#619df219`

### Semantic tokens (110) — `theme/tokens/semantic.generated.css`

Component-intent layer, carries Tailwind classes via `tokens.generated.ts`'s
`generatedTheme` (bucketed into `textColor` / `backgroundColor` / `borderColor` /
`fill` / `stroke`). Full list, CSS var → resolved value:

`--g-text-default` `#161819` · `--g-text-overline-default` `#6e777b` · `--g-text-button-outline` `#161819` · `--g-text-link-primary` `#e1000f` · `--g-text-link-grey` `#6e777b` · `--g-text-button-outline-hover` `#ffffff` · `--g-text-button-outline-disabled` `#9aa2a5` · `--g-text-button-primary` `#ffffff` · `--g-text-button-primary-hover` `#e1000f` · `--g-text-button-text` `#161819` · `--g-text-button-glass` `#ffffff` · `--g-text-button-glass-disabled` `#d2d7d9` · `--g-text-button-text-negative` `#ffffff` · `--g-text-button-text-disabled` `#9aa2a5` · `--g-text-link-hover` `#e1000f` · `--g-text-overline-red` `#e1000f` · `--g-text-tab-active` `#e1000f` · `--g-text-tab-default` `#9aa2a5` · `--g-text-tab-hover` `#161819` · `--g-text-breadcrumbs-active` `#161819` · `--g-text-breadcrumbs-default` `#474c4f` · `--g-border-button-outline-black` `#474c4f` · `--g-border-button-disabled` `#9aa2a5` · `--g-border-button-glass` `#ffffff` · `--g-surface-button-primary` `#e1000f` · `--g-surface-button-primary-hover` `#780009` · `--g-surface-button-primary-disabled` `#9aa2a5` · `--g-surface-button-glass` `#16181999` · `--g-surface-button-glass-hover` `#16181933` · `--g-surface-button-glass-disabled` `#f1f6f866` · `--g-surface-button-text-black-hover` `#6e777b19` · `--g-surface-button-outline-black-hover` `#6e777b19` · `--g-surface-primary` `#ffffff` · `--g-icon-information` `#619df2` · `--g-icon-success` `#43bf58` · `--g-icon-warning` `#f2ce61` · `--g-icon-error` `#f2616d` · `--g-border-primary` `#d2d7d9` · `--g-border-action-default` `#6e777b` · `--g-border-action-hover` `#161819` · `--g-border-action-disabled` `#d2d7d9` · `--g-border-action-focus` `#161819` · `--g-border-action-error` `#f2616d` · `--g-surface-hover-red` `#e1000f19` · `--g-text-action-placeholder` `#6e777b` · `--g-text-action-disabled` `#d2d7d9` · `--g-border-selected` `#e1000f` · `--g-icon-warning-orange` `#ef9e4e` · `--g-icon-action` `#161819` · `--g-border-button-outline-white` `#ffffff` · `--g-surface-button-outline-white-hover` `#ffffff33` · `--g-surface-button-text-white-hover` `#ffffff33` · `--g-text-button-outline-negative-hover` `#161819` · `--g-text-button-outline-negative` `#ffffff` · `--g-text-negative` `#ffffff` · `--g-text-breadcrumbs-negative-active` `#ffffff` · `--g-text-breadcrumbs-negative` `#ffffff99` · `--g-surface-action-default` `#e1000f` · `--g-surface-hover` `#d2d7d933` · `--g-border-button-primary` `#e1000f` · `--g-border-button-outline-black-hover` `#161819` · `--g-text-button-wrapped` `#161819` · `--g-text-button-wrapped-hover` `#e1000f` · `--g-surface-action-disabled` `#f7f7f9` · `--g-text-disabled` `#9aa2a5` · `--g-icon-action-negative` `#ffffff` · `--g-text-error` `#f2616d` · `--g-text-help` `#474c4f` · `--g-surface-action-selected-disabled` `#e1000f33` · `--g-surface-action-not-selected` `#9aa2a5` · `--g-border-selected-disabled` `#e1000f33` · `--g-border-primary-red` `#e1000f` · `--g-text-extra-information` `#6e777b` · `--g-icon-action-red` `#e1000f` · `--g-text-chip-selected` `#e1000f` · `--g-text-chip-grey` `#474c4f` · `--g-text-success` `#43bf58` · `--g-surface-marketing` `#ffca02` · `--g-surface-tag` `#f7f7f9` · `--g-surface-error` `#e1000f19` · `--g-surface-success` `#43bf5819` · `--g-surface-chip-default` `#474c4f0c` · `--g-surface-warning` `#f2ce610c` · `--g-surface-divider` `#d2d7d9` · `--g-border-hover` `#e1000f` · `--g-icon-action-disabled` `#9aa2a5` · `--g-icon-action-grey` `#6e777b` · `--g-surface-tooltip` `#6e777b` · `--g-text-action` `#e1000f` · `--g-text-negative-extra-information` `#d2d7d9` · `--g-text-step-default` `#e1000f` · `--g-text-step-unselected` `#9aa2a5` · `--g-surface-negative` `#161819` · `--g-text-header-default` `#6e777b` · `--g-text-header-hover` `#161819` · `--g-surface-chip-selected` `#e1000f19` · `--g-text-overline-dark` `#474c4f` · `--g-border-button-focus-primary` `#e1000f` · `--g-border-button-focus-black` `#161819` · `--g-border-button-focus-white` `#ffffff` · `--g-border-button-focus-grey` `#6e777b` · `--g-surface-loading` `#d2d7d9` · `--g-surface-action-disabled-element` `#d2d7d9` · `--g-text-th-default` `#6e777b` · `--g-text-th-hover` `#161819` · `--g-surface-secondary` `#f1f6f8` · `--g-surface-chip-hover` `#474c4f19` · `--g-surface-chip-selected-hover` `#e1000f33` · `--g-icon-action-red-700` `#780009` · `--g-border-button-primary-hover` `#780009`

Tailwind classes for these (from `tokens.generated.ts`, e.g.): `text-text-action`,
`text-text-button-outline-disabled`, `bg-surface-button-primary`,
`border-border-action-default`, `fill-icon-action-red` / `stroke-icon-action-red`.
The category word (`text`/`surface`/`border`/`icon`) always appears twice by design
("strict namespacing", PR 7704) — see Conventions.

Downstream reality check: **no consumer app uses a single semantic class today.**
Grepping all four apps for `bg-surface-*` / `text-text-*` / `border-border-*` /
`fill-icon-*` / `stroke-icon-*` returns nothing — they all still style from the legacy
palette (`bg-primary`, `text-grey-400`, `border-grey-200`). The semantic classes *are*
available to them (the preset ships them, unprefixed); adoption simply hasn't started
outside the library. Spec accordingly: proposing a semantic class in a consumer app is
valid but will be the first of its kind in that codebase.

### Dimension tokens (35) — `theme/tokens/dimensions.generated.css`

FLOAT px tokens (component-scoped heights/paddings/gaps/sizes/radii); `border-width-*`
are CSS-var-only per the curation rule (no Tailwind width class, to avoid colliding
with the `border-*` color-class family). Full list:

`--g-border-width-button-default` `1px` · `--g-border-width-button-focus` `2px` · `--g-border-width-card` `1px` · `--g-dimensions-height-button-small` `36px` (`min-h-button-small`) · `--g-dimensions-height-button-medium` `40px` (`min-h-button-medium`) · `--g-dimensions-height-button-large` `48px` (`min-h-button-large`) · `--g-dimensions-height-button-wrapped-small` `24px` (`min-h-button-wrapped-small`) · `--g-dimensions-padding-lateral-button` `16px` (`px-lateral-button`) · `--g-dimensions-padding-lateral-button-wrapped` `0px` (`px-lateral-button-wrapped`) · `--g-dimensions-size-icon-button-small` `36px` (`h-icon-button-small` / `w-icon-button-small`) · `--g-dimensions-size-icon-button-medium` `40px` (`h-icon-button-medium` / `w-icon-button-medium`) · `--g-dimensions-size-icon-button-large` `48px` (`h-icon-button-large` / `w-icon-button-large`) · `--g-dimensions-size-icon-button-extra-small` `24px` (`h-icon-button-extra-small` / `w-icon-button-extra-small`) · `--g-dimensions-padding-top-bottom-button-wrapped-medium` `8px` (`py-top-bottom-button-wrapped-medium`) · `--g-dimensions-padding-top-bottom-button-wrapped-large` `12px` (`py-top-bottom-button-wrapped-large`) · `--g-dimensions-gap-button` `8px` (`gap-button`) · `--g-border-width-action-default` `1px` · `--g-border-width-action-focus` `2px` · `--g-border-radius-card` `6px` (`rounded-card`) · `--g-border-radius-button` `4px` (`rounded-button`) · `--g-border-radius-action` `4px` (`rounded-action`) · `--g-border-radius-checkbox` `4px` (`rounded-checkbox`) · `--g-border-radius-chip` `999px` (`rounded-chip`) · `--g-dimensions-size-checkbox` `20px` (`h-checkbox` / `w-checkbox`) · `--g-dimensions-size-radio-button` `20px` (`h-radio-button` / `w-radio-button`) · `--g-dimensions-size-checkbox-clickable-area` `32px` (`h-checkbox-clickable-area` / `w-checkbox-clickable-area`) · `--g-dimensions-size-radio-button-clickable-area` `32px` (`h-radio-button-clickable-area` / `w-radio-button-clickable-area`) · `--g-dimensions-height-chip-medium` `32px` (`min-h-chip-medium`) · `--g-dimensions-height-chip-small` `24px` (`min-h-chip-small`) · `--g-dimensions-gap-chip` `6px` (`gap-chip`) · `--g-dimensions-padding-lateral-chip` `12px` (`px-lateral-chip`) · `--g-dimensions-height-input-field-normal` `48px` (`min-h-input-field-normal`) · `--g-dimensions-height-input-field-dense` `40px` (`min-h-input-field-dense`) · `--g-dimensions-height-input-field-multi-line` `120px` (`min-h-input-field-multi-line`) · `--g-border-radius-input-field` `4px` (`rounded-input-field`)

### Typography classes (12) — `theme/typography.ts`

Not part of the generated CSS tiers and not in the fingerprint — typography lives in
`theme/typography.ts` and is emitted by `typographyThemePlugin` (a `plugin(addComponents)`
registered in `base-tailwind.config.ts`'s `plugins`). Because it rides the exported
preset, it reaches consumers unprefixed exactly like the token classes.

**This is the complete set — 12 stems, no others exist.** The `TYPOGRAPHIES` map in
`theme/typography.ts` is the source of truth; the emitted names are confirmed against
`dist/lib/index.css`. Text styling *is* existence-checkable — check a design's text
style against this table.

| Class (consumer) | In-library | Size / line-height | Weight | Letter-spacing | Transform | Responsive steps |
|---|---|---|---|---|---|---|
| `text-h1` | `g-text-h1` | 40px / 48px | 300 light | -0.01em | none | `md` 60/72 · `lg` 68/72 (spacing → 0) |
| `text-h2` | `g-text-h2` | 32px / 40px | 300 light | -0.01em | none | `md` 40/54 · `lg` 48/54 |
| `text-h3` | `g-text-h3` | 24px / 30px | 400 normal | 0 | none | `md` 28/40 · `lg` 32/40 |
| `text-h4` | `g-text-h4` | 22px / 28px | 400 normal | 0 | none | `md` 22/30 · `lg` 24/30 |
| `text-h5` | `g-text-h5` | 20px / 26px | 300 light | 0.02em | none | `lg` 22px (line-height stays 26) |
| `text-h6` | `g-text-h6` | 18px / 24px | 400 normal | 0.04em | **uppercase** | — |
| `text-body1` | `g-text-body1` | 18px / 24px | 400 normal | 0 | none | — |
| `text-body2` | `g-text-body2` | 16px / 22px | 400 normal | 0 | none | — |
| `text-caption` | `g-text-caption` | 12px / 18px | 400 normal | 0 | none | — |
| `text-overline` | `g-text-overline` | 14px / 20px | 400 normal | 0.05em | **uppercase** | — |
| `text-button` | `g-text-button` | 18px / 18px | 700 bold | — (unset) | — (unset) | — |
| `text-button-link` | `g-text-button-link` | 18px / 18px | 400 normal | — (unset) | — (unset) | — |

Breakpoints are Tailwind defaults (`md` 768px, `lg` 1024px) — `base-tailwind.config.ts`
does not override `screens`.

Notes that matter when resolving a design against this list:

- **No size-suffixed variants exist.** The per-breakpoint numbers come from a private
  `typographyFontSizes` map that is deliberately **not** exported to `theme.fontSize`
  (explicit comment in the file). So `text-h1-base`, `text-h1-md`, `text-h1-lg` are
  **not** classes — only the composite `text-h1`, which carries its own `@screen`
  rules. Responsiveness is built in; never spec `md:text-h1-md`.
- `text-button` / `text-button-link` are flagged in-file as **v2-bridges**: hand-edited
  to match Figma `button/button v2` and `button/button-link v2`, to be regenerated once
  design ships semantic typography tokens. They intentionally set no letter-spacing and
  no text-transform.
- A `button-base-lg` entry (18px/24px) exists in `typographyFontSizes` but no class
  consumes it — dead data, not an available style.
- `theme/figma-tokens/responsive.json` (the upstream typography source) is parsed by the
  token pipeline but **not yet emitted** — the typography migration onto generated
  tokens is deliberately deferred. Until it lands, this hand-written file is the API.

Two companion utility scales ship alongside, via `themeTypography` in `theme.extend`
(they *extend* Tailwind's defaults rather than replacing them):

- **`fontWeight`** — `font-light` 300 · `font-normal` 400 · `font-bold` 700. Tailwind's
  other weights (`font-medium`, `font-semibold`, …) survive the merge but are not DS
  values.
- **`letterSpacing`** — `tracking-narrow` **-0.01em** (DS-only, no Tailwind equivalent) ·
  `tracking-normal` 0 · `tracking-wide` **0.02em** · `tracking-wider` **0.04em** ·
  `tracking-widest` **0.05em**. Note the last three **override** Tailwind's defaults
  (0.025 / 0.05 / 0.1em) with DS values — same class name, different value.

## Icons

37 keys in `SYSTEM_ICONS` (`system_icons/_list.tsx`), consumed via
`<SystemIcon name="..." className="..." />` (`system_icons/system-icon.tsx`). Note: the
skill's typical count of "~25" is stale — the live list has grown to 37. FontAwesome is
used by consuming apps but never inside `grimme-ui src/**` — not recorded here.

Full key list (kebab-case): `angle-right`, `angle-left`, `angle-down`, `angle-up`,
`caret-right`, `caret-left`, `caret-down`, `caret-up`, `chevron-down`, `chevron-up`,
`chevron-right`, `chevron-left`, `close`, `check`, `error`, `fullscreen`,
`image-slash`, `toast-info`, `toast-success`, `toast-warning`, `toast-error`,
`calendar`, `magnifying-glass`, `user`, `eye`, `eye-slash`, `grid-round`, `xmark`,
`whatsapp`, `envelope`, `phone`, `ellipsis-vertical`, `arrow-up`, `arrow-down`,
`zoom-out`, `zoom-in`, `download`.

## Conventions

### Token naming rules (from `theme/CONTEXT.md`)

- **Three tiers**: primitive (`primitives.json`, raw values) → alias
  (`alias.json`, named buckets, e.g. `primaryFullDefault`) → semantic/"mapped"
  (`mapped.json`, component-intent, e.g. `surfaceButtonPrimary`,
  `dimensionsHeightButtonMedium`). All three are now **literals** at every layer
  (design's export resolves everything; no runtime `var()` alias chain) — the
  cascade happens at **build time** via `yarn tokens:build`, not at CSS runtime.
- **camelCase → kebab, faithful flatten.** `kebabize()` mechanically splits
  camelCase/acronym/letter↔digit boundaries. CSS var = `--g-<full-kebab>`. No
  renaming or typo-fixing in code — design owns source quality; issues surface via
  `yarn tokens:report`, not silent fixes.
- **Strict namespacing (PR 7704) — never strip the category word.** The Tailwind
  color class keeps the full kebab path including the category word twice:
  `surfaceButtonPrimary` → `bg-surface-button-primary` (not `bg-button-primary`).
  This is deliberate: stripping the category word once collided the semantic layer
  with the legacy primitive palette (`surfacePrimary` hijacked `bg-primary`
  repo-wide, breaking Checkbox/Slider). The two-layer redundancy
  (`border-border-button-primary`) is the accepted cost of that safety.
  The generator emits **bucket keys only** — the `g-` seen in library source is applied
  later by the root config's `prefix`, and is absent from the exported preset
  (see [Class prefix](#class-prefix)).
  | Top segment | Value | TW bucket | Class (consumer) | Class (in-library) |
  |---|---|---|---|---|
  | `text` | color | `textColor` | `text-text-*` | `g-text-text-*` |
  | `surface` | color | `backgroundColor` | `bg-surface-*` | `g-bg-surface-*` |
  | `border` | color | `borderColor` | `border-border-*` | `g-border-border-*` |
  | `icon` | color | `fill` + `stroke` | `fill-icon-*` + `stroke-icon-*` | `g-fill-icon-*` + `g-stroke-icon-*` |
- **Dimension tokens are different**: the category word (`dimensionsHeight*`,
  `dimensionsPadding*`, `dimensionsGap*`, `dimensionsSize*`, `borderRadius*`)
  selects the Tailwind bucket and is then **dropped** from the emitted class name
  (e.g. `dimensionsHeightButtonMedium` → `min-h-button-medium`, not
  `min-h-dimensions-height-button-medium`). `border-width-*` is the one dimension
  family that stays **CSS-var-only** — a Tailwind width class would share the
  `border-*` family with the border **color** classes, reintroducing the
  exact color/size ambiguity the strict-namespacing rule exists to prevent. Same
  curation rule applies to any future `ring-*`/`divide-*`/`outline-*`/`stroke-*`
  width companions.
- **Version-suffix collapse.** Trailing `V1`/`V2` on a raw camelCase key
  (`borderButtonOutlineBlackV1`/`V2`) collapse to one class using the **highest**
  version's value, suffix stripped even when only one version exists. Design should
  still drop V-suffixes at the source; this is a defensive fallback.
- **Escape hatch.** Every layer emits CSS custom properties, so an arbitrary-value
  Tailwind class can reach a raw token when there's no generated class:
  `className="bg-[var(--g-color-brand-grimme-brand)]"` in a consumer app,
  `g-bg-[var(--g-color-brand-grimme-brand)]` in-library. The `--g-` prefix on the CSS
  variable is unrelated to the Tailwind class prefix and never changes.
- **Typography is not part of this pipeline yet.** It is hand-written in
  `theme/typography.ts` and emitted via `addComponents`, not from `mapped.json` — see
  [Typography classes](#typography-classes-12--themetypographyts).
- Upstream source: `theme/figma-tokens/{primitives,alias,mapped,responsive}.json`
  (Figma export, double-JSON-encoded on export, decoded to plain JSON on disk;
  design-owned, not hand-edited). `responsive.json` (typography, per-breakpoint) is
  parsed but **not yet emitted** — typography migration is deliberately deferred.

### cva skeleton (how a variant axis is declared)

Variants are defined **per-component-file**, not centrally. Typical shape (from
`src/chip.tsx`):

```ts
const chipVariants = cva(
  ["<base classes always applied>"],
  {
    variants: {
      variant: { primary: "...", success: "...", warning: "...", error: "..." },
      clickable: { true: "..." },
      selected: { true: "..." },
      size: { md: "...", sm: "..." },
    },
    defaultVariants: { size: "md", variant: "primary" },
  },
);
```

Consumed as `cn(chipVariants({ variant, clickable, selected, size }), className)`.
Not every component uses `cva` — plenty (Checkbox, Switch, Tooltip, DropdownMenu,
Popover, Skeleton, layout components, …) style purely through static Tailwind classes
plus Radix `data-state`/group selectors, with no variant axis at all. Absence of a
`cva` call is itself a fact the catalog records (see "—" rows in Components).

### "Add a component" steps

1. Add the implementation file under `src/*.tsx` (or the relevant subfolder:
   `src/inputs/`, `src/layout/`, `src/table/`, `src/phone-input/`, `src/toast/`,
   `src/calendar/`).
2. Add a matching key to `package.json` `"exports"` pointing at
   `./dist/lib/<path>.mjs` (+ `.d.ts`), mirroring the file's path under `src/`.
   `tsup.config.ts`'s entry glob (`src/**/*.tsx`, `src/**/*.ts`, excluding
   `src/stories/**`) picks it up automatically on build — but the `exports` key is
   what makes it publicly resolvable, and it is not auto-derived, so it's a manual,
   easy-to-forget step (see the stale `typography` export above for what happens
   when it drifts the other way — file removed, export key left behind).
3. Add Storybook stories under `src/stories/` (excluded from the build via the
   `!src/stories/*` glob entries, so stories never leak into the published package).
4. If the component needs variants, define a local `cva(...)` call in the same file
   (see skeleton above) — there is no shared/central variants registry.
5. Run `yarn build:lib` (or equivalent) to confirm `dist/lib/<name>.mjs` +
   `.d.ts` are produced, matching the new `exports` entry.

### "Add an icon" steps

1. Open `system_icons/_list.tsx`.
2. Add one new key to the `SYSTEM_ICONS` object, kebab-case, holding the raw
   inline `<svg>...</svg>` (viewBox + path(s), typically `fill="currentColor"` so
   consumers control color via Tailwind `text-*`/`fill-*` utilities — a few toast
   icons hardcode their own fill color instead, by design).
3. No separate registration step — `SystemIcon` (`system_icons/system-icon.tsx`)
   looks the name up directly (`SYSTEM_ICONS[name]`), typed as
   `keyof typeof SYSTEM_ICONS`, so adding the key alone makes it usable as
   `<SystemIcon name="your-new-icon" />` and type-checked at call sites.
4. FontAwesome icons must never be added here — this file is exclusively the DS's
   own inline SVG set; FontAwesome is a consuming-app concern only.

### Semantic-layer coverage note

**Button is the only component fully migrated to the semantic token layer today**
(`src/button.tsx` — classes appear there in library form: `g-bg-surface-button-primary`,
`g-text-text-button-primary`, `g-border-border-button-primary`, plus dimension tokens
`g-gap-button`, `g-px-lateral-button`, `g-rounded-button`,
`g-min-h-button-{small,medium,large}` — i.e. `bg-surface-button-primary` etc. to a
consumer).
Every other component (~60+, everything else in `src/**`) still styles from the
**legacy primitive Tailwind palette** (`theme.colors` in `base-tailwind.config.ts`),
which is deliberately kept available alongside the new generated layer so components
can migrate one at a time without a flag day. Practical implication for any
"resolve against the design system" tooling: a rule that prefers semantic tokens over
legacy classes will correctly flag nearly every non-Button component as having "no
semantic equivalent yet" — that is accurate signal about the migration's current
state, not a detection bug.
