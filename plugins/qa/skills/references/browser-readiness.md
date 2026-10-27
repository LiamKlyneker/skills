# Browser readiness

What a `qa` skill confirms before it drives a real browser: the consent the adapter records, and
that the Playwright MCP tools are in the session. `qa:prove-branch` and `qa:setup-states` both read
this file (`../references/browser-readiness.md`); neither restates it.

## Consent

The project adapter at `<repo-root>/.claude/project/adapter.md` → `## QA` carries the row
*Browser automation consent*. **`yes` records that the skill may drive a real browser against the
target.** The installer writes the `## QA` section only with that row reading `yes`. The skill reads
the row by name and asks for consent nowhere else.

## Playwright MCP readiness

Before any browser is driven, confirm that **the Playwright MCP tools are present in this session** —
`browser_navigate`, `browser_snapshot`, `browser_take_screenshot`, `browser_console_messages` and
`browser_network_requests` at least. When they are not, stop and name the remedy: add the
Playwright MCP server, start a fresh session, and run the skill again. The shape is

```bash
claude mcp add playwright -- npx @playwright/mcp@latest --isolated --storage-state <path to a session.json>
```

and the exact flags are the ones the server documents at run time. **Isolated mode plus a
storage-state file is how a saved session reaches the browser**: the browser holds its profile in
memory, starts signed in from the scenario's `session.json`, and writes nothing back to it. The
server runs headed unless the developer asks for headless, so the developer can watch.

**When the skill dispatches drivers, one driver per flow means one isolated browser context per
flow, loaded with that flow's role's session.** Confirm the connected server gives each driver its
own context. When it can give the session only one browser, two drivers would act in the same page,
so dispatch the drivers one at a time, in flow order, and say why. A role whose session the server
cannot load is a stop that names the role.

Never install the server or a browser into the project, and never add the server without a yes.
