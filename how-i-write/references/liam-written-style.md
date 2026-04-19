# Liam’s writing samples — reference archive

Real samples of Liam’s writing across four registers: narrative-technical (blog posts, case studies), Slack-work (team messages), casual-conversational (replies to friends), and personal-reflective (diary-style notes). The writing inside each section is preserved verbatim — the section headers are annotations added for navigation only.

For a shorter curated subset (one sample per register), see `liam-written-style-small.md` in this same directory.

## 1. Narrative-technical — Blog post (full Chapter I on server components + shared UI libraries)

Building Shared UI Libraries In The Server Components Era  - Chapter I
If you’re reading this, you probably love server components as much as I do. We all enjoy working on server-component-based projects. As fancy as that sounds, it simply means that we love to take full advantage of server capabilities using frameworks designed for them, like Next.js. Benefits like faster rendering, immaculate SEO, less JavaScript delivery to users, improved loading experiences, and all the other juicy features it offers.
When it comes to building UIs and using or reusing components like buttons, inputs, dialogs, etc., we already have solutions like MUI, ChakraUI, MantineUI, and who knows what other library with a random name ending in UI is going to appear. So, why create another option? Well, those can work for a single or personal project, but when your team has several projects that need to share components, a common UI language, company styles, utilities for it, etc… you have to build a UI Library for them.
Now, to build it (assuming we’re not in a monorepo situation), we’d usually have a specific repository for it where we can throw all this common UI stuff, then publish it to our company’s npm so projects can use it. From there, we can pick our poison. As I said before, we can choose a solution that provides everything, like MUI, tweak it a bit, add company styles, export everything from an index file, and call it a day. Or, if we don’t want to depend on them and prefer to have full control of the components, we can create them from scratch and enhance them with the lovely RadixUI library. Regardless of the path you choose (I’m not here to judge anyone…), the way our components are built and processed has to change for a server-friendly approach. So, let’s see how we can achieve that.
But before jumping in, a quick note: I want to pour my mind out and share my experiences coding this stuff - not just the code itself, but the "whys" behind it. To avoid boring you, I’ve broken it into chapters (guess I’m a novelist now…). This chapter focuses on some core concepts, package setup, and tsup configuration, the goal is to have the foundation for building this type of UI library. So, get ready, because s##t is about to get a bit technical.
How It Used To Be, The Good Old Days
Before the server components era, exporting our stuff from a shared library was simple. For example, you might have had a folder structure like this:
From this structure, you’d create a single entry point (typically an index.ts) that re-exports everything:
And a typical package.json for such a library would look like this:
Nothing special, that’s the way it has always been… and once devs use our library, they would consume the components like this:

The Server Components Era
Now, with server components, especially with Next.js from version 13 and onward, we’re dealing with a `use client` directive at the top of our files, so the app knows when a component is a server or client component.
This is why we can’t export everything from a single entry point anymore. First, if any component in our library uses useState, useMemo, or any client-side behavior without the new directive, it will cause our app to crash. Second, we don’t want to turn our server pages into client ones just to accommodate this, or even worse, create a bypass component to render them first and then use it in the project (guilty af)… And that’s without mentioning all the benefits that individual exports give us, like improved tree-shaking of unused components, better control over dependencies, flexibility for devs, and so on.
So… let’s break down what we need to do:
Export each component individually.
Add the `use client` directive where needed.
Build the library without losing the `use client` directive. This one is easier said than done.

