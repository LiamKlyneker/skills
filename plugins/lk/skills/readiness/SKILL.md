---
name: readiness
description: >
  One round of questions after a grill, or against an existing PRD or spec, that surfaces what a
  worker would be missing before an unattended run: missing context, credential or access, external
  dependency, ambiguous acceptance criterion. Prints a `## Readiness` block into the conversation
  and files nothing. Invoke /lk:readiness, optionally with a PRD or spec reference.
disable-model-invocation: true
---

# readiness

**Ask what a worker with no human beside it would stall on, once, and write the answers down.**

A grill settles the design. It does not ask whether a cold worker can start: whether it has the context, the access, the tickets it depends on, and acceptance criteria it can check. This skill asks that, in one round, and prints the result as a `## Readiness` block that `/prd-workflow:to-prd` carries into the PRD.

**It files nothing.** No issue, no comment, no file, no label. Its only output is the block in the conversation. The only tracker read is the optional body fetch in step 1.

## 1. Find what to check

- **A reference was passed** (PRD or spec number, URL, ticket key, or a path): fetch its body per `../_shared/ticket-source.md` and treat that body as the plan. That is the only tracker read this skill makes.
- **No reference**: the plan is the conversation so far, normally a grill that just ended. Do not re-open the grill's decisions.

## 2. Ask one round over four classes

Read the plan and list every item a worker could stall on, sorted into these classes:

| Class | An item is |
|---|---|
| Missing context | a fact the worker needs and the plan does not state: a file, a convention, a decision's reason, an example |
| Credential or access | a key, login, permission, environment or account the worker cannot get for itself |
| External dependency | work in another ticket, repo, team or system that must land first |
| Ambiguous acceptance criterion | a criterion two readers would check differently, or one that names no observable result |

Ask the whole list as **one round**: numbered questions, grouped by class, each stating the item and a recommended answer. For every item the developer picks exactly one of three answers:

1. **Give it now**: they supply the missing fact, the access detail, the ticket id or the sharpened criterion in their reply.
2. **Make it an external step**: it stays a manual action outside the editor, recorded for the task's `## External steps` or `## Blocked by`.
3. **Defer the group**: the whole class, or the item's group, is left open on purpose and will not block the run's start.

A class with no item still gets its sub-list, marked `None`. Do not invent items to fill a class, and do not open a second round: an answer that raises a new item is recorded as an open item.

## 3. Print the block

Print this into the conversation, and nothing else after it but the next command:

```
## Readiness

### Missing context
- <item> — given: <the fact>
- <item> — external step: <what the developer does>
- <item> — deferred

### Credential or access
- None

### External dependency
- <item> — external step: <ticket, repo or team>

### Ambiguous acceptance criterion
- <criterion> — given: <the sharpened criterion>
```

One line per item with its recorded answer: `given: …`, `external step: …`, or `deferred`. An item the developer has not answered yet is `open`. The block ends with the next command: `/prd-workflow:to-prd` when it follows a grill with no PRD yet, or `/prd-workflow:to-prd <ref>` to merge it into an existing PRD.
