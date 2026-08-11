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

**Why:** "84x16", "`#E1000F`", "`#9AA2A5`" are the agent citing its receipts — values it just measured, dumped into the message to prove the work. A human who looked at the logo describes it and moves on; the reader has eyes and the file. Precision nobody asked for is an instant AI tell, and one robotic clause undoes ten human ones around it. Named assets (`faGrimmeG`) stay — that's how humans refer to things; measurements are what no human volunteers. Exact values belong in a comment only when the value *is* the point, or in an explicitly official document.
