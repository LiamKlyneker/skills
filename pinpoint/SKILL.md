---
name: pinpoint
description: Locate something in the codebase via a throwaway Explore subagent and report back only what's needed to continue. Use when you want to find where/how something is implemented without polluting the main thread with searches and file dumps.
argument-hint: [what to locate]
disable-model-invocation: true
---

Locate the following in the current codebase and report back concisely: **$ARGUMENTS**

Delegate the search to a single subagent so the exploration noise never enters this conversation:

- Use the **Agent** tool with `subagent_type: "Explore"` and `model: "haiku"`.
- Thoroughness: "medium" — bump to "very thorough" only if the target plausibly spans multiple areas or naming conventions.
- Do **not** read, grep, or glob files yourself. The whole point is to keep this thread clean: spawn the subagent, then relay its result.

The goal is to **anchor the area, not do a deep dive**. Shallow is fine — I'll drill into specifics on the main thread once I know where we're working. Tell the subagent to return only:

1. **Primary location(s)** — the file path(s), with line numbers, for the area asked about.
2. **Key symbols** — the main component / function / hook / type name(s) that live there.
3. **One-line orientation** — a single sentence on what that file/area is responsible for, so the main thread has context.

Do not ask it to trace call graphs, wiring, or edge cases — that's what I'll follow up on. Keep it skimmable: paths and names over prose. If nothing matches, say so and suggest the closest candidates.

If `$ARGUMENTS` is empty, ask what to pinpoint before doing anything.
