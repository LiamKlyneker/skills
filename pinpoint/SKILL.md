---
name: pinpoint
description: Locate something in the codebase via a throwaway Explore subagent and report back only what's needed to continue. Use when you want to find where/how something is implemented without polluting the main thread with searches and file dumps.
---

Locate the following in the current codebase and report back: **$ARGUMENTS**

Delegate the search to a single subagent so the exploration noise never enters this conversation:

- Use the **Agent** tool with `subagent_type: "Explore"` and `model: "haiku"`.
- Thoroughness: "medium" — bump to "very thorough" only if the target plausibly spans multiple areas or naming conventions.
- Do **not** read, grep, or glob files yourself. The whole point is to keep this thread clean: spawn the subagent, then relay its result.

This is a **specialized locator**: it should surface more grounded detail than the main thread would stop to gather, but it stays out of interpretation. The rule is _report facts you can copy, not conclusions you'd have to reason to_. Give the subagent these guardrails, then the report shape:

**Grounding (say this to the subagent):**

- Ground every line in something you actually read, grepped, or listed. If you'd be inferring, omit it — prefer omission over guessing.
- Copy identifiers exactly; never paraphrase a name.
- Do **not** trace data flow, explain "why", or claim feature flags / conditional rendering / edge cases. That's for the main thread to follow up on.

**Report shape (only what applies):**

1. **Location(s)** — file path(s) with line numbers for the exact thing asked about.
2. **Key symbols** — the main component / function / hook / type name(s) that live there.
3. **Signature** — one copied line: the props type, function, or hook signature of the primary symbol.
4. **Used by** — grep the primary symbol and list the `file:line` sites that import or render it (this is literal grep output, not analysis).
5. **Neighbors** — the other files in the containing folder, listed (`ls`-level), so the area's neighborhood is visible.
6. **One-line orientation** — a single sentence on what the area is responsible for.

Keep it skimmable — paths, names, and signatures over prose. If nothing matches, say so and suggest the closest candidates.

If `$ARGUMENTS` is empty, ask what to pinpoint before doing anything.
