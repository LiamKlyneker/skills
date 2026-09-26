---
name: report-leak
description: >
  Report a skill failure back to the skills repo. Runs inside the consumer project where
  the failure was noticed, reduces it to facts, walks each fact back along the
  design-source → brief → grill → issue → code chain to the hop that first carried it
  without a source, and files one sanitized `[LEAK]` issue per guilty hop on
  `LiamKlyneker/skills`. Never fixes the failure and never writes an eval case. Invoke
  /lk:report-leak.
disable-model-invocation: true
---

# report-leak

**You noticed something a skill got wrong. This session turns that into a report the skills repo can act on, and nothing else.**

Three things this skill never does:

1. **It never fixes anything.** Not the code, not the brief, not the issue. The fix is a separate decision made by a separate session, in the project, after this report exists.
2. **It never writes an eval case.** It proposes a grader and a fixture element; the case is authored in the skills repo by whoever picks the issue up.
3. **It never asks which skill is guilty.** That is the whole question this skill answers. Asking it hands the walk back to the person who cannot run it.

**Its only output is one or more issues on `LiamKlyneker/skills`.** That repo is hardcoded here, because it is this skill's own home rather than a fact about the project you are standing in. Nothing about the skills repo ever enters a project's adapter, and this skill has no adapter section of its own.

## 1. Up-front — two questions, then stop asking

Ask both in one message, then wait. They are the only questions asked before the loop opens.

1. **What is wrong?** In your own words. Paste screenshots if you have them.
2. **What did you run to get here?** The ticket id, the branch or PR, and the slash commands in the order you ran them.

**Take the answers as given.** Do not ask which skill is at fault, which hop leaked, or what the design said — the walk in §3 finds all three. A third question before the loop is a question the artifacts already answer.

For a `to-task --out` run that produced no tracker issue, the second answer takes the **path of the issue file** instead of a ticket id. Everything downstream reads that file where it would have read the issue.

## 2. Project facts, and the chain you already know

**Read the consumer project's adapter at `<repo-root>/.claude/project/adapter.md`, and read its `## Repo` section only.** That section names the tracker and the repo; nothing else in the adapter concerns this skill. Find the run the way `manual-qa` does:

- **GitHub** — the PR whose body carries the whole-line resume key:

  ```bash
  gh pr list --repo <owner>/<repo> --state all --json number,headRefName,body \
    --jq '[.[] | select(.body | test("(^|\n)PRD: #<n>[ \t\r]*(\n|$)"))] | .[] | {number, headRefName}'
  ```

  **Match the whole line, never a substring** — `PRD: #12` is a prefix of `PRD: #127`. More than one hit, or none, is a **stop**: say what you found and ask.
- **Azure DevOps** — the `[SPEC]` work item's ArtifactLink gives the pull request.

**When the adapter is absent, or has no `## Repo` section, ask for the PR or the ticket instead of failing.** A project that never ran `install-skills` still has a failure worth reporting.

**The brief chain is known to this skill and is never asked for:**

```
design source (a Figma node, or a designer's code prototype at a pinned SHA)
  → brief            .claude/briefs/<ticket>.md
                     screenshots beside it for a Figma brief;
                     raw source URLs at the pinned SHA for a prototype brief
  → grill summary    .claude/briefs/<ticket>/grill.md
  → the tracker issue  ledger rows pasted byte-for-byte, plus the Decision and
                       Instruction columns, plus `## Decisions confirmed`
  → the branch diff  against the default branch, attributed by the `(#N)` commit suffix
```

Each arrow is a **hop**, and each hop is a skill: the brief hop is `figma-tools:figma-to-brief` or `figma-tools:prototype-to-spec`, the grill hop is `lk:deep-grill`, the issue hop is `prd-workflow:to-task` (or `to-prd` → `to-issues`), and the code hop is `prd-workflow:work-on-task` (or a `work-on-prd` worker).

## 3. The loop — one finding at a time

Each turn of the loop is four moves, in order. **Nothing is filed until §6.**

1. **State one finding.** One visual or behavioural failure, named plainly.
2. **Reduce it to facts.** A fact is one checkable claim about the shipped result — a copy string, a stack direction, a divider's owner, a padding owner, an icon name, a state that draws a container. Read the screenshots to derive the list.
3. **Walk each fact back** per §4, and mark it `leak` or `gap` per §5.
4. **Report the facts and the walk together, in one stop.** Print the fact list and the walk's result in the same message: the hop, quoting **the exact line of the guilty artifact**, and quoting **the sentence of that hop's `SKILL.md` or shared contract that the output violated** — or saying plainly that **no sentence covers it**, which is itself the most useful finding this skill produces. Then wait once, and continue on a "yes".

**The fact list gets no stop of its own.** A fact the user does not recognise is corrected at this one stop, and the walk over it is redone; a separate confirmation turn before the walk buys nothing the combined stop does not.

Then: next finding, or finish.

## 4. The walk

**For each fact, ask in this order:**

| # | Artifact | Question |
|---|---|---|
| 1 | the branch diff | is the fact in the code? |
| 2 | the tracker issue | is it in the issue's ledger row, its Decision or its Instruction? |
| 3 | `grill.md` | is it in the grill's saved decisions? |
| 4 | the brief | is it in a `## Fidelity ledger` row or elsewhere in the brief? |
| 5 | the design source | is it in the prototype source slice or the Figma node? |

