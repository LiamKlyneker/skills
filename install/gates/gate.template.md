# `<Gate Name>` (HARD GATE) — TEMPLATE

Copy to `<repo-root>/.claude/project/<gate>.md` and register it in the adapter's `## Project gates` with its trigger. Skills find it through that registry and never by name.

A gate exists to catch **one class of improvisation** that no compiler, linter or test will catch, in a place this project has actually been burned. If you can't name the silent failure it prevents, you don't need a gate — you need a line in the adapter.

The reference case is an API-contract manifest: iOS code calling a route or field the committed contract doesn't ship, or sending it in the wrong auth mode. Nothing fails loudly; it just 401s or quietly drops a field.

## What it catches

`<the silent-failure class, in one paragraph. Name the real incident if there was one — a gate justified by a story gets run; a gate justified by principle gets skipped.>`

## When it runs — and when it may be skipped

`<the trigger, stated so it can't be self-exempted by feel. The pattern that works: an inclusive trigger ("any plan whose code does X — including a new operation against something the code already uses"), then a narrow explicit skip ("only for plans that do no X at all"), then the anti-self-exemption line: if you can't say "the planned code does zero X," run the gate.>`

The **new operation on an already-used resource** is the case that bites, whatever the domain — it isn't a schema or a contract change, so it slips past every "did the shape change?" check.

## Feedstock

`<which explorer or source pre-populates the rows, if any — a recon agent named in the adapter, a generated spec, a policy console. A gate that confirms and interrogates a feedstock table beats one that re-derives it blind. Delete this section if the rows are built by hand.>`

## Rows

Enumerate **every** `<unit>` the planned code touches, one row **per operation actually exercised** — never one row per `<unit>`, since `<a resource covered for one operation is not covered for another>`. For each row, resolve before the gate closes:

- **`<dimension 1>`** — `<what to determine, and what going wrong in *either* direction costs>`.
- **`<dimension 2>`** — `<the specific check, not the vague one: not "does it look right" but "does <exact artifact> contain <exact thing>">`.
- **Errors surfaced, not swallowed** — `<how failures must reach the caller in this stack; a swallowed error is what lets the gap ship invisibly>`.

This is a **hard gate**: do not close it while any row is ⚠️ or ❌. Present the manifest back as a table and get confirmation:

| `<unit>` | Operation | `<dimension 1>` | `<dimension 2>` | Status |
|---|---|---|---|---|
| `<example>` | `<op>` | `<value>` | ✅ | ✅ covered |
| `<example>` | `<op>` | `<value>` | ❌ | ⚠️ gap — `<what unblocks it>` |

Status ∈ ✅ covered / ⚠️ gap (needs a fix or an upstream issue) / ❌ unchecked (not yet verified — must resolve). Only after every row is ✅ is the gate done.