Bundler And Package Configuration
We’ll dive deeper into the rest of the stack in future chapters - spoiler alert: it’ll be Tailwind and RadixUI. But for now, let’s focus on the bundler. I’ll be using tsup for this setup. Here’s the configuration:
Now, here’s where things start to differ from regular, fully client-side libraries. In our package.json, instead of using a single entry point, we’re going to use the exports key - in this case, to expose the exported .mjs files. This key allows us to individually export our stuff by defining the package’s entry points, explicitly specifying which paths are exposed and accessible to devs:
And… don’t forget about the types! Without typesVersions, TypeScript would be completely clueless about which types to associate with the individual exports.
With this setup, we’re no longer bundling everything into a single entry point anymore. Each component is independently exported and projects can consume only the components they need like so:
The "use client" Directive
Now that we’ve exposed our components individually, we need to identify which ones are hardcore-client-specific and which can remain server-side. In general, components like buttons, inputs and some other like them should stay as server components because the browser already handles their behavior natively. If we need client-specific behavior for them, it’s the project’s responsibility to manage that.
For the sake of this example, let’s assume that components with heavy interactivity, like Dialog and Carousel, are client components so, these files will have the use client directive at the top:
If we build the library at this point without any additional configuration, the output files will look something like this:
Lets track down that chunkIt’s already a problem that the `use client` directive is missing here, but if we dive into the chunk itself, we also find this:
`use client` is nowhere to be seenTo ensure these components work properly when imported individually in a server situation, we need to add the `use client` directive to the exported component itself and to its respective chunks if necessary, like in this one, it’s importing a useEffect… it is a client component for sure.
After some investigation I found out that the only way to achieve it (at least at the time of writing this) was by creating a plugin for tsup. Trial and error, some questionable attempts, fate - and not gonna lie, a few sleepless nights -  lead me to thevuong’s solution so, big thanks to him - I adapted his approach to fit my needs.
Finding this was everything…The logic behind the plugin is in theory simple: it reads the files, identifies the `use client` directive, and ensures that it is preserved. It also checks if any chunk generated by tsup contains hooks or events, and if so, adds the `use client` directive there as well:
Although the "magic" is everywhere in the process, the key part is in the itContainsHooksOrEvents function. This function evaluates whether a chunk contains hooks or events, allowing us to flag it with the `use client` directive - beautiful… You can even take this further by adding more checks, like identifying exclusively client-side external libraries, and automatically applying the directive when needed.
Then, in the tsup.config, we just:
Finally, when you run the tsup command, you should see that the chunk files meant to be client-side include the `use client` directive... I was just "Ain’t no way!!!".
And it was there…Conclusion
We’ve covered how to configure tsup and package.json, along with a few more concepts. With this, we now have a nice server-friendly setup to start building components on top of it.

---

¡Y bueno! That’s the first part of my experience building UI libraries for my team. In the next chapter, I’ll dive deeper into the specifics of the library itself: the folder structure, the problems it solves, best practices, peculiarities, how to improve developer experience, valuable things that I learn in the process, and probably much more. For now, that’s about it. Till further notice ✋.

## 2. Narrative-technical (presentational variant) — Design portfolio case study (Genius app redesign)

First, some context (I promise, will be really short), then, the designs.
Let’s begin!
What is Genius?
Genius brings music intelligence to the masses.
Genius is a powerful tool, which allow to all of us who loves music an opportunity to collect and share knowledge, founded in 2009, Genius is a unique media company that’s powered by community, an in-house creative team, and the artists themselves.
Genius started as a platform for annotating clever rap lyrics-the original name was Rap Genius. Over the years, they’ve expanded their mission to include more than hip-hop, and more than just lyrics.

Currently (2019), some parts of the app can be a little bit confusing for those users that only want to learn everything about their favorites songs and those who contribute with knowledge to the platform.
So, the goal with this project is to reach a harmony between these types of users by improving the usability and experience, hence, make much easier use Genius.
Types of Users
I identified two types of users, lets see them:
#TYPE 1
THE OCCASIONAL ONE
- Could be new users as well.
- They use Genius only to see lyrics.
- They only want to go into the app and search the song really quickly.
The goal here is improve the way that they search a song, save items and discover all the facts about their favorite artists.
#TYPE 2
THE HEAVY ONE
- Users that know the platform.
- Apart from learn, they also contributing and earning points by transcribing songs, adding cover annotations, etc.
The goal here is to improve the collaboration flows to make intuitive the way to contribute, without annoying those users who only came to Genius to collect knowledge.
To clarify, these types of users are not separated per se, they are separated by the way that they using Genius.
So, with the idea that the app have to be easy to use and the premise that everyone can collaborate, this project will try to merge in harmony everyone that use Genius.

First Things First
The song section its our core, because there is where you really start using genius. So, right after you open the app, three really simple ways to reach that section exist.

