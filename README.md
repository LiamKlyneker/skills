# Agent Skills

A collection of my agent skills... more to come soon!

## Agents

Some skills ship a custom subagent alongside `SKILL.md` + `references/`. The agent file
carries the parts of the contract that never change between calls, so the orchestrator only
passes the per-call inputs. It lives inside the skill directory (one source of truth) and is
symlinked into the agents directory to be spawnable by type.

| Agent | Skill | Install | Notes |
|---|---|---|---|
| `figma-region-extractor` | `figma-to-spec` (Phase B) | user-scoped | Pinned to Sonnet; write tools denied. Detachable — if not installed, Phase B reads the same file and pastes its body into a `general-purpose` agent. |

```bash
ln -sfn "$PWD/figma-to-spec/agents/figma-region-extractor.md" \
        ~/.claude/agents/figma-region-extractor.md
```

Three things worth knowing before adding another one:

- **A newly installed agent takes a few minutes to register.** It does not need a restart,
  but `subagent_type` will not resolve immediately after you write the file. Any skill that
  spawns an agent by type should check availability and fall back rather than assume.
- **Agents have no `disable-model-invocation`.** A `description` that reads like a capability
  advertisement invites auto-delegation from unrelated sessions, bypassing the skill's setup
  phase. Write it as a caller contract ("internal to X, never invoke directly"), and where
  the agent depends on inputs only the orchestrator can supply, make it hard-STOP when they
  are missing.
- **The body replaces the system prompt, but not everything comes from there.** Measured
  with a throwaway probe agent: git conventions (including the `Co-Authored-By` trailer and
  the never-commit-unless-asked rule), the prefer-dedicated-file-tools guidance, `CLAUDE.md`,
  and the date/user context all still reach a custom subagent — they arrive via tool
  descriptions and injected context rather than the system prompt. What measurably does
  **not** survive is the honesty/evidence/don't-fabricate guidance. Restate that in any
  agent whose job is to report results; don't waste lines restating the rest.
