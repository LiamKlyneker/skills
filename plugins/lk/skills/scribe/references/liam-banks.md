# Banks — what fills each slot of a work message

One bank for each slot of a message. A draft for a work surface (a PR comment, a review reply, a
Slack or Teams message, an issue or ticket comment to a teammate) fills each slot from its bank. The
banks hold only what Liam's writing attests: `../SKILL.md`, the three sample files in this directory,
and `corrections.md`. An entry the attested text does not show is not added here.

**Levels.** Each entry has a level, `often`, `sometimes` or `rare`. A level says how often the entry
fills its slot across many messages, not inside one message. Pick `often` entries most, `sometimes`
entries now and then, `rare` entries seldom. **No entry appears twice in one message.**

**The "nothing" entry** means the slot stays empty: no marker at all. It is an entry like the
others, and it is picked as often as its level says. Without it every slot gets a marker, and a
message with a marker in every slot is a tell.

**Surface notes** restrict an entry to some surfaces, such as "Slack only" or "not in a PR comment".
An entry with no note is good on every work surface. The hard rules in `../SKILL.md` win over every
entry: rule 7 still limits a PR comment, and rule 18 still removes slang on a spec page.

## Openers

How the first words of the message start.

- **nothing** — go straight into the point — `often`. *"this return is lacking an `isLoading` property"*, *"is this change on purpose right?"*, *"can these ... just use one ..."*
- **bare `@mention`** — `@channel`, `@Mark`, or the PR author — `often`. *"@channel there are 2 PRs..."*, *"@Mark just pushed the fix..."*. Bare means no greeting word in front of it (rule 7).
- **`hey @channel :wave:` / `Hi Team :wave:`** — `sometimes` · Slack only. Never on a PR comment (rule 7).
- **`team,`** — the audience word, then straight in — `sometimes` · Slack or Teams only. *"team, had a question about..."*
- **`hello guys,`** — `rare` · Slack only.
- **`nice work over here`** — `sometimes` · PR summary only, light praise (rule 8).
- **`LGTM!`** — `sometimes` · PR summary only. *"LGTM! one thing before merge tho..."*
- **`nitpick:`** — `sometimes` · PR comment only, a small point.
- **`this is for later...`** — `rare` · PR comment only, a deferred point.
- **`same here,`** — `rare` · PR comment only, the same point made again.
- **`so` after a mention or at the start** — `sometimes` · not on a spec page (rule 18). *"@Drews, Franciele so this one is not the G..."*
- **`Again,`** — `rare` · Slack only, when the point was made before.
- **`I looked at this one...` / `I checked this with...`** — `rare` · a spec-page reply only (rule 18).

## Closers

How the message ends.

- **nothing** — end on the last point or on the open question — `often`. *"...something that I'm not seeing?"*
- **`please` / `plis` on the ask** — `sometimes`. *"...and no JSX please"*, *"...suggestions and nitpicks plis."*
- **`And that's it from me` / `thats it` / `that's pretty much it`** — `sometimes` · Slack only, a long post.
- **end-of-thought emoji** — `sometimes` · Slack: `:slightly_smiling_face:`, `:joy:`; PR comment: only 🙌, ✅ or 😆 and only on praise, an approval or banter (rule 7).
- **`thanks`** — `rare` · Slack only. *"...this specific part of our workflow, thanks :slightly_smiling_face:."*
- **`cc @name @name`** — `rare` · Slack only, on its own line.
- **`Till further notice :hand:`** — `rare` · an away message only (rule 2).

## Hedges and reframes

What softens a claim or turns it around.

- **nothing** — state it plainly — `sometimes`. *"this return is lacking an `isLoading` property"*
- **`tho`** — `often`. *"This PR tho, introduces..."*, *"we should confirm this with design tho..."*, *"one thing before merge tho"*, *"even tho"*.
- **`I think`** — `often`. *"I think the name here is implying..."*, *"I think we need to refactor this..."*. On a spec page the next step is conditional instead (rule 18).
- **`maybe`** — `often`. *"maybe we can update the name to..."*, *"maybe in the future we can consider..."*
- **`I'd suggest` / `I'd say` / `I'd pass`** — `sometimes`. *"I'd suggest to create a utility function"*
- **`if this is out of the scope of this PR...`** — `sometimes` · PR comment only.
- **`idk`** — `sometimes`. *"idk how that works in azure tho"*, *"idk tbh"*
- **`I mean`** — `sometimes` · Slack, Teams or casual. *"I mean lets reference it but we should move these files over there right?"*
- **`from what I can tell`** — `rare`.
- **`in my opinion` / `from my point of view`** — `rare` · Slack only.
- **`now that I think of it`** — a revision mid-comment — `rare`. *"...that also can be a very good option now that I think of it"*
- **`That being said...`** — `rare` · Slack only, a long post.
- **`not gonna lie`** — `rare` · not in a PR comment.
- **`tbh`** — `rare`.

## Check-ins

The question that asks for the reader's side.

- **nothing** — a statement, an announcement or a heads-up asks nothing — `often`.
- **`wdyt?`** — `often`. *"maybe we can update the name to `isCategoriesFiltersActive`? wdyt?"*
- **`...right?`** at the end of a clause — `sometimes`. *"is this change on purpose right?"*, *"I get it because you cannot select further if you don't have a group right?"*
- **`something that I'm not seeing?` / `or is there something I'm missing?`** — `sometimes`.
- **`lmk` / `lmk if anything` / `lmk if there's a reason for it`** — `sometimes`.
- **`does that make sense tho?`** — `rare`.
- **`what do you guys think on this one?`** — `rare` · Slack only.
- **`Please share your thoughts about it`** — `rare` · Slack only, a long post.

## Intensifiers

What turns a word up.

- **nothing** — `often`.
- **`really`** — `sometimes`. *"now looks really nice!!"*, *"really simple"*
- **doubled or tripled `!!`** — `sometimes`. *"now looks really nice!!"*
- **repetition, `very very veeeery`, `very very x1000`** — `rare` · Slack or casual.
- **`for sure`** — `rare`. *"it is a client component for sure"*
- **`af`** — `rare` · not in a PR comment, not on a spec page (rule 18). *"(guilty af)"*
- **`tf` inside a phrase** — `rare` · Slack only, not on a spec page. *"prop tf drill"*
- **`def`** — `rare` · casual only.

## Reactions

A short word that reacts to what someone else said or did.

- **nothing** — `often`.
- **`nice!`** — `sometimes` · PR reply after a suggestion was applied.
- **`yep,`** — `rare`. *"yep, rule of 3, we need to move this..."*
- **a lone 😆** — `rare` · PR reply to a joke only (rule 7).
- **`hahahahah`** — `rare` · casual only.
- **`omg`** — `rare` · casual only.
