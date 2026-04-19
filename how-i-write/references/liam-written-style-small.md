# Liam’s writing samples — curated 4-sample subset

Four samples, one per register. Use this as a quick voice refresh. For the full archive (12 samples across all registers), see `liam-written-style.md` in this same directory.

## 1. Narrative-technical — Blog post (opener + outro from the Server Components Chapter I)

Building Shared UI Libraries In The Server Components Era  - Chapter I
If you’re reading this, you probably love server components as much as I do. We all enjoy working on server-component-based projects. As fancy as that sounds, it simply means that we love to take full advantage of server capabilities using frameworks designed for them, like Next.js. Benefits like faster rendering, immaculate SEO, less JavaScript delivery to users, improved loading experiences, and all the other juicy features it offers.

But before jumping in, a quick note: I want to pour my mind out and share my experiences coding this stuff - not just the code itself, but the "whys" behind it. To avoid boring you, I’ve broken it into chapters (guess I’m a novelist now…). This chapter focuses on some core concepts, package setup, and tsup configuration, the goal is to have the foundation for building this type of UI library. So, get ready, because s##t is about to get a bit technical.

¡Y bueno! That’s the first part of my experience building UI libraries for my team. In the next chapter, I’ll dive deeper into the specifics of the library itself: the folder structure, the problems it solves, best practices, peculiarities, how to improve developer experience, valuable things that I learn in the process, and probably much more. For now, that’s about it. Till further notice ✋.

## 2. Slack-work — PR announcement with migration notes (long-form, `:hand:` signoff)

@channel there are 2 PRs in GrimmeUI that need to be merge before you keep using the lib, more details on each PR:

Dialog Component (Breaking Change) - PR
The Dialog anatomy was improved because we had issues using the previous version with some other Radix Components like the DropdownMenu and the RadixUI Layer which is used to dismiss popovers, tooltips, dialogs, alerts, etc. The reason is because the props to deal with that were too encapsulated and we had to prop-drilling our way to the solution or to do what they recommend, to fix it we needed to mirror their composition.

This PR tho, introduces a "mini" breaking change for the ones that are already using the current version, I’ve added a MIGRATIONS.md for this type of scenarios, you can see more details and the "whys" there, but the change is very very veeeery simple:

So basically you’ll need to put your DialogHeader and DialogFooter (previously named DialogActions) inside the DialogContent and pass the "grimme-ui" props there, and thats it.

Benefits of this? a lot... we won’t need to maintain extra props to add more behaviour to it (or again prop tf drill) since now is a mirror of the RadixUI version, for instance if you want to prevent the closing/dismissing on click outside you’ll use a native RadixUI prop:

Also now you can use the thing with its Radix Triggers and Close Wrappers to avoid extra useStates  if your logic allows it:
etc, etc, etc... now the

Date Input Improvements - PR
This is not a breaking change but it has some context around it, we had issues at the moment to use react-hook-form with "special inputs", say the DateInput, PhoneInput, Autocomplete, in the case of the DateInput the value that is using is not a regular string is a Date so some filthy bugs were happening over there, this PR fixes it.

That being said... I took this opportunity to add a Section to test all our inputs so we are sure that they’re fully compatible with react-hook-form and all its methods and props: reset, setValue, defaultValues, isDirty, you name it. Also if its compatible with just regular react-hook-form rules or with zod validations.

You can find that in the Form Validation Section - src/stories/sections/form-validation.stories.tsx

And that’s it from me... til further notice :hand:


ps. somebody with permissions update my mandatory review please.

## 3. Casual-conversational — Reply with context (photo chat, crater detail)

hahahahah yes, the main hole is at the right side of that lake, and it’s active again since late 2024 I think, could hear some detonations and stuff so def they start again expanding the thing but there are some tensions/protests at the moment as they have to reach to an agreement with parts of the city that will stop existing basically… tricky situation.

First photo is from a mountain near by, couldn’t reach higher, the lack of oxygen was killing me :joy: the hole can be seen a little bit far away on the right side, and the second one is the closest that I got to it

## 4. Personal-reflective — Diary-style entry (the kino)

So… today I’m going to the kino with that person, idk where this will lead me, or lead us, but… idk, I’m feeling something on my stomach, butterflies? Or maybe it’s just the excitement of watching that movie in a cinema for the very first time…

In any case we’re about to enter to watch the movie, let’s see how I’ll remember this day in the days to come…