**The guilty hop is the one that produced the first artifact carrying the fact with no source in the artifact before it.** Walking backwards is only the search order — a fact the design source carries and every artifact after it carries faithfully leaked nowhere, and is not a finding at all.

**Any other skill is one hop.** For a failure that has no brief chain behind it — a writing skill, a search skill, a bootstrap skill — ask two things instead: **where the output is**, and **what was expected**. The walk then has exactly one question: *which sentence of that `SKILL.md` covers this, if any*. Quote it, or say none does.

**`lk:how-i-write` names a rule number.** That skill carries a numbered `## Hard rules` list, so the issue names the hard rule the output violated **by its number**, or states that no rule covers it. The proposed grader for a `how-i-write` finding is a **regex or a Vale-style rule** — a banned phrase, a forbidden em-dash in a short register, a signoff outside its two permitted registers — never a judgement call.

## 5. `leak` or `gap` — every finding is marked as one

- **A `leak`** is a fact an artifact carries that its predecessor does not. Something was invented, renamed, re-summarised or overridden at that hop.
- **A `gap`** is a fact present **nowhere** in the chain. It is charged to the hop whose contract said to capture it: a design fact no brief row holds is a gap at the **brief** hop; a fact the brief carried that the grill never put in front of the human is a gap at the **grill** hop.

The two need different fixes — a leak needs a grader that catches an invention, a gap needs one that catches an omission — so the mark is part of the finding rather than a note about it.

## 6. Unverifiable hops are named, never skipped silently

**Briefs are regenerated in place.** The brief on disk today is not necessarily the brief the issue was written from, and nothing records which one was.

- **Diff the issue's ledger rows against the on-disk brief's rows.** On any difference, or when the brief is absent, mark the brief hop **"unverifiable, brief regenerated after the issue"** and continue the walk from the **issue** as the earliest trusted artifact.
- **The same rule applies to a missing `grill.md`**, which is the usual case: `deep-grill` writes it only when run with `--debug`. Fall back to the issue's `## Decisions confirmed` block, and **say in the session and in the issue body that the grill hop was read from the issue rather than from `grill.md`**.

An unverifiable hop still appears in the finding. "This may have leaked at the brief hop, and the brief can no longer prove it either way" is a real report; silence about it is not.

## 7. Known-leak check

**Before filing, say whether this is a known leak, a known leak with a new shape, or new.**

The taxonomy and the existing case names live in the skills repo, not in the project you are standing in, so read them over `gh`:

```bash
gh api repos/LiamKlyneker/skills/contents/plugins/prd-workflow/evals/fixtures/leaks.md \
  --jq '.content' | base64 -d

gh api 'repos/LiamKlyneker/skills/git/trees/main?recursive=1' \
  --jq '.tree[].path | select(test("evals/[^/]+/case\\.yaml$"))'
```

Three possible answers, and each goes in the issue body:

- **known** — `leaks.md` already names this leak and a case already covers it. Say which case.
- **known, new shape** — `leaks.md` names the leak, but this instance is a shape the existing case would not catch. Say which case, and what about this instance escapes it.
- **new** — no line in `leaks.md` describes it. For a skill with **no eval suite at all**, say so: no case exists, and this would be the first.

Phrase the finding in `leaks.md`'s own vocabulary. That file is where the issue's reader starts.

## 8. Re-entrant — findings live on disk while the session runs

**Findings so far are written to `<scratch>/leaks/<key>.md`, outside the consumer project**, where `<scratch>` is the session scratchpad directory the harness names — Claude Code names it in the session environment — and a fresh temp directory when it names none. The key is:

