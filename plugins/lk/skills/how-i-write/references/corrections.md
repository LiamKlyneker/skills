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
