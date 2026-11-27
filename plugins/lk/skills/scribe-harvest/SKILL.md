---
name: scribe-harvest
description: >
  Collect voice data for `lk:scribe` from the text Liam typed in the current session — bank
  entries, voice samples and corrected drafts — sanitize it, show it to Liam, and after his
  approval file it as one `needs-grill` issue on `LiamKlyneker/skills`, or add it to the open
  harvest issue. Proposes data only; never edits `lk:scribe`. Invoke /lk:scribe-harvest.
disable-model-invocation: true
---

# scribe-harvest

**The session transcript is the evidence. This skill turns what Liam typed into data for `lk:scribe`, and files it as one issue on the skills repo.**

The issue carries data only. A later grill on that issue decides what lands in the `lk:scribe` reference files. This skill never edits a `lk:scribe` file, and nothing it files changes how `lk:scribe` drafts until that grill merges a change.

**Its only output is an issue, or a comment on an issue, on `LiamKlyneker/skills`.** That repo is hardcoded, because it is this skill's own home rather than a fact about the project you are standing in. This skill reads nothing from the project's adapter and writes nothing to the project.

`<scratch>` below is the session scratchpad directory the harness names, or a fresh temp directory when it names none. Every file this skill writes goes under `<scratch>/scribe-harvest/`.

## 1. Find the transcript of this session

**Read the words from the transcript file, never from your memory of the conversation.** A long session is summarized, and the summary loses the exact words.

The harness replaces a session-id variable in this file, so the session id is `${CLAUDE_SESSION_ID}`. When the previous sentence shows a variable name instead of a UUID, take the session id from the scratchpad path the harness names: it is the last path segment, a UUID. Do not take it from any other harness path, such as a background task's output file: after a `/clear`, such a path can still carry the id of the session before it.

The transcript is `<config dir>/projects/<project slug>/<session id>.jsonl`. The config directory is `$CLAUDE_CONFIG_DIR` when it is set, otherwise `~/.claude`. Find the file by its name rather than by building the slug:

```bash
find "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects" -maxdepth 2 -name '<session id>.jsonl'
```

No file, or more than one → stop, print what the search returned, and post nothing.

## 2. Extract the typed messages

**A typed message is a row with `type: "user"` and `promptSource: "typed"`.** Its `message.content` is a string, or a list of blocks when Liam attached an image; take the text of each `text` block and skip the `image` blocks. Every other row is not a typed message:

- a row with `isMeta: true`, or with `isCompactSummary: true`;
- a tool result: a user row whose content is a list of `tool_result` blocks, with no `promptSource`;
- a slash command: a user row whose content opens with `<command-name>` or `<local-command-stdout>`, with no `promptSource`;
- a row whose `promptSource` is anything other than `typed`, such as `system` (a message from another session or a subagent) or `sdk`.

Inside a typed message, remove what is not Liam's prose: every `<pasted_content …>…</pasted_content>` block and every `[Image #N]` placeholder. A message that is empty after that is skipped.

```bash
mkdir -p <scratch>/scribe-harvest
python3 -I - "<transcript path>" > <scratch>/scribe-harvest/typed.txt <<'PY'
import json, re, sys
paste = re.compile(r'<pasted_content[^>]*>.*?</pasted_content>', re.S)
image = re.compile(r'\[Image #\d+\]')
for line in open(sys.argv[1]):
    row = json.loads(line)
    if row.get('type') != 'user' or row.get('promptSource') != 'typed':
        continue
    if row.get('isMeta') or row.get('isCompactSummary'):
        continue
    content = row.get('message', {}).get('content')
    if isinstance(content, list):
        content = '\n'.join(b.get('text', '') for b in content if b.get('type') == 'text')
    text = image.sub('', paste.sub('', content or '')).strip()
    if text:
        print('=== ' + row.get('timestamp', ''))
        print(text)
PY
```

The `lk:scribe` drafts this session made are in the transcript, not in `typed.txt`: an assistant row after a `Skill` tool call for `lk:scribe`, or after a `/lk:scribe` command row, holds the draft as text. §4 reads them for corrections.

No typed message at all → say "nothing new here", and stop.

## 3. Read what `lk:scribe` already holds

Read the current `lk:scribe` reference files to compare against: `references/liam-banks.md`, `references/liam-session-messages.md`, `references/corrections.md`, and the three sample files `references/liam-written-style.md`, `references/liam-written-style-small.md` and `references/liam-pr-review-comments.md`. Prefer the copy this session loaded, under the base directory the harness named when it loaded `lk:scribe`. Otherwise read `main`:

```bash
gh api repos/LiamKlyneker/skills/contents/plugins/lk/skills/scribe/references/<file> --jq '.content' | base64 -d
```

Then look for the open harvest issue, and read its body and comments when it exists:

```bash
gh issue list --repo LiamKlyneker/skills --state open --search 'in:title "lk:scribe — harvest"' \
  --json number,title,url --limit 10
gh issue view <N> --repo LiamKlyneker/skills --json body,comments
```