#1
THE USUAL
Tap the search button — which, is at the reach of your thumb :)
Search what you want.
Pick the song

#2
WHEN YOU ARE LISTENING FROM YOUR FAVORITE STREAMING SERVICE
At the top you will see your recently listened songs.
Pick the song.

#3
WHEN THE SONG IT’S OUT LOUD
Hold the search button.
Let the app listen the song.
Voila!

No, It’s Not Just Lyrics
We know that a song is a meaningful piece of art, this section was renovated, allowing you collect all knowledge that our contributors provide, the only thing that you have to do is #swipe.
Introducing... the Song Section.

SONGS ANNOTATIONS
Just tap in any highlighted section to see the meaning, could be the yellow ones or the green ones.

THE FACTS
At the first swipe to right we have The Facts, here you can find info about the song such it description, writer, music video, and so on.

THE MUST TO KNOW
Here is where comes the power of Genius community, a Q&A section where you can learn even more about that song.

- Last but no least
MORE
The reason that this section is at the first left swipe is to do much simpler the task to navigate between songs, like a playlist, see to where album or albums belongs the song.

THE BIO MATTERS
Since some Bios are quite big and it has to be, because we wanna know everyting. A Reading Section was created, doing easy and enjouyful reading the About of your favorite Artist, Song or Album.
Enter here by tapping the see more link, available in all of our sections.

The Almighty
Cooperate Symbol
O)
Under the premise that everyone can cooperate or contribute,
Genius now have a symbol that you will find in many places inside the app, wherever you see this symbol is a sign that you can contribute and earn IQ points, so, your duty is spread your knowledge to the world.
The Basics
Maybe you heard a interview of your favorite artist, or seen a lost article in the web about the meaning of a lyric, well, there is where we need you, annotate lyrics in Genius now is simple and intuitive, along your annotation you can add images or sources. therefore giving a more valuable contribution.

Large Screen
Same Experience
If you get the mobile flow, understanding the desktop flow will be super easy, the work of passing the designs from the mobile app was really organic, we adjusted some of them, and transform the usability and fidelity to larger screens.

Coda
Well, that was a lot of work!
I think that the goal was acomplished, I’m leaving in the inkwell some sections that I could work later, such as the Profile, Video & Articles Sections, or even a Contributor Home where these ones can review aportations, see stats and so on, but... I feel that the core of Genius was covered.
Obviusly, there is a lot things that can be improved, but, that is what design is all about right? iterate and improve.
I’ll really appreciate your feedback and thoughts regarding this project.
Nothing left to say from my side, I leave you with the technical info and some early wireframes and... thank you very very x1000 much to reach this point and reading this coda • #peaceAndLove.

## 3. Casual-conversational — One-line reaction (ultra-short)

Biblical, prophetic!!

## 4. Slack-work — PR announcement with migration notes (long-form, `:hand:` signoff)

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

## 5. Slack-work — Status update / end-of-initiative handoff (with "till further notice" signoff)

Hi @channel, before I leave, here’s the status/result of the Tailwind Proof of Concept and what might come next:

A repo for the new library has been created: grimme-components
Despite the consensus of the majority of us was on favor to use the new library we still need to be careful before deploying it to production. Currently, developers can only check the library, its configuration, and structure. They can also open PRs with suggestions, try it locally, etc.
I’ve added a detailed README.md there, so developers can try it on their own.
To try it locally and play with it, I recommend creating another branch in your projects, as for now, we are going to use the file protocol.
The project has a functional local Storybook, so we can start adding components. @Hauke has the styles for the button that he created in Grid, that can be added to the library for instance.
I would appreciate some feedback from the developers on the project so we can continue improving it.

Sooo, that’s pretty much it. We can say that the library is in a beta state, so the next steps involve developers getting familiarized with it. Then, we can release it to a proper Storybook and CI and start using it in production.

Thanks and till further notice.

## 6. Casual-conversational — Travel photo caption (one-liner with emoji)

Greetings from my hometown in Peru :flag-pe: — Cerro de Pasco. At 4,380m above sea level, it’s literally in the clouds :cold_face:

