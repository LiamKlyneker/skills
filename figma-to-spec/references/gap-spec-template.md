# DS-gap spec template

One file per deduped gap: `gaps/gap-NNN-<slug>.md`. Mirrors the grimme-ui intake template
(`~/schmiede-one/grimme-ui/.azuredevops/pull_request_template/new_feature.md`) so an
escalated gap drops straight into a **GRIMME Libraries** PBI, plus RFC fields the intake
template lacks. The page spec references this gap as `blocked on gap-NNN`; this gap lists
the page as a consumer — the two are cross-linked.

---

# gap-NNN: <short title>

**Category:** color | dimension | typography | component | icon
**Fingerprint:** `<stable hash of (category, observed value, nearest match)>` — used for
backlog dedup so a re-run doesn't refile.
**Recommendation:** build-local | escalate *(user sets at triage)*
**ADO PBI:** #<id — written back after filing; blank until then>
**Consumer(s):** <page-spec + region(s)> · **Instance count:** <N>

## 1. Description

### Overview
<What's missing and why the design needs it, in one short paragraph.>

### Key Features
- <what the new token / component / icon must do>
- <variant / size / state coverage, if a component>

### Technical Changes
<The concrete proposal:>
- **color/dimension/typography:** proposed token name + value + tier (semantic preferred),
  and where it slots in `theme/figma-tokens/*.json` → generated CSS.
- **component:** proposed name, cva shape (variant/size axes + options), API surface,
  states.
- **icon:** proposed `SYSTEM_ICONS` key + the raw SVG.

### Impact on Existing Functionalities
<What existing components/tokens/consumers this touches; migration ripple if any.>

## 2. Breaking Changes
- [ ] **No breaking changes**
- [ ] **Yes** — <explain + migration path>

## 3. Design & Specification Links
**Figma node URL:** <url to the specific node this gap came from>

## 4. Testing Strategy
1. <how to verify the new token/component/icon in Storybook>
2. <visual check against the Figma node>

## 5. Screenshots
<region/node screenshot(s) captured during the scan>

## 6. Checklist
- [ ] Follows project coding standards
- [ ] Storybook stories added
- [ ] Tokens regenerate cleanly (`yarn tokens:build`) *(token gaps)*
- [ ] No new lint warnings
- [ ] Existing tests pass

---

## RFC fields (not in the intake template — required here)

- **Nearest existing considered & why rejected:** <the closest catalog token/component/icon
  and the specific reason it doesn't fit — ΔE, missing variant, wrong metaphor, etc.>
- **Consumer(s) + instance count:** <aggregated across the page — drives priority>
- **Interim fallback used:** <the local recommendation carried in the page spec:
  value / component / file + codemod-friendly API note> — present when build-local.
- **Drawbacks / alternatives:** <if you can't articulate these, that's a stop-and-ask
  signal, not a reason to escalate.>
