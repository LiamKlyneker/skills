# Corrections — drafts that missed, and what Liam actually wanted

Before/after pairs collected from real usage. Each entry is: what a draft got wrong → what it should have been → why. Treat every **Why** line as a rule with the same weight as the hard rules in `SKILL.md`. This file grows over time — when a draft in Liam's voice gets edited before sending, the pair belongs here.

## 1. Forensic detail in a PR comment (2026-08 — became hard rule 12)

**Register:** PR review comment (Azure DevOps), replying about whether a logo asset matched the Figma.

**Before (as drafted — starts human, then turns robotic):**

> @Drews, Franciele so this one is not the G... it's the full myGRIMME wordmark, the lockup with the red GRIMME plus the two bars and the dot, and the grey `my` sitting next to it, 84x16, rendered as a plain `img`. two fills in there, `#E1000F` for the red and `#9AA2A5` for the my.
>
> that's also why it couldn't be the kit icon even if we wanted it to... the customicons are single path monochrome and take one color from css, so a two tone lockup can't really be expressed as a font icon. `faGrimmeG` is the single letter mark, different asset altogether.
>
> so no drift in the figma from what I can tell, the file is asking for the brand lockup and that's what's in there. wdyt?

**After (what it should have been):**

> @Drews, Franciele so this one is not the G... it's the full myGRIMME wordmark, the red GRIMME with the two bars and the grey my next to it, rendered as a plain `img`.
>
> that's also why it couldn't be the kit icon even if we wanted it to... the customicons are single path monochrome and take one color from css, so a two tone lockup can't really be expressed as a font icon. `faGrimmeG` is a different asset altogether.
>
> so no drift in the figma from what I can tell, the file is asking for the brand lockup and that's what's in there. wdyt?

**Why:** "84x16", "`#E1000F`", "`#9AA2A5`" are the agent citing its receipts — values it just measured, dumped into the message to prove the work. A human who looked at the logo describes it and moves on; the reader has eyes and the file. Precision nobody asked for is an instant AI tell, and one robotic clause undoes ten human ones around it. Named assets (`faGrimmeG`) stay — that's how humans refer to things; measurements are what no human volunteers. Exact values belong in a comment only when the value _is_ the point, or in an explicitly official document.

## 2. Opener, run-on flow, and bare ending on a Slack technical question (2026-09)

**Register:** Slack-work — a question to the BE/product team about a data-model field (eligibility question ordering). Liam keeps backticks on the code identifiers (`position`, `option.eligibilityQuestions[]`, `section` + `row`); code formatting is fine in Slack, this entry is not about that.

**Before (as drafted):**

> Hey :wave: had a question about the `position` field on the eligibility questions (FUS-8967/8968)...
>
> I was looking at how to persist the participant-facing order and I'm curious how you were picturing `position` working for it. Right now it lives inside each group (`option.eligibilityQuestions[]`), so it orders the questions within a single group... but since the same question can sit in a few groups with different positions, I wasn't sure how that maps to one order across the whole form.
>
> For the regular participant questions there's already their own positioning at the form level (`section` + `row`), so I had something to lean on there. I couldn't find an equivalent for the eligibility ones, so I wanted to check... was `position` meant to cover that too, or were you thinking of a separate form-level order? Maybe there's an angle I'm not seeing. lmk wdyt :slightly_smiling_face:

**After (what Liam sent):**

> team, had a question about the `positions` field on the eligibility questions, I was looking at how to persist the participant-facing order and I'm curious how you were picturing `position` working for it, now it lives inside each group (`option.eligibilityQuestions[]`), so it orders the questions within a single group... but since the same question can sit in a few groups with different positions, I wasn't sure how that maps to one order across the whole form.
>
> For the regular participant questions there's already their own positioning at the form level (`section` + `row`), so there is working and i was expecting some equivalent for the eligibility ones, so I wanted to check... was `position` meant to cover that too, or were you thinking of a separate form-level order? something that I'm not seeing?