## 7. Casual-conversational — Reply with context (conversational detail, photo chat)

hahahahah yes, the main hole is at the right side of that lake, and it’s active again since late 2024 I think, could hear some detonations and stuff so def they start again expanding the thing but there are some tensions/protests at the moment as they have to reach to an agreement with parts of the city that will stop existing basically… tricky situation.

First photo is from a mountain near by, couldn’t reach higher, the lack of oxygen was killing me :joy: the hole can be seen a little bit far away on the right side, and the second one is the closest that I got to it

## 8. Slack-work — Process suggestion (long-form, dash-sectioned, scheduled message)

Hi Team :wave: , I just sent a new PR to review, also I’ve been checking the rest of them as well and I have some suggestions to do.

– Commits Format –

We could try using a format for commits, something like this (for instance):
[JIRA-TICKET] (feat|fix|chore|test): description here"

And try to maintain it in ONE commit per PR, otherwise we will have something like: (see image 1)
Instead of something more readable like this:
GIT LOG:
[SOR-12] chore: setup husky and lint staged, prettify some files
[SOR-11] feat: some nice feature here
[SOR-10] feat: some nice feature here
[SOR-9] fix: some nice fix here
[SOR-8] feat: some nice feature here
...and so on

The big advantages of doing this, apart that it will be more readable for git log and some tools like tig , are the following (some of them):

If something happens in production and we need to perform a rollback, it will be more easy to find where we want to return.
If we have a lot of features/tickets that we need to release in a certain sprint and for some reason some feature/PR that is already merged is rejected or request to be removed by our QA team or the very same Client, do a cherry pick to remove it from our release branch will be more easy to perform.


– PR Descriptions –

Also, maybe we can have a template for our Descriptions, I’m using this (see image 2).

Please share your thoughts about it, maybe you already have some rules that I miss or better ideas to improve this specific part of our workflow, thanks :slightly_smiling_face:.


cc @pavi @Ibrahim @Niklas @Alex

*This is a scheduled message  :robot_face:

## 9. Slack-work — Technical opinion reply (i18next translations, no signoff)

Again, this is how the translations_keys are configured, so:

I see some other projects that they add the keys progressively so if they don’t have keys for ru locale for instance, they don’t even create the file so the default fallback works.
In JavaScript we have closures and function callbacks that consume memory and fill the CallStack, that is the way that JS works with its Engine (v8 one of them) and stuff, so the t from react-i18next it’s a function that consumes memory already to render strings and put this one inside another function it’s from my point of view a bit overkill for the task that it’s doing.
Also, again, this is not the fault of the library, is the way the they configured the keys.
I didn’t see this implementation in another grimme project, so I’m suspecting if we deploy this to prod we only going to release the locales that they have ready to go.
Worst case scenario, if they ask specifically for something like this we should include it, otherwise I’d say that let’s stick with the natural way that react-i18next works.

## 10. Slack-work — Asking for input on a decision (deploy/versioning)

hello guys, I’m about to deploy the new library to the pipelines but Mukku is asking me about the versioning of that, in my opinion, since we won’t release this to the public we can just increasing the patch version every time a developer do some changes:
- v0.0.120
- v0.0.121
- v0.0.122
- v0.0.123
- and so on
increasing dev speed and removing the effort of manual releasing, we can relay on tags for breaking changes but in these two years that I’ve been in the company I didn’t found a specific scenario for that, at least on the components, what do you guys think on this one? this approach is only for the components, maybe the rest of the apps need the semver structure.

Or.... we can also implement changeset: https://github.com/changesets/changesets?tab=readme-ov-file, idk how that works in azure tho.

## 11. Casual-conversational — Short trip note

Was a nice electronic festival, I dance a lot! But what I like the most of this trip was the other city: omg Eindhoven, I’ll come back for sure!

## 12. Personal-reflective — Diary-style entry (the kino)

So… today I’m going to the kino with that person, idk where this will lead me, or lead us, but… idk, I’m feeling something on my stomach, butterflies? Or maybe it’s just the excitement of watching that movie in a cinema for the very first time…

In any case we’re about to enter to watch the movie, let’s see how I’ll remember this day in the days to come…