Only an issue whose title is exactly `[IDEA] lk:scribe — harvest` counts. Data that issue already proposes is not proposed again.

## 4. Collect three kinds of data

**The banks are sorted by slot**: openers, closers, hedges and reframes, check-ins, intensifiers, reactions. Read the definition of each slot and of the levels at the top of `liam-banks.md`.

- **Bank data.** For each of the six slots, tally what Liam's typed messages used in that slot, including "nothing", over every typed message. From that tally:
  - *New bank entries* — an entry the banks do not hold yet, with the level the tally suggests, a surface note when it is restricted, and one quote that shows it.
  - *Level changes* — only where the tally contradicts the level the bank records, such as a `rare` entry in most messages, or an `often` entry in none of many messages. A level the tally roughly agrees with is not a change. One session is weak evidence; propose a change only when it is not close.
- **Voice samples.** At most 5 for each run. A sample is a typed message, or one part of it, that shows a move worth keeping for Registers 2 and 3. A candidate that the reference files already attest — the same move, not just the same words — is dropped. When `liam-session-messages.md` holds 30 samples, each new sample names the sample it replaces.
- **Corrections.** Before/after pairs from this session: `lk:scribe` drafted, and Liam then edited the draft or rejected it. Each pair takes the shape of an entry in `corrections.md`: the register, the before, the after, and the why. A why that Liam did not state is marked as your inference. There is no maximum.

**One optional line, "Pattern I noticed"**, is the only place a harvest may suggest a rule, a new trait or a new slot. Everything else in the issue is data.

**Nothing new → say "nothing new here", and stop.** That is the case when there is no new bank entry, no level change, no voice sample, no correction and no pattern. A tally with nothing new is not enough to file.

## 5. Sanitize

**A quote keeps Liam's words.** Do not fix his spelling, his rhythm or his punctuation; those are the data.

**Each private noun in a quote is replaced by a generic noun in square brackets**: a company, product, client, project, repo, branch, ticket id, person, file path, component, route or endpoint. For example *"the `RouteCard` is still broken"* becomes *"the [a component] is still broken"*. A quote that loses its meaning after the replacement is dropped.

What this skill may file, in full: Liam's quoted words with private nouns replaced, entries and levels for the banks, the names of `lk:scribe`'s files and slots, and your own descriptions of what a quote shows. No URL other than `github.com/LiamKlyneker/skills`, no email, no credential, no code, no log line.

**Write the title and body to files first.** Title: `<scratch>/scribe-harvest/title.txt`, with the text `[IDEA] lk:scribe — harvest`. Body: `<scratch>/scribe-harvest/body.md`, with these sections in this order, each omitted when it has no content:

```
## Session tally
<one line for each slot: the entries used and how often, including "nothing">

## New bank entries
<slot · entry · level · surface note, if any · one quote>

## Level changes
<slot · entry · recorded level → proposed level · the tally that contradicts it>

## Voice samples
<each one: the quote · what it shows · "add" or "replaces <sample>">

## Corrections
<each one: register · before · after · why>

## Pattern I noticed
<one line, or the section is omitted>
```

**Then run the shared scan** in `../references/public-issue-scan.md`: read it and run it as written, with `<scratch>/scribe-harvest` as `<dir>`, `<scratch>/scribe-harvest/title.txt` as `<title>` and `<scratch>/scribe-harvest/body.md` as `<body>`. A hit is replaced by a bracketed generic noun under the rule above, or its quote is dropped, and the scan runs again.

## 6. Show it, and wait for approval

**Post nothing before Liam approves.** A scan cannot prove a free-text quote clean, so Liam reads every quote first.

Show the body file as it will be posted, the result of the scan, and each explained false positive. Then ask whether to post. Liam can remove items: remove them from the body file, run the scan again, and show the result again. A run he stops posts nothing.

## 7. Post

After approval, post from the files.

When §3 found the open harvest issue `<N>`, add a comment to it and file no new issue:

```bash
gh issue comment <N> --repo LiamKlyneker/skills --body-file <scratch>/scribe-harvest/body.md
```

Otherwise file a new one:

```bash
gh issue create --repo LiamKlyneker/skills \
  --title "$(cat <scratch>/scribe-harvest/title.txt)" \
  --label needs-grill \
  --body-file <scratch>/scribe-harvest/body.md
```

In the last message, print the title and URL of the issue or comment posted, and name each explained false positive.

## 8. `gh`, on any tracker

**Check `gh auth status` before §3.** The issue lands on GitHub whatever tracker the project uses.

**Without `gh` auth:** read the reference files from the loaded copy only, collect, sanitize and show as usual, then write the title and body to `<scratch>/scribe-harvest/` and stop. Print the full path of each file, and say that nothing was posted. Do not try another route to the repo.

## 9. When the samples file is full

When `liam-session-messages.md` holds 30 samples, look for the audit issue by its title:

```bash
gh issue list --repo LiamKlyneker/skills --state open \
  --search 'in:title "lk:scribe-harvest — audit the limits after real use"' --json number,title,url
```

When it is open, the last message of the run names it and its URL, and says the samples file is full.