**Why:** Four moves, all pulling the same direction — away from "assistant drafting a message" and toward "Liam typing to his team":

1. **Opener is a bare `team,`, not `Hey :wave:`.** For a group-facing technical ask he opens with the audience word and goes straight in. The `:wave:` opener is real (see SKILL.md) but it is not a default — a bare `team,` or a name is just as native, and often more so for a substantive question.
2. **Ends bare on the open question** (`something that I'm not seeing?`) — no trailing emoji, no `lmk wdyt`. The end-of-thought emoji and `wdyt` are optional, not a required closer. Do not staple them on when the message already ends on a genuine open question.
3. **Run-on, comma-spliced flow over clipped separate sentences.** The draft's "...working for it. Right now it lives..." became "...working for it, now it lives...". He joins clauses with commas and lets thoughts run; the drafted period-separated sentences read too tidy.
4. **Drops the inline ticket ref** ("(FUS-8967/8968)") — he doesn't tag ticket numbers into the middle of a conversational question.

Also note his non-native rhythm ("so there is working and i was expecting some equivalent", lowercase `i`) stays untouched per hard rule 4 — the draft's tidy "so I had something to lean on there. I couldn't find an equivalent" is the wrong instinct.

## 3. Lowercase after every full stop in a PR comment (2026-10)

**Register:** PR review comment, an approval summary. Liam flagged the line *"left some suggestions inline. one thing for Mark tho"*; the rest of the comment around it is reconstructed to show the pattern.

**Before (as drafted):**

> nice work over here. left some suggestions inline. one thing for Mark tho, the filters hook fetches on every render. is this on purpose? if it's out of the scope of this PR we can add a TODO. otherwise lgtm.

**After (what it should have been):**

> nice work over here, left some suggestions inline... one thing for Mark tho, the filters hook fetches on every render, is this on purpose? if its out of the scope of this PR we can add a TODO. Otherwise LGTM ✅

**Why:** Hard rule 13 lowercases the **opening word** of a comment, and hard rule 14 capitalises the word after a full stop. The draft lowercased after all four full stops, and that uniformity is what reads as generated. His real comments join sentences in a mix: comma splices most often, a question mark into lowercase, an ellipsis, a full stop into a capital. A full stop into lowercase can appear once, but never on every join. Any rule applied to every case becomes a new tell.

## 4. Every apostrophe and every subject in place on a Slack heads-up (2026-10)

**Register:** Slack-work, a short heads-up. Illustrative, not a sent message: it shows the shape of the miss rather than a real edit.

**Before (as drafted):**

> team, I've pushed the fix for the date picker, it's on the `fix/date-picker` branch. I'd appreciate a quick look when you've got a sec... I'll merge it tomorrow if nobody's against it, that's the plan at least

**After (what it should have been):**

> team, pushed the fix for the date picker, its on the `fix/date-picker` branch... would appreciate a quick look when you've got a sec. I'll merge it tomorrow if nobody's against it, thats the plan at least

**Why:** Every contraction spelled correctly and every clause with its subject is tidier than anyone types in Slack. The after drops the subject on the short clauses (`pushed the fix`, `would appreciate`) and the apostrophe on two contractions (`its`, `thats`) while `you've` and `nobody's` keep theirs. The mix is the signal: dropping every apostrophe is as uniform as keeping them all. `I'll` keeps its apostrophe because `ill` is a different word.

## 5. Named praise opening the summary of a routine PR (2026-11)

**Register:** PR review summary comment, on a small PR: one new tab that reuses an existing view, plus one small fix in a shared section. Reconstructed to show the shape of the miss, not the sent text.

**Before (as drafted):**

> nice work over here, small and clean change... the new tab reuses the existing view nicely and the tests cover the empty and loading states really well. one thing before merge tho, the shared section fix also changes the header spacing on the other tabs, can you double check those?

**After (what Liam sent):**

> LGTM! one thing before merge tho, the shared section fix also changes the header spacing on the other tabs, can you double check those?

