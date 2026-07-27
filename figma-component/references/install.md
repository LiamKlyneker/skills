# Install: wiring a host project

How to set up any repo — with a UI library or about to grow one — for `/tokens-init` + `/figma-component`.

## Prerequisites

- **Figma**: Professional plan or above with a **paid Dev or Full seat**. Hard requirement — `get_variable_defs` and usable rate limits need it (free/Starter seats get ~6 MCP calls/month). Code Connect is NOT required; it's an Org/Enterprise-only accelerator these skills exploit when present.
- **Repo**: Node project with Tailwind (v3 or v4). Storybook installed if you want stories — the skills write stories, they don't install Storybook.
- **Claude Code** with the **official** Figma MCP wired (below) — not Framelink. Settled; don't re-litigate. Framelink reads variables through the REST Variables API, which is **Enterprise-only**, so on a Professional Dev seat it cannot return semantic variable names. The official server's `get_variable_defs` can (node-scoped), and that is the feed these skills run on.

## 1. Wire the Figma MCP

Desktop server (Figma desktop app running, "Enable Dev Mode MCP Server" turned on in Preferences):

```json
// .mcp.json
{ "mcpServers": { "figma": { "type": "http", "url": "http://127.0.0.1:3845/mcp" } } }
```

`type` is required — an entry with a bare `url` is silently skipped at startup.

Or the remote server (no desktop app): `https://mcp.figma.com/mcp`, OAuth on first use.

Verify: `/mcp` in Claude Code shows figma connected with `get_metadata`, `get_variable_defs`, `get_screenshot`, `get_design_context`.

## 2. Install the skills

**Symlink** — don't copy — each skill into the host repo:

```
.claude/skills/
  figma-component -> <canonical>/figma-component
  tokens-init -> <canonical>/tokens-init
```

The `../_shared/…` references inside the skills resolve *past* the symlink into the canonical repo, which is where `ui-manifests.md` and `ui-standard.md` live. **Do not create a `_shared/` in the host repo** — that is the one thing that would make those paths ambiguous.

These two skills are **adapter-free**: they read only global reference files, so a repo can run them with no `.claude/project/` at all. If this project does need its own primitive homes and token traps named, that goes in `.claude/project/ui-manifests.md` (template: `install/gates/ui-manifests.template.md`), not in a `_shared/` copy.

## 3. First run

1. **Blank or token-less repo:** `/tokens-init <foundations-frame-url> [<type-specimen-url>]` — seed with the foundations/style-guide frame, **plus the type specimen frame if the ramp lives on its own** (it usually does; a colors-only seed yields no typography). Fallback: the most representative component. Then review the generated `tokens.css`, Tailwind mapping, and `.claude/skills/<repo>-ui/SKILL.md` — the profile is the contract for every future run; correcting it once is cheaper than correcting every build.
2. `/figma-component <component-node-url>` — first component. Expect the ❌-build path: nothing exists yet to reuse.
3. **Round two — the real test:** a second component that *reuses* round-one tokens/primitives. This exercises the ✅/⚠️ resolution logic a blank repo can't.

## 4. Designer contract

Share the **Designer contract** section of the canonical `_shared/ui-standard.md` with whoever owns the Figma file. Every hygiene report these skills emit measures against that checklist — the cleaner the file, the fewer checkpoint questions.
