# Architecture decision records

Why a handful of this repo's rules are the way they are — specifically the ones whose
reasoning exists only in a commit message, and which a reader would therefore undo in
good faith. `CLAUDE.md` and `.claude/project/adapter.md` state the rules; these records
state the argument behind them.

Adopted from [`mattpocock/skills`](https://github.com/mattpocock/skills), and adopted
**light** on purpose. An ADR here is a page. If writing one starts to feel like a
project, write less.

These files are documentation, not loaded config — no session discovers `docs/adr/`.
They are for a human, and for an agent that has been told to read them.

## When a decision earns a record

- **It reverses an earlier decision.** The strongest case by far: the original reasoning
  is still sitting in the history, and the next reader who finds it will restore the rule
  from the commit that introduced it.
- **It has a rejected alternative worth naming**, so the alternative is not re-proposed
  as if it had never been considered.
- **It is a standing disagreement with prior art** that we deliberately do not resolve.

A rule that is simply true and uncontested does not need one. It belongs in `CLAUDE.md`
or the adapter, and stops there.

## Convention

- **Filename**: `NNNN-kebab-case-title.md` — four digits, zero-padded.
- **Numbering**: monotonic, allocated once, never reused. Gaps are never backfilled. A
  number belongs to its record permanently, including after that record is superseded.
- **Header**: the first lines of every file, in this order.

  ```markdown
  # ADR NNNN — Title

  - **Status**: Accepted
  - **Date**: YYYY-MM-DD
  - **Context**: the PRD, issues, or commit this comes out of
  ```

  Optional fourth line: `**Supersedes**` / `**Superseded by**` / `**Reverses**`.
- **Status vocabulary**, and only this: `Accepted`, or `Superseded by ADR NNNN`. There is
  no `Proposed` — a decision that has not been made yet is a conversation, not a record.
- **Supersede by appending, never by editing.** Write a new record at the next number
  with `**Supersedes**: ADR NNNN` in its header. Then the old record gets *exactly one*
  edit: its `Status` line becomes `Superseded by ADR NNNN`. Its body stays as written,
  wrong and all — the reasoning that used to be right is the entire reason the file is
  still on disk. Rewriting an ADR is how a repo loses an argument it has already had.
- **Sections are the record's own business.** Most want some shape of Context, Decision,
  Consequences, Rejected alternatives. Nothing enforces it.
- **State the losing reasoning fairly, first.** A record that makes the decision it
  reverses look careless is an invitation to reverse it back on the same grounds.

## Index

| ADR | Title | Status |
|---|---|---|
| [0001](0001-version-the-plugins-and-enforce-the-bump.md) | Version the plugins, and enforce the bump | Accepted |
| [0002](0002-the-lk-plugin.md) | The `lk` plugin, and why `install-skills` is not in it | Superseded by ADR 0008 |
| [0003](0003-invocation-policy.md) | Invocation is the isolation boundary | Accepted |
| [0004](0004-shared-reference-and-skill-dependencies.md) | `_shared/` files are shared; skills are not | Accepted |
| [0005](0005-qa-is-an-issue-not-a-committed-document.md) | The QA pass is a per-run item, not a committed document | Superseded by ADR 0006 |
| [0006](0006-sub-issues-and-qa-as-a-prd-comment.md) | A PRD's children are sub-issues, and its QA pass is a comment on it | Superseded by ADR 0009 |
| [0007](0007-a-marketplace-not-an-estate-manager.md) | This repo publishes a marketplace; it does not manage the estate | Accepted |
| [0008](0008-prd-qa-skills-belong-to-prd-workflow.md) | The PRD-QA skills belong to `prd-workflow`, not to `lk` | Accepted |
| [0009](0009-the-qa-comment-is-a-parse-contract.md) | The QA comment is a parse contract, and the receipt comes back | Accepted |
| [0010](0010-one-distribution-one-dev-mode.md) | One distribution, one dev mode | Accepted |
