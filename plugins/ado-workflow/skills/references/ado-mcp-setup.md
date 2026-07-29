# ADO MCP Setup

How every `ado-workflow` skill reaches Azure DevOps. Cited by the readiness probe in
`ado-workflow:to-spec`, `ado-workflow:to-spec-tasks`, `ado-workflow:next-task-to-implement`
and `ado-workflow:work-on-spec`.

The plugin carries this file so the probe's pointer resolves from inside any of its skills
(`../references/ado-mcp-setup.md`) and from a marketplace install cache alike — no skill
borrows a reference out of a sibling skill's directory.

**The organisation is not written down here.** It comes from the project adapter at
`<repo-root>/.claude/project/adapter.md` → `## Repo` → `### Azure DevOps` → *Organisation*.
Read it and substitute it wherever `<organisation>` appears below.

Package: `@azure-devops/mcp` · scope flag: `-d all`.

## The server key must be `ado`

Register the server under the key **`ado`**, exactly, lowercase. Nothing else works.

An MCP server's key *is* its tool namespace: a server registered as `<key>` exposes its tools
as `mcp__<key>__*`. Every skill in this plugin calls `mcp__ado__…` by name, so the key is a
hard contract, not a label you get to choose.

## Register it

Project scope — shared with anyone who opens this repo, written to `.mcp.json` at the repo
root:

```
claude mcp add ado -s project -- npx -y @azure-devops/mcp@latest <organisation> -d all
```

`-s local` (the default) keeps it to this machine + this project; `-s user` makes it global.
Prefer project scope: the org is a property of the repo, not of the machine.

By hand, the same thing — merge into an existing `mcpServers` block rather than replacing it:

```json
{
  "mcpServers": {
    "ado": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@azure-devops/mcp@latest", "<organisation>", "-d", "all"],
      "env": {}
    }
  }
}
```

The key `ado` on the third line is the one that matters. Both routes are equivalent — the CLI
writes exactly this file.

## Then verify

1. Reload or restart the session; a newly registered stdio server is not live in the session
   that added it.
2. Probe: call `mcp__ado__core_list_projects` with `top: 1`. A response means the server is
   active, authenticated, and reachable under the name the skills expect.
3. Record it in memory — `ADO MCP active for this project` — so later runs skip the probe.

## When the probe fails but the server is fine

This is the failure worth knowing by heart, because it looks like nothing.

Register the same server under any other key — `azure-devops`, `devops`, whatever a package
example or a previous config used — and everything about it works. It starts, it
authenticates, `claude mcp list` shows it connected. Its tools simply arrive as
`mcp__azure-devops__core_list_projects` instead of `mcp__ado__core_list_projects`.

Every skill in this plugin then fails its readiness probe. And the probe cannot tell "no such
tool" from "no such server", so it reports the server as **unconfigured** — sending you to set
up a server that is already running. Nothing in the output ever says *misnamed*, which is why
this costs an afternoon rather than a minute.

**The tell:** the probe says unconfigured, but `claude mcp list` shows the server connected.
That combination means the key, and only the key, is wrong.

**The fix** is a rename, nothing more — the command, the args and the authentication are
already correct:

```
claude mcp remove <wrong-key>
claude mcp add ado -s project -- npx -y @azure-devops/mcp@latest <organisation> -d all
```

or edit the key in place in `.mcp.json`. Reload afterwards.

## Why MCP, and not the CLI or REST

Access is **MCP only**. The `az` CLI / REST route was considered and rejected: it authenticates
with a token that expires, and an expiry lands mid-loop — halfway through an orchestrated run,
after work items have been created and a branch exists. That is a failure the loop cannot
recover from on its own, and it is not worth trading for the convenience of `curl`.

## Other MCP clients

The same server, the same key. Any other MCP client takes the same `command` + `args` under
whatever its config calls `mcpServers` (`type: "stdio"` may be implicit). The key rule above is
client-independent: whatever the client is, it derives the tool namespace from the key, so the
key stays `ado`.
