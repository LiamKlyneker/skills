# figma

`figma-to-spec`, packaged as a Claude Code plugin, plus the
`figma-region-extractor` agent it spawns per region.

Named `figma`, not `figma-to-spec` — plugin skills are invoked as
`plugin:skill`, so a plugin named after its own skill would double up as
`/figma-to-spec:figma-to-spec`. `figma` yields the clean `/figma:figma-to-spec`.

## Layout

```
plugins/figma/
  .claude-plugin/plugin.json
  skills/
    _shared -> ../../../_shared                    # symlink
    figma-to-spec/
      agents/figma-region-extractor.md -> ../../../agents/figma-region-extractor.md
  agents/figma-region-extractor.md
```

Nothing sits at the plugin root — same reason as `plugins/prd-workflow/`: a
root `SKILL.md` alongside a `skills/` subdirectory registers twice.

## Decisions

Same three calls as `plugins/prd-workflow/` (see its README for the full
reasoning and evidence — repeated here only where this plugin differs):

- **No `version` in `plugin.json`.** Plain `claude plugin validate` passes with
  the missing-`version` warning as the only warning; `--strict` fails on that
  warning by definition and is expected to.
- **`skills/_shared -> ../../../_shared`.** Same depth as `prd-workflow`'s
  placement (`plugins/<name>/skills/` is three levels below the repo root
  either way), so the identical relative target is correct verbatim.
- **Compat shims.** The top-level `figma-to-spec` name survives as a symlink
  into `plugins/figma/skills/figma-to-spec`, so the three config-dir consumer
  links (`~/.claude/skills/figma-to-spec`, `~/.claude-schmiede/skills/figma-to-spec`,
  `~/.claude/agents/figma-region-extractor.md`) keep resolving unchanged.

### The nested agent shim

Unlike `prd-workflow` — where the nested shim existed only because two
*consumer repos* linked the inner path — this plugin needs one for a second,
independent reason found by checking rather than assuming: `~/.claude/agents/figma-region-extractor.md`
itself resolves straight to `figma-to-spec/agents/figma-region-extractor.md`
(not through any intermediate symlink), and the skill's own reference docs
(`references/phases.md`, `references/resolution-rules.md`) link the agent as
`../agents/figma-region-extractor.md` from inside the skill. Both needed the
file to still be reachable at that inner path after the real file moved to
`plugins/figma/agents/`, so `skills/figma-to-spec/agents/figma-region-extractor.md`
is a symlink back to it — same shape as `prd-workflow`'s
`skills/work-on-prd/agents/prd-worker.md`.

## Out of scope

`figma-component/` and `tokens-init/` are untouched — deprecated, unlinked,
and staying that way until #9 and #14 decide what to salvage.
