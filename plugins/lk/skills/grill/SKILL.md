---
name: grill
description: Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree in rounds. Invoke /lk:grill to stress-test a plan or get grilled on a design.
disable-model-invocation: true
---

# Grill Me

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Map it as a **design tree**: every decision branches into the decisions that hang off it.

## Rounds and the frontier

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled — the questions you can ask *now* without guessing at answers you haven't heard yet. Ask the whole frontier in one round, then wait for my answers before the next.

A question whose answer depends on another question still open in this round belongs to a **later** round, not this one. Each round of answers reshapes the tree: settled decisions push the frontier outward and unblock what depended on them. Recompute the frontier and ask again.

**A round is numbered questions, never a form.** Each carries its own recommended answer. Asking me to fill in a table, mark up a list, or confirm a batch of rows is not a round — it hands the reconciliation back to me, which is the work you are here to do.

Format a round like this:

```
❓ **Q1** — **<question title>**: <question body — may be several paragraphs, and may offer choices>

➡️ <your recommended answer, and one line on why>

---

❓ **Q2** — **<question title>**: <question body>

➡️ <your recommended answer, and one line on why>
```

## Facts are your job, never mine

If a question can be answered by exploring the codebase, explore instead of asking. Never ask me for something you could look up yourself.

**Don't block on a lookup.** A running exploration is just an unsettled prerequisite: only the questions downstream of it wait. Ask the rest of the frontier now, and fold the answer in when it lands.

## Done

The interview is done when the frontier is empty — every branch of the design tree visited, nothing left silently assumed. **Do not act on the plan until I confirm we have reached shared understanding.**

## Inline vs deep

This skill grills **inline** — it explores on this thread and keeps the whole interview in one place. For a plan that crosses a service boundary, spans several areas, or already has a design spec to grill against, use `deep-grill` instead: it fans the exploration out to recon subagents first, so the questions arrive grounded rather than guessed.

## Context Loading

If the `scoped-context` skill is available in this project, use it to load relevant `CONTEXT.md` files before beginning the interview. This gives you architectural context to ask better, more informed questions. If scoped-context is not available, proceed without it.
