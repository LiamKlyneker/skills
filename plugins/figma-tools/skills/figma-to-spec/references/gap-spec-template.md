# DS-gap spec template

One file per deduped gap: `gaps/gap-NNN-<slug>.md`. Mirrors the grimme-ui intake template
(`~/schmiede-one/grimme-ui/.azuredevops/pull_request_template/new_feature.md`) so an
escalated gap drops straight into a **GRIMME Libraries** PBI, plus RFC fields the intake
template lacks. The page spec references this gap as `blocked on gap-NNN`; this gap lists
the page as a consumer — the two are cross-linked.

**A candidate keeps its file whichever way triage goes.** All three outcomes — escalate,
compose-from-tokens, build-local — are recorded here; only `escalate` produces a ticket. The
file is the run's record that a deviation was seen *and settled*, which is what a later run
reads to avoid re-opening it, so a compose-from-tokens decision that files nothing still
writes its file.

---

# gap-NNN: <short title>

**Category:** color | dimension | typography | component | icon
**Fingerprint:** `<stable hash of (category, observed value, nearest match)>` — used for
backlog dedup so a re-run doesn't refile.
**Recommendation:** escalate | compose-from-tokens | build-local *(user sets at triage)*
**Rationale:** <one line — **required** for compose-from-tokens and build-local; blank only
for escalate, whose reasoning goes in the ticket it produces>
**Triaged:** <YYYY-MM-DD, by whom>

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
- **Reusable across the product, or one-off to this design?** <the triage question, answered
  in a phrase — this is what separates escalate from the two local outcomes.>
- **Composition:** <compose-from-tokens only — the existing tokens/utilities that already
  express this, in arrangement (e.g. `bg-surface-2` + `gap-4` + `text-h3`), so the
  implementer never reaches for a raw value.> Every constituent must resolve ✅ on its own;
  one raw value in the composition means this is that value's gap instead.
- **Interim fallback used:** <the local recommendation carried in the page spec:
  value / component / file + codemod-friendly API note> — present when build-local.
- **Drawbacks / alternatives:** <if you can't articulate these, that's a stop-and-ask
  signal, not a reason to escalate.>

---

## Why the rationale line is mandatory

It is not paperwork. **The rationale plus the written-back ticket IDs are the entire dedup
story across runs.** A re-run regenerates the spec from scratch and will re-derive this same
deviation; the fingerprint tells it *this is the same gap*, and the rationale tells the human
*it was already argued out, here's why*. Without that line the second pass re-litigates a
settled decision with none of the context that produced it — and a triage checkpoint that
costs as much on run five as on run one is one people start clicking through.
