# Spec Splitting Seams

Normative home for where a spec splits into work items, not whether it does. A spec always
produces at least one work item — this document decides where to cut, and `to-spec-tasks`
applies it against current code state.

Cut on a seam whenever one of these applies:

1. **HITL gate** — a manual step owned by another team blocks downstream work mid-stream (e.g. translation-key fallback approval, copy sign-off).
2. **Different code areas with zero touch overlap** — e.g. a backend schema migration plus an unrelated frontend copy fix in the same spec.
3. **Size** — more than roughly five acceptance criteria (~5 AC). Size alone is sufficient to cut on; no additional natural-seam condition is required. This is the same proxy `to-issues` uses for "too big for one worker", and it gives every work item the same implicit guarantee its GitHub counterpart carries: it fits one fresh worker session.
4. **Expand/contract migration risk** flagged in the spec. Two-part (expand → cutover), or three-part (expand → cutover → contract) when legacy removal is in scope.
5. **Prefactoring** — a refactor that would make the feature work trivial becomes its own **leading** slice ("make the change easy, then make the easy change"), listed as `Blocked by` for the slices it unblocks.

Cap at **4** work items. If the spec would need more, push back: the underlying User Story is too big and should be re-scoped by Product.
