# Vendor mode

Symlinks are machine-local and uncommittable. A collaborator cloning the repo, a cloud
agent, or CI all get a dangling link. Where the canonical clone can't be reached, the only
thing that works is a copy.

So copies are **legal but checkable**: `install --vendor` copies the bundle in and writes a
stamp recording the commit it came from. Silent forking stops being possible — it becomes
a `STALE` or `DIVERGED` line the next time `doctor` runs.

Symlink mode remains the default everywhere it works. Vendoring is for the cases where it
can't.

## What gets copied

The bundle's skills **and its global reference files**.

This is the part that surprises people: a copied skill's `../_shared/…` resolves to
`.claude/skills/_shared/`, not to canonical, because there is no symlink left for POSIX to
resolve past. So vendor mode has to place a `_shared/` inside the project — the exact
directory the layout otherwise bans.

That is not a re-litigation of the ban. The ban exists so `../_shared/x.md` can never mean
*project facts*; a vendored `_shared/` is a stamped snapshot of canonical global reference,
and project facts still live in `.claude/project/`. The invariant holds. What changes is
that the snapshot can now go stale, which is precisely why it is stamped and checked.

`doctor` enforces the distinction: a `_shared/` covered by the stamp is reported as a
vendor snapshot; the same directory **unstamped** is a `BANNED` error. Never hand-create
one, and never hand-edit one.

## The stamp

`<repo-root>/.claude/skills/INSTALL-STAMP.md`, committed alongside the vendored copies:

```markdown
# Vendored skill install — stamp

Written by `install-skills install --vendor`; read by `doctor`. Do not hand-edit —
run `install-skills update` instead.

- **Canonical repo:** `LiamKlyneker/skills`
- **Canonical clone (this machine):** `/Users/you/…/skills`
- **Mode:** vendor
- **Bundle(s):** `prd-workflow`

| Path | Bundle | Canonical SHA | Installed |
|---|---|---|---|
| `to-prd` | `prd-workflow` | `35e3d81…` | 2026-07-27 |
| `_shared` | `prd-workflow` | `35e3d81…` | 2026-07-27 |
```

Row per top-level entry under `.claude/skills/`, including `_shared`. Per-path SHAs rather
than one repo-wide SHA, so a partial update leaves an honest record instead of claiming
every skill moved.

Only vendor installs have a stamp. **A symlink install writes no bookkeeping at all** —
`readlink` already answers every question a stamp would, and a file that restates the
filesystem is a file that can disagree with it.

## Drift, and the two ways to have it

`doctor` reports these separately because they need opposite responses:

- **`STALE`** — canonical has N commits touching this path since the stamp. The copy is
  behind. Fix: re-copy, re-stamp.
- **`DIVERGED`** — the copy differs from the content at its own stamped SHA. Someone
  edited it in place. Fix: **a conversation.** That edit may be work worth back-porting to
  canonical, and re-copying over it destroys it silently. This is the failure this whole
  mechanism exists to make visible; do not automate past it.

A skill can be both at once. Resolve `DIVERGED` first — decide what to keep — then update.

Both checks need a reachable canonical clone. Without one, `doctor` says so and skips
them rather than reporting a clean bill of health it can't back up.

## `update` in vendor mode

1. `doctor` first. Never update on top of unreported divergence.
2. For each `DIVERGED` path, show the diff against its stamped SHA and get a decision:
   back-port to canonical, discard, or leave the path pinned for now.
3. Re-copy the paths cleared for update, at canonical `HEAD`.
4. Rewrite those rows' SHA and date. Leave pinned rows alone — a stamp that lies about
   what is installed is worse than one that admits a path is behind.
5. `doctor` again.

## Which mode a project should be in

| | symlink | vendor |
|---|---|---|
| skill edits are live | yes, immediately | no — until the next update |
| survives `git clone` on another machine | no | yes |
| CI / cloud agents | broken | works |
| can drift | can't | can, visibly |
| `.claude/skills/` in git | gitignored | committed |

Default to symlink. Reach for vendor when the install has to survive being cloned.
