# Liam's real PR review comments — reference archive

Real review comments Liam wrote on Azure DevOps pull requests (Marketplace repo), lightly curated. This is the ground truth for the PR / code review register: lowercase starts, `nitpick:` prefixes, deferral softeners, short value-dense observations, questions left open (`wdyt?`, `right?`), and the three-emoji allowlist (🙌 ✅ 😆) used sparingly at end-of-thought. Context lines in *italics* are annotations for navigation, not part of the comments.

## Suggestions and open questions

*Inline on a `DataTable` component, deferring a design question:*

> this is for later, we should ask if this Select can be part of the Pagination component as both seems to be intrinsic related to each other.

*Inline on a variants const, enumerating real alternatives — the one attested bullet use in this register, and thinking aloud mid-comment:*

> I was thinking on this approach and names and I have couple of observations or maybe 2 ways that we can improve this area:
> - Option one, we can rename this to `paginationButtonVariants` and that can fix a bit to define to what is this const intended.
> - Option two, I see that you are consider this variants as the main one for the component in the `PaginationProps` type, so I think the best approach here will be to rename this the variants inside the `paginationButtonVariants` to `primary` and `secondary` where probably `primary` would be the default in our design system which is the `bg-transparent` I think. We are doing this because normally in components that potentially will go to the library the styles that depends on the variant needs to come from the main parent so we don't have coalitions in the future, by doing this change then when the time comes we can have add a main `paginationVariants` that will go in the `<ReactHeadlessPagination />` according to specs...
>
> ...There is a third option that will be having this `paginationVariants` with `primary` and `secondary` and add tailwind groups and then the buttons can act accordingly, that also can be a very good option now that I think of it if we don't have that many classes to put in each other. You can check the Accordion component in grimme-ui for more reference.

*Inline on a boolean name — `nitpick:` prefix, reasoning included, question left open:*

> nitpick: I think the name here is implying that at least one category should be on even tho you're just checking the group filter, I get it because you cannot select further if you don't have a group right? maybe we can update the name to `isCategoriesFiltersActive`? wdyt?

*Inline on a styling detail, deferred to design:*

> maybe in the future we can consider have that `<span />` as part of the pressed style in grimme-ui, we should confirm this with design tho...

*Inline on `useTranslations` inside a shared component — explains the why, then scopes the ask down:*

> we are planning that in some point we should move these components to grimme-ui, so we can't use `useTransalations` here, I'd pass these as strings from the parent, but that will imply that now `DataTable` should accept more params... lets have that as a topic in the future for now you can just leave a comment over here please, that says that we need to find a strategy to remove these tKeys out of this component

*Inline on hook naming — states his lean, leaves it open:*

> I think `useGetCountriesList` was describing what the hook does a bit better wdyt?

## Direct asks (reviewing a more junior teammate)

*Inline on JSX being returned from a data function:*

> always lets only return the object that you want here and no JSX please, its more readable to have all html related content down there, for tracking, debugging, tests-ids, etc and we are not guessing what `{countryOptions}` this means and you are not jumping through the file the find different structures

*Same PR, same pattern elsewhere — short because the argument was already made:*

> same here, lets only return the object and no JSX please

*Follow-up in the same thread, with a sketch:*

> also, I see that this is the same function that you are using in the step-01 file ?, I'd suggest to create a utility function, another advantage of not having JSX here is that allow us to encapsulate that kind of functions, so it'll be something like:
> ```
> const countryOptions = useMemo(() => {
>   return getSortedOptionsBySomethingFromCountriesList(...paramsNeededHere)
> }, [countriesList, geoLocation?.data]
> ```

*Third occurrence of the pattern:*

> yep, rule of 3, we need to move this into a utility function without the JSX thing there

*Inline on a fetch inside `useEffect` — with the out-of-scope softener:*

> I think we need to refactor this to be a SWR fetch, its not a good practice anymore to use `useEffect` with a fetch inside, if this is out of the scope of this PR please add a TODO comment here that we need to do that

*Inline on a hook calling another hook:*

> I wont use a hook inside a hook, what if I need data from a diiferent locale even tho idk if this is applied here but its a good practice, lets turn this locale as a param please

*Inline on `usedMachineFiltersData` / `countriesList`:*

> can these `usedMachineFiltersData` and `countriesList` just use one `useDeprecatedPageData`? also, left a comment that we need to replace this with the `useBrowsePageContext` once is ready.

## Short observations — most comments look like these

> this return is lacking an `isLoading` property

> is this change on purpose right?

> nitpick: isn't `an` here?

## Praise, approvals, replies

*Reply after a suggestion was applied:*

> nice!

> now looks really nice!!

*Inline praise — one of the three allowed emoji, end-of-thought:*

> Nice abstraction 🙌

*Approval summary comment:*

> LGTM Fran! approved ✅, I just left some suggestions and nitpicks plis.

*Whole reply to a teammate laughing at a typo:*

> 😆
