# Design brief template

The shape `prototype-to-spec` writes and `deep-grill` reads. **The `##` headings are fixed** —
the grill keys on them to tell a fact from a question — and everything inside them is the
project's and the prototype's vocabulary.

A brief is **disposable**. It describes one ticket against one prototype at one SHA, it is
written to a gitignored directory, and it is regenerated rather than updated. Nothing reads it
after the grill.

---

```markdown
# Design brief — <ticket> · <prototype name>
Source: <owner/repo>@<sha> (<path>) · Preview: <url> · Catalog: <fingerprint> · Generated: <YYYY-MM-DD>

## Scope

Kept: uc1-s1, uc1-s2, uc1-s4 …
Dropped: uc1-s8 (edit drawer — separate ticket), uc2-* (questions step — not in AC) …

## Overrides (ticket wins)

- ~~Range picker closes on first click~~ → overridden by ticket: stays open until both
  endpoints are chosen.

## Screens

### uc1-s4 — <step title>
Screenshot: <raw URL at the pinned SHA>
Annotations:
- <annotation text> `component:<tag>`

## Component states

### <ComponentName>
State page: <url>
- `<state>` — <description>

## Business rules & edge cases

- <rule> *(observed in uc1-s4)*

## Element → DS mapping

| Element | Seen in | Proposed | Confidence | Notes |
|---|---|---|---|---|
| value chips w/ remove | uc1-s4 | MultiSelectPicker | likely | prototype hand-rolls pills |
| click-away overlay | uc1-s2 | Popover (built-in) | exact | do not port the fixed div |
| saved-view switcher | uc1-s6 | — | OPEN | no catalog match |

## Tokens

| Prototype token | Code token | Status |
|---|---|---|
| `var(--color-surface-raised)` | the raised-surface semantic token | ✅ resolves |
| `var(--color-slate-200)` (raw) | — | ⚠ no equivalent, do not invent |

## DS gaps (proposed, not filed)

- **saved-view switcher** — nothing in the catalog composes it. Would file against
  <the adapter's DS-gap backlog>. **Not filed.**

## Out of scope

- uc1-s8 (edit drawer) — separate ticket
- uc2-* (questions step) — not named in the AC

## Rules to cite

- `<rule name>` — from `<usage-rules source>`
```

---

## Rules the template does not show

- **Every heading is present, every time.** A section with nothing in it says
  `None — <why>`. An absent heading and an empty one are indistinguishable to the grill, and
  "the prototype had no business rules" and "nobody looked" are very different facts.
- **`Source:` is required and is a pinned SHA**, never a branch name. A brief that cannot say
  which commit it describes cannot be checked against anything later.
- **Screenshots are linked at that SHA, never embedded.**
- **`## Scope` carries `⚠ inferred`** where the ticket named no component and the steps were
  scored. The scored list — every step, with its score, not only the kept ones — goes under the
  heading so the guess is checkable at a glance.
- **`## Overrides` keeps both halves** — the prototype's text struck through, the ticket's
  text after it. An override with the original deleted reads as the design.
- **Confidence is `exact`, `likely` or `OPEN`, and nothing else.** They are the grill's
  interface: `exact` is never asked about, `likely` gets one batched confirmation, `OPEN` is a
  round-one question. Promoting a guess to `exact` is the one error here that reaches
  implementation unchallenged.
- **A rule is cited by name and by the source it came from.** The adapter's usage-rules row may
  name several sources, and two of them may name a rule the same thing. Cite, never restate.
- **Nothing in this brief is filed anywhere.** A proposed DS gap says where it *would* go and
  that it has not gone there.
