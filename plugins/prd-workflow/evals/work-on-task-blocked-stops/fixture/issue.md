[TASK] Shelf count: skip archived shelves

## Summary

`countShelves` in `lib/shelf-count.ts` counts archived shelves, so the header total overstates
what a user can open. This task makes the count skip them.

**Implement this issue with `/prd-workflow:work-on-task <this-issue-url>`.**

## External steps

- [ ] Confirm with the shelf-store owner that `archived` is set on every shelf the import job writes

## What to build

`countShelves` returns the number of shelves whose `archived` is `false`.

1. `countShelves` in `lib/shelf-count.ts` — filter out shelves with `archived: true` before counting.

## Decisions confirmed

- Archived shelves never count toward the total — the header shows what a user can open.

## Out of scope

- The archive action itself — another task.

## Worker context

- **Files**: `lib/shelf-count.ts`.
- **Prior art**: none.
- **Verify**: `test -f lib/shelf-count.ts`.
- **User-visible**: n

## QA notes

A pure function change with no screen of its own; nobody can exercise it by hand.

## Acceptance criteria

- [ ] `countShelves` returns 2 for three shelves of which one is archived

## Blocked by

- #41 Shelf store: backfill `archived` on imported shelves
