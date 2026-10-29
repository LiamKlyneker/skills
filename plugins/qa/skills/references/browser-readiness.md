# Browser readiness

What a `qa` skill confirms before it drives a real browser: the consent the adapter records, the
HTTP Basic Auth in front of the preview, and that the Playwright MCP tools are in the session.
`qa:prove-branch` and `qa:setup-states` both read this file (`../references/browser-readiness.md`);
neither restates it.

## Consent

The project adapter at `<repo-root>/.claude/project/adapter.md` → `## QA` carries the row
*Browser automation consent*. **`yes` records that the skill may drive a real browser against the
target.** The installer writes the `## QA` section only with that row reading `yes`. The skill reads
the row by name and asks for consent nowhere else.

## Preview Basic Auth

Some previews sit behind **HTTP Basic Auth**, in front of the app's own sign-in. A saved session does
not cover it: a storage-state file holds cookies and local storage, and Basic Auth credentials are
neither. The optional `## QA` row *Preview basic auth* names two environment variables, the username
and then the password. **Absent means the preview has no Basic Auth.**

### Detect the challenge

The first request the skill makes against the target is the check. **A `401` whose
`WWW-Authenticate` header names the `Basic` scheme is a Basic Auth challenge**, not a target that
does not answer. The header can appear more than once, and any one of them naming `Basic` counts.
Then:

1. **The row is absent**: stop. Say the target asks for HTTP Basic Auth, name the *Preview basic
   auth* row, and tell the developer to add it with `/qa:setup` (or by hand) naming two variables,
   export them, and run again.
2. **The row is present and a named variable is unset or empty in the shell**: stop and name the
   variable. Tell the developer to set it and run again. Never ask for a value.
3. **The row is present and both variables are set**: repeat the request with the credentials. A
   second `401` is a stop that says the preview rejected them. **Do not retry with changed input.**
   When the preview accepts them and `.qa-scenarios/browser-config.json` is missing, write it now,
   as *The browser* below says, after creating the scenario directory as `qa:prove-branch` → *The
   scenario directory* says — and stop there.

A target that does not challenge needs nothing here, whether or not the row is present: no
variable is checked and no config is written.

### Every request the skill makes

Every `curl` against the target — the readiness check, the session check, the `api` sign-in — carries
the credentials **by variable name**, so the shell expands them and the command text never holds a
value:

```bash
curl -u "$<USERNAME_VAR>:$<PASSWORD_VAR>" …
```

Never add `-v`, `--trace` or any other option that echoes the request: the `Authorization` header
carries the pair.

### The browser

Playwright MCP takes the credentials from a **config file** given at launch, as
`browser.contextOptions.httpCredentials`. The file has no variable substitution, so the skill writes
it from the two variables with one command that prints nothing, into the scenario directory
(`qa:prove-branch` → *The scenario directory*), which is excluded from git and readable only by the
developer's user:

```bash
cfg="$(git rev-parse --show-toplevel)/.qa-scenarios/browser-config.json"
rm -f "$cfg"
U_VAR=<USERNAME_VAR> P_VAR=<PASSWORD_VAR> node -e '
  const fs = require("fs"), u = process.env[process.env.U_VAR], p = process.env[process.env.P_VAR];
  if (!u || !p) { console.error("unset"); process.exit(1); }
  fs.writeFileSync(process.argv[1],
    JSON.stringify({ browser: { contextOptions: { httpCredentials: { username: u, password: p } } } }),
    { mode: 0o600 });' "$cfg" && ls -l "$cfg"
```

The `rm` comes first because the `0600` mode applies only to a file the command creates. Write the
file when it is missing, and again when the developer says the credentials changed. **Never read,
print or `cat` it**; `ls -l` is the only look it gets.

**The config sets no `origin`.** A preview's host changes with each pull request, Playwright matches
`origin` exactly, and the server reads the file only at launch. An origin would therefore force a
server reconnect per pull request. Without it, the browser answers a Basic Auth challenge from any
host with these credentials. The row accepts that trade.

The server reads the file only when it starts. **After writing it for the first time, stop** —
before composing any flow, so no work is lost — tell
the developer to add `--config <that path>` to the server's launch line (*Playwright MCP readiness*
below has the shape), reconnect the server with `/mcp` or start a fresh session, and run the skill
again.

A browser that still meets the challenge — a navigation that fails with
`ERR_INVALID_AUTH_CREDENTIALS`, or a page answering `401` — means the server was not started with
the file, or the file is stale. Stop and name both remedies.

## Playwright MCP readiness

Before any browser is driven, confirm that **the Playwright MCP tools are present in this session** —
`browser_navigate`, `browser_snapshot`, `browser_take_screenshot`, `browser_console_messages` and
`browser_network_requests` at least. When they are not, stop and name the remedy: add the
Playwright MCP server, start a fresh session, and run the skill again. The shape is

```bash
claude mcp add playwright -- npx @playwright/mcp@latest \
  --isolated \
  --storage-state <path to a session.json> \
  --output-dir <cache dir>/playwright-mcp/<project> \
  --output-max-size 52428800
```

with `--config <repo-root>/.qa-scenarios/browser-config.json` added when the adapter has a *Preview
basic auth* row. The exact flags are the ones the server documents at run time.

**Recommend the two output flags; never stop without them.** The server writes a page snapshot and
a console log on every action, and with no `--output-dir` it writes them into the working
directory, so the project root collects an untracked `.playwright-mcp/` that grows without bound.
`--output-dir` moves those auto-named files to a cache outside the repo — `~/Library/Caches` on
macOS, `~/.cache` on Linux, `%LOCALAPPDATA%` on Windows — and `--output-max-size` evicts the oldest
once the folder passes that size (52428800 is 50 MB). A file the skill saves under an explicit name
still resolves against the workspace root, so evidence is unaffected. Snapshots stay on: the skills
read the page from them, so `--snapshot-mode none` is never the remedy. A server without the flags
drives the browser correctly; name them once and continue. **Isolated mode plus
a storage-state file is how a saved session reaches the browser**: the browser holds its profile in
memory, starts signed in from the scenario's `session.json`, and writes nothing back to it. The
server runs headed unless the developer asks for headless, so the developer can watch.

**When the skill dispatches drivers, one driver per flow means one isolated browser context per
flow, loaded with that flow's role's session.** Confirm the connected server gives each driver its
own context. When it can give the session only one browser, two drivers would act in the same page,
so dispatch the drivers one at a time, in flow order, and say why. A role whose session the server
cannot load is a stop that names the role.

Never install the server or a browser into the project, and never add the server without a yes.