**Why:** Hard rule 8 says to keep acknowledgment proportional, and this is what proportional means for the summary: a routine PR gets a bare `LGTM!` or `nice work` and no named details. Naming what an ordinary PR does well ("small and clean", "covers the empty and loading states") is something a human reviewer never bothers to write, so it reads as an unsupervised AI review. Some praise is always sincere, so sincerity is not the filter; the size and weight of the PR is. Named praise is for a large PR or unusual work — a hard bug, a clever design, a large cleanup.

## 6. One of two questions left unanswered in a spec-page reply (2026-11 — became hard rule 17)

**Register:** reply to a reviewer comment on a spec page. The comment asked two things: what it would take to close a gap, and whether Liam had already talked to the third-party vendor about it. Illustrative, not a sent message: it shows the shape of the miss rather than a real edit.

**Before (as drafted):**

> I looked at this one... to close the gap we would need a second call after the save, plus a small migration for the records that already exist. it is not a big change tho, roughly a day of work. wdyt?

**After (what it should have been):**

> I looked at this one... to close the gap we would need a second call after the save, plus a small migration for the records that already exist. it is not a big change tho, roughly a day of work. About the vendor, not yet, I wanted to know if we go this way first. wdyt?

**Why:** The draft answered the first question in detail and never touched the second. A plain *"not yet"* is a complete answer, and leaving it out reads as dodging the question. Before drafting any reply, list each direct question in the parent comment and check that the draft answers every one.

## 7. Full Register 2 tics on a reply to stakeholders on a spec page (2026-11 — became hard rule 18)

**Register:** reply to a product owner on a technical spec page in the team wiki, with a senior engineer from another team also on the thread. Illustrative, not a sent message: it shows the shape of the miss rather than a real edit.

**Before (as drafted):**

> so I went down the rabbit hole on this one and pinged the platform team on Slack... thats only possible if the service sends the event before the save, and right now it doesn't. I think we need to add the event on their side and listen for it here. (the spike only covered the read path btw, that's why this didn't show up there.) does that make sense tho?

**After (what it should have been):**

> I checked this with the platform team... that's only possible if the service sends the event before the save, and right now it doesn't. if we want that behaviour, we would need to add the event on their side and listen for it here. does that make sense tho?

**Why:** Four moves, all from hard rule 18:

1. **Plain first-person opener.** The lowercase `so` and the idiom for researching (*"went down the rabbit hole"*) go. *"I checked this with..."* says the same thing to a reader who is not a teammate.
2. **No chat-tool reference, and every apostrophe in place.** *"pinged the platform team on Slack"* becomes *"checked this with the platform team"*, and `thats` becomes `that's`.
3. **The next step is conditional on the reader's decision.** *"I think we need to"* is Liam's verdict. *"if we want that behaviour, we would need to"* leaves the call with the product owner, who owns it.
4. **No unprompted defence of earlier work.** Nobody asked about the spike's scope, so the parenthetical goes.

The ellipsis join, the `tho` and the open question at the end stay. The voice still applies, set lighter.

## 8. A commit hash copied from the drafting prompt into a ticket comment (2026-11 — extended hard rule 12)

**Register:** ticket comment addressed to a teammate, asking them to recheck a fix. The calling agent put the commit hash in the drafting prompt. Illustrative, not a sent message: it shows the shape of the miss rather than a real edit.

**Before (as drafted):**

> @Mark Pushed in `a3f9c21`, could you recheck the date picker when you have a sec? the edge case with the empty value should be gone now

**After (what it should have been):**

> @Mark just pushed the fix, could you recheck the date picker when you have a sec? the edge case with the empty value should be gone now

**Why:** No human types a commit hash into a regular comment. The teammate opens the branch and sees the latest push; the hash adds nothing for them. That one token makes the whole comment read as machine-written. The hash came from the drafting prompt, not from Liam, and that does not change the rule: facts in the prompt are input to rephrase, not text to copy. Hard rule 12 covers opaque identifiers on every conversational surface, ticket comments included. A hash stays only when it is the point, such as naming the commit where a regression starts.
