# Render Verification

A ✅ Token Manifest means the token **resolved**. It does not mean the token **survived to the screen**. Every failure caught by this phase so far has been silent: the component renders, looks approximately right, type-checks, lints, and passes its stories.

**Screenshots prove layout, not type.** 13px vs 16px is one pixel of intuition on a label nobody is scrutinising. Read computed values.

## The check — one variant minimum (the default)

Render in the repo's real harness (Storybook), then read `getComputedStyle` per slot and compare against the numbers captured in triage:

| Read | Against |
|---|---|
| `fontSize`, `lineHeight`, `fontWeight` | the Figma **text style**'s size / LH / weight |
| `color`, `backgroundColor`, `borderColor` | the **bound variable**'s resolved value |
| box — height, border width | the node's frame size + stroke |

Also read the element's **class list**. A utility present in source but missing from the DOM was erased by the styling layer — it never reached the browser.

## Trap: class-merge erasure

A `cn()` / `tailwind-merge` helper classifies class names by **its own built-in vocabulary**, not the repo's theme. Wherever a repo's semantic tier reuses a built-in namespace, unknown keys get misclassified and dropped as false conflicts:

```
twMerge('text-label', 'text-fg-default')  ->  'text-fg-default'   // size silently gone
```

Both are `text-*`. tailwind-merge doesn't know `label` is a size, so it calls it a colour, groups it with the colour, and keeps the last one. Colour survives; size/line-height/weight fall back to inherited (`16px/24px/400` under preflight — a plausible-looking near-miss, not an obvious break).

**Probe it during Phase 1**, whenever the repo has a merge helper *and* semantic `text-*` / `bg-*` style names:

```
node --input-type=module -e "import {twMerge} from 'tailwind-merge'; console.log(twMerge('text-<style>','text-<colour>'))"
```

If either class disappears, the helper needs `extendTailwindMerge` registering the ramp under `font-size`. This is a **repo-wide** defect and a ui-profile finding — fix it in the helper, never by dodging it in the component.

Generalise the shape, not the instance: any merge/`@apply`/CSS-in-JS layer that dedupes by class name can erase a semantic utility it doesn't recognise.

## Trap: display-only tooling that no-ops in the test runner

Story addons that force pseudo-states may apply in the **Storybook UI** but not under portable-stories / Vitest. Confirm which context they work in before trusting either.

- **Never assert forced pseudo styling in a play function.** It reads the resting value, and the failure impersonates a broken component.
- Real focus (`click` / `tab`) is genuine and safe to assert. Synthetic `hover()` is **not** — browsers only apply `:hover` from a real cursor, so a hover assertion fails no matter how correct the CSS is.

## Guard what was silent

Where a failure would be invisible, leave a regression assertion behind (computed size/weight on the type slots is the cheap, high-value one).

**Prove the guard fails without the fix.** A guard that passes either way is worthless — re-break it once, watch it go red, restore.