- the **ticket id**, for anything with a brief chain behind it;
- the literal **`how-i-write`**, for a writing correction;
- the **skill name**, for any other one-hop case.

**Running this skill again on the same key picks up what is already there** rather than starting empty — read the file first, present the findings it holds, and add to it. **Print the full path of that file in the session's last message**, so it can be copied before the scratch directory goes away.

**Nothing this skill writes lands in a repository.** Not the consumer project — after a run, `git status --porcelain` there reads exactly what it read before it — and not the skills repo. Only the sanitized issue bodies cross over, as issues.

## 9. Filing, on finish

**Group the findings by guilty hop and file one issue per hop.** Two findings on the same hop belong in one issue, because they become two graders in one future case. Findings on two hops are two issues, always.

For each hop, in order:

1. **Write the body to `<scratch>/leaks/<key>/issue-<hop>.md` — before anything is shown or posted.** The file is written first on purpose: the real run and any eval of this skill then exercise the same path, and the body that is summarised is the byte-identical body that gets posted.
2. **Summarise the issue. Never print the body.** Five lines per issue: the title, the hop, each finding's `leak` / `gap` mark, the known-leak status from §7, and a one-line list of the borderline tokens the body carries under §10 — a `sui-` prefix, a `-[Npx]` utility shape, anything that reached the body through a quoted contract sentence rather than through the run. **The `## Hop and skill` … `## Known-leak status` block never enters the transcript.** It stays in the file, and reaches `gh` through `--body-file`.
3. **Ask for approval only when nothing in the conversation authorises posting.** The user saying "post them", or naming the issues as the deliverable in the §1 answers, is that authorisation: post from the file without asking. When you do ask, state the sanitizing rule from §10 in the prompt — so the check is against a rule rather than against taste — and still show the summary rather than the body.
4. **Post it from that file:**

   ```bash
   gh issue create --repo LiamKlyneker/skills \
     --title "[LEAK] <hop> — <one-line shape of the finding>" \
     --label needs-triage \
     --body-file <scratch>/leaks/<key>/issue-<hop>.md
   ```

**Body sections, in this order:**

```
## Hop and skill
<which hop, and the skill that owns it>

## Contract sentence
<the sentence of that SKILL.md or shared contract the output violated — quoted>
<or: no sentence covers this>

## Finding
<one entry per finding, each in abstract form, each marked `leak` or `gap`>

## Minimal input
<what a micro stub needs to reproduce it, and nothing else: the adapter rows the
 skill reads, the catalog tokens involved, the one source file or component, and —
 when the guilty hop is not the first in the chain — the frozen artifact of the hop
 before it, such as a ledger row or an issue fragment>
<name a `skills-fixture` element only when the finding is about fixture shape — the
 skill reading the wrong file, ignoring a pointer the adapter gave it, mis-walking the
 tree — and say why a stub cannot carry it; ADR 0017 holds the boundary>

## Proposed grader
<what a grader would assert — for how-i-write, a regex or a Vale-style rule>

## Known-leak status
known / known, new shape / new — <the case name, or "no case exists for this skill yet">
```

## 10. The sanitizing rule — mechanical, not judgement

**The body may quote this repo's files and nothing else.** Concretely, permitted content is:

- text from a `SKILL.md`, from `_shared/*.md`, or from `plugins/prd-workflow/evals/fixtures/leaks.md`;
- fixture element names and stub file names;
- the names of skills, hops and eval cases.

**Everything else is excluded, with no judgement call:** no project name, no company name, no ticket id, no project path, no component name, no branch or PR number, no screenshot, and no quoted text from any artifact of the run — no brief row, no issue line, no diff hunk, no grill answer.

**Screenshots stay in the consumer project.** They are read to derive the fact list, and then dropped. They are never attached, never described in the body, and never uploaded.

This is what the finding being "in abstract form" means: the body says *a composite classified by name match while its default chrome differs from the still*, never what that composite was called in this project.

## 11. `gh`, on any tracker

**Call `gh` regardless of which tracker the project uses, and check `gh auth status` up front.** The issues land on `LiamKlyneker/skills`, which is on GitHub whatever the project is on.

**On an Azure DevOps project**, find the pull request and the `[SPEC]` through the ADO tools; `gh` is still what files the report.

**Without `gh` auth: write every body to `<scratch>/leaks/<key>/` and stop.** Print the full path of each file, and say that nothing was posted. Do not attempt another route to the repo, and do not discard the bodies — they are the whole session's work, and a human can post them in a minute.
