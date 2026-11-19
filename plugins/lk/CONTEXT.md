# lk plugin

## The shared review reference

`skills/references/pr-review-posting.md` holds only text that is identical in `human-review` and
`proposal-review`: PR resolution, project facts, the discussion, the drafts and the post, and the
re-review detection and base lookup. Each skill points to it at the step that uses a section.

A change that would need an "if proposal review" (or "if human review") branch inside the reference
does not go into it. The skill that diverges takes its own copy of that text into its `SKILL.md`,
and the reference keeps the part that is still identical. A sentence that only one skill can say,
such as how many subagents it spawns, stays in that skill's `SKILL.md`.

`pr-feedback` uses §Invocation and input and nothing else in the reference. It posts nothing, so the
discussion, drafts, post and re-review sections do not apply. It keeps its own copy of the project
facts because it runs in repos with no adapter, falling back to the git remote, and that fallback
would be an "if pr-feedback" branch in the shared section.
