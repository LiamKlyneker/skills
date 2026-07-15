# Install: wiring a host project

How to set up any repo — with a UI library or about to grow one — for `/tokens-init` + `/figma-component`.

## Prerequisites

- **Figma**: Professional plan or above with a **paid Dev or Full seat**. Hard requirement — `get_variable_defs` and usable rate limits need it (free/Starter seats get ~6 MCP calls/month). Code Connect is NOT required; it's an Org/Enterprise-only accelerator these skills exploit when present.
- **Repo**: Node project with Tailwind (v3 or v4). Storybook installed if you want stories — the skills write stories, they don't install Storybook.
- **Claude Code** with the Figma MCP wired (below).

## 1. Wire the Figma MCP

Desktop server (Figma desktop app running, "Enable Dev Mode MCP Server" turned on in Preferences):

```json
// .mcp.json
{ "mcpServers": { "figma": { "url": "http://127.0.0.1:3845/mcp" } } }
```

Or the remote server (no desktop app): `https://mcp.figma.com/mcp`, OAuth on first use.

Verify: `/mcp` in Claude Code shows figma connected with `get_metadata`, `get_variable_defs`, `get_screenshot`, `get_design_context`.

## 2. Install the skills

Copy or symlink into the host repo:

```
.claude/skills/
  figma-component/   (including references/)
  tokens-init/
  _shared/           (ui-manifests.md, ui-standard.md)
```

The `../_shared/` references inside the skills depend on this layout.

## 3. First run

1. **Blank or token-less repo:** `/tokens-init <foundations-frame-url>` — seed with the foundations/style-guide frame (fallback: the most representative component). Then review the generated `tokens.css`, Tailwind mapping, and `.claude/skills/<repo>-ui/SKILL.md` — the profile is the contract for every future run; correcting it once is cheaper than correcting every build.
2. `/figma-component <component-node-url>` — first component. Expect the ❌-build path: nothing exists yet to reuse.
3. **Round two — the real test:** a second component that *reuses* round-one tokens/primitives. This exercises the ✅/⚠️ resolution logic a blank repo can't.
4. Fidelity check when ready: run `verify-ui` (needs `claude --chrome`).

## 4. Designer contract

Share the **Designer contract** section of `_shared/ui-standard.md` with whoever owns the Figma file. Every hygiene report these skills emit measures against that checklist — the cleaner the file, the fewer checkpoint questions.
