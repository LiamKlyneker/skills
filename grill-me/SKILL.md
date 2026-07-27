---
name: grill-me
description: Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree. Invoke /grill-me to stress-test a plan or get grilled on a design.
disable-model-invocation: true
---

# Grill Me

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time.

If a question can be answered by exploring the codebase, explore the codebase instead.

This skill grills **inline** — it explores on this thread and keeps the whole interview in one place. For a plan that crosses a service boundary, spans several areas, or already has a design spec to grill against, use `deep-grill` instead: it fans the exploration out to recon subagents first, so the questions arrive grounded rather than guessed.

## Context Loading

If the `scoped-context` skill is available in this project, use it to load relevant `CONTEXT.md` files before beginning the interview. This gives you architectural context to ask better, more informed questions. If scoped-context is not available, proceed without it.
