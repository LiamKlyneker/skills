---
name: report
description: >
  File what this session concluded about one of Liam's skills — a defect or an improvement — as
  a sanitized issue on `LiamKlyneker/skills`. Runs in the consumer project where it was noticed,
  reads the conclusion out of the conversation, strips everything that belongs to that project,
  and files it with `needs-grill`. Never fixes anything. Invoke /lk:report.
disable-model-invocation: true
---

# report

**The conversation is the evidence. This skill turns its conclusion into an issue on the skills repo, and nothing else.**

By the time this runs, the investigation is done: the session already holds what went wrong or what could be better, and which skill it concerns. This skill does not re-investigate, does not re-ask what the session already answers, and does not fix anything — the fix is decided later, in a grill in the skills repo.

**Its only output is issues on `LiamKlyneker/skills`.** That repo is hardcoded, because it is this skill's own home rather than a fact about the project you are standing in. This skill reads nothing from the project's adapter and writes nothing to the project.

## 1. Read the conclusion out of the session

From the conversation so far, extract, for each distinct thing to report:

- **the skill** it concerns, by its namespaced name (`prd-workflow:to-task`, `lk:deep-grill`);
- **what happened, or what is missing**, as one or two plain sentences;
- **what should change**, as concretely as the session settled it;
- **the kind** — `[BUG]` when a skill did something its contract or its obvious intent says it should not, or failed to do something it says it does; `[IDEA]` for everything else: a missing capability, friction, a better default, a rewording.

**Pick the kind yourself.** Never ask which it is.

**Two unrelated things are two issues.** Two symptoms of one root cause are one issue.

**Ask only when the session holds no conclusion** — it is empty, or it never reached one about a skill. Then ask exactly one question: *"What do you want to report, and about which skill?"* Take the answer as the session's conclusion and continue. A minor idea needs no more than that answer.

## 2. Find the contract sentence

For each item, read that skill's `SKILL.md`. Prefer the copy this session loaded — the harness names its base directory when it loads a skill — because that is the text that actually ran. Otherwise read `main`:

```bash
gh api repos/LiamKlyneker/skills/contents/plugins/<plugin>/skills/<skill>/SKILL.md --jq '.content' | base64 -d
```

Quote **the sentence the behaviour violated**, or the sentence an idea would change. When no sentence covers it, say so — that is itself a finding.

Record the plugin's `version` from the loaded copy's `.claude-plugin/plugin.json`, two directories above its `skills/`. When only `main` was read, leave the version out rather than guess.

## 3. Check for an existing issue

```bash
gh issue list --repo LiamKlyneker/skills --state all --search "<skill name> <two or three key words>" \
  --json number,title,url,state --limit 10
```

The search covers open and closed issues. When the session's conclusion already says the failure was seen before, the search only has to find the issue number.

**When an open issue already covers the item, do not file a new one.** Add the new detail to it as a comment instead, written to the same files and posted by §7. Filing and commenting follow the same sanitizing rule.

**When a closed issue describes the same skill and the same symptom, the failure is a recurrence.** File the report as usual, and put one line in its body: `Recurrence of #N`, where `N` is the closed issue. A closed issue on a different skill or a different symptom is not a recurrence and adds no line.

## 4. Security findings never go public

**If the item is about a secret, a credential, or a privacy hole in a skill** — a skill that printed a token, wrote a password to a file, or posted private data somewhere public — **do not file an issue.** Stop, say that this belongs in a private security advisory on `LiamKlyneker/skills` (`SECURITY.md`), and give the link `https://github.com/LiamKlyneker/skills/security/advisories/new`.

## 5. Write the body

**Write each issue to `<scratch>/report/<n>/title.txt` and `<scratch>/report/<n>/body.md`**, where `<scratch>` is the session scratchpad directory the harness names, or a fresh temp directory when it names none, and `<n>` counts from 1. The file is written before the scan, so the body the scan checked is byte-identical to the body that is posted.

Title: `[BUG] <skill> — <one-line shape>` or `[IDEA] <skill> — <one-line shape>`.

Body sections, in this order:

```
## Skill
<plugin:skill>, version <x.y.z> — or no version line when none was found

## What happened
<for [BUG]: the behaviour, in abstract form. For [IDEA]: the situation that made the gap visible, in abstract form>

## Contract sentence
<the quoted SKILL.md sentence, or: no sentence covers this>

## Proposed change
<what should change, as concretely as the session settled it>

Recurrence of #<N>
```

The `Recurrence of #<N>` line is the last line of the body, after `## Proposed change`, and appears only on a recurrence report. A report that is not a recurrence has no such line.

## 6. The sanitizing rule — mechanical, not judgement

**This repo is public, and an issue is permanent: it is indexed, and GitHub keeps every edit.**

**The body may quote this repo's files and nothing else.** Permitted content:

- text from any file in `LiamKlyneker/skills` — a `SKILL.md`, `_shared/*.md`, an eval case, a fixture;
- the names of plugins, skills, agents, eval cases, and the `version`;
- a reference to an issue in `LiamKlyneker/skills` itself, such as `Recurrence of #N`: it names this repo's own issue and nothing of the project, so it is the one issue number the "no PR name or number" exclusion below does not cover;
- generic descriptions written in your own words: *a component*, *a list screen*, *a two-step form*, *the project's tracker*, *a design token*.

**Everything else is excluded, with no judgement call:** no company, product, client or project name; no repo, org, branch or PR name or number; no ticket id; no person's name or handle; no file path from the project; no component, route, table, endpoint or token name from the project; no URL other than `github.com/LiamKlyneker/skills`; no email; no credential or anything shaped like one; no screenshot; and **no quoted text from any artifact of the project** — no code, no diff hunk, no issue line, no brief row, no log line, no error message copied verbatim.

Abstract form means the body says *a skill picked a design token by name match while the design used a different one*, never what the token was called.

**Then scan the title and body mechanically** before posting them. The scan is in `../references/public-issue-scan.md`: read it and run it as written, with `<scratch>/report` as `<dir>`, `<scratch>/report/<n>/title.txt` as `<title>` and `<scratch>/report/<n>/body.md` as `<body>`. A hit is rewritten in abstract form, the rule above, and the scan runs again; the reference says how a false positive and an unfixable hit are handled.

## 7. Post

**Post without asking for approval.** The session already holds the conclusion, and the scan is the check. Post each item whose scan is clean, or whose every remaining hit is explained, from its files:

```bash
gh issue create --repo LiamKlyneker/skills \
  --title "$(cat <scratch>/report/<n>/title.txt)" \
  --label needs-grill \
  --body-file <scratch>/report/<n>/body.md
```

For a comment on an open issue `<N>` from §3:

```bash
gh issue comment <N> --repo LiamKlyneker/skills --body-file <scratch>/report/<n>/body.md
```

In the last message, print the title and URL of each issue or comment posted, and name each explained false positive.

## 8. `gh`, on any tracker

**Check `gh auth status` before §3.** The issues land on GitHub whatever tracker the project uses.

**Without `gh` auth: write every title and body to `<scratch>/report/` and stop.** Print the full path of each file, and say that nothing was posted. Do not try another route to the repo.
