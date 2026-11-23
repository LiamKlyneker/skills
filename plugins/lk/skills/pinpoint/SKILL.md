---
name: pinpoint
description: Locate something in the codebase via a throwaway Explore subagent and report back only what's needed to continue. Use when you want to find where/how something is implemented without polluting the main thread with searches and file dumps.
---

Locate the following in the current codebase and report back: **$ARGUMENTS**

Delegate the search to a single subagent so the exploration noise never enters this conversation:

- Use the **Agent** tool with `subagent_type: "Explore"` and `model: "haiku"`.
- Thoroughness: "medium" — bump to "very thorough" only if the target plausibly spans multiple areas or naming conventions.
- Do **not** search yourself: no grep, no glob, no reading files to find the target. Spawn the subagent, then relay its report. Reading a `file:line` range the report cites is not a search, and **Relying on a lead** below requires it.

This is a **specialized locator**. Its report is a set of **leads, not facts**: it finds the area and copies what is there, and it does not describe or interpret. Give the subagent these guardrails, then the report shape:

**Grounding (say this to the subagent):**

- Every line of the report is a path, an identifier, a listing, or a line copied from a file with its `file:line`. Write no sentence of your own about what the code does, contains, or is for.
- If you'd be inferring, omit it — prefer omission over guessing.
- Copy identifiers exactly; never paraphrase a name.
- Do **not** trace data flow, explain "why", or claim feature flags / conditional rendering / edge cases. That's for the main thread to follow up on.

**Report shape (only what applies):**

1. **Location(s)** — file path(s) with line numbers for the exact thing asked about.
2. **Key symbols** — the main component / function / hook / type name(s) that live there.
3. **Signature** — one copied line: the props type, function, or hook signature of the primary symbol.
4. **Used by** — grep the primary symbol and list the `file:line` sites that import or render it (this is literal grep output, not analysis). Cap at ~10 sites; if there are more, list the first 10 and give the total count instead of the full list.
5. **Neighbors** — the other files in the containing folder, listed (`ls`-level), so the area's neighborhood is visible.
6. **Evidence** — lines copied verbatim from the source, each with its `file:line`, and nothing else: the doc comment on the primary symbol if it has one, the file's export lines, and the fields of the primary props or parameter type. Cap at ~15 lines; if there are more, copy the first 15 and give the count of the rest.

Keep it skimmable — paths, names, and copied lines, no prose. If nothing matches, say so and suggest the closest candidates.

## Relaying the report

- Start the relay with this line, exactly: `Unverified leads. Read the cited lines before you rely on any claim.`
- Pass the report on unchanged. Shorten it only by dropping a whole section. Never reword a line, and add no description of your own.
- A sentence in the report about what the code does or contains, with no copied line under it, is the subagent's guess. Mark it `(unquoted)` in the relay.

## Relying on a lead

The report holds two kinds of line. A **pointer** — a path, a line number, a **Used by** site, a neighbor — verifies itself when you open it. A **content line** — the **Signature**, an **Evidence** line, any statement about what the code does or contains — does not.

- Before a content line goes into a plan, a ticket, an edit, or an answer, read its cited `file:line` range. Read at that moment, not at relay.
- An `(unquoted)` statement has no range to read. Read the file at its **Location**, or leave the statement out.
- If the lines do not support the lead, say in one sentence which lead was false and what the lines say, then continue from what you read. Run `pinpoint` again only if the location itself was wrong.

If `$ARGUMENTS` is empty, ask what to pinpoint before doing anything.
