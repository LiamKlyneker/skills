#!/usr/bin/env bash
#
# doctor.sh — check that a project's skill install still matches the layout.
#
# Every failure class here is one that is silent today: a forked copy that looks
# like an install, a leftover `_shared/` that shadows canonical, an adapter still
# carrying template placeholders, a pointer to a gate file nobody wrote, a vendored
# skill quietly N commits behind the repo it came from.
#
# Usage:
#   doctor.sh [--repo <path>] [--bundle <slug>] [--canonical <path>] [--quiet]
#
#   --repo       project repo root (default: git root of $PWD)
#   --bundle     also check this bundle from install/bundles.md is fully reachable
#   --canonical  path to the canonical skills repo (default: inferred from this
#                script's own location, then from the install stamp)
#   --quiet      suppress OK/INFO lines; print problems only
#
# Exit: 0 clean · 1 problems found · 2 usage error

set -uo pipefail

# ---------------------------------------------------------------- setup

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
canonical="$(cd "$script_dir/../.." && pwd -P)"
repo=""
bundle=""
quiet=0
errors=0
warnings=0

while [ $# -gt 0 ]; do
  case "$1" in
    --repo)      repo="${2:-}"; shift 2 ;;
    --bundle)    bundle="${2:-}"; shift 2 ;;
    --canonical) canonical="${2:-}"; shift 2 ;;
    --quiet)     quiet=1; shift ;;
    -h|--help)   sed -n '2,20p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *)           echo "doctor.sh: unknown argument '$1'" >&2; exit 2 ;;
  esac
done

if [ -z "$repo" ]; then
  repo="$(git rev-parse --show-toplevel 2>/dev/null)" || {
    echo "doctor.sh: not in a git repo and no --repo given" >&2; exit 2; }
fi
[ -d "$repo" ] || { echo "doctor.sh: no such directory: $repo" >&2; exit 2; }
repo="$(cd "$repo" && pwd -P)"

skills_dir="$repo/.claude/skills"
project_dir="$repo/.claude/project"
adapter="$project_dir/adapter.md"
stamp="$skills_dir/INSTALL-STAMP.md"
template="$canonical/install/adapter.template.md"
bundles="$canonical/install/bundles.md"

err()  { printf '%-9s %s\n' "$1" "$2"; errors=$((errors + 1)); }
warn() { printf '%-9s %s\n' "WARN" "$1"; warnings=$((warnings + 1)); }
info() { [ "$quiet" -eq 1 ] || printf '%-9s %s\n' "INFO" "$1"; }
ok()   { [ "$quiet" -eq 1 ] || printf '%-9s %s\n' "OK" "$1"; }

rel() { printf '%s' "${1#$repo/}"; }

# Stamp lookup: `| `<path>` | `<bundle>` | `<sha>` | <date> |` rows.
# Prints the SHA for a vendored path, nothing if it is not stamped.
stamped_sha() {
  [ -f "$stamp" ] || return 0
  awk -F'|' -v want="$1" '
    NF >= 5 {
      p = $2; s = $4
      gsub(/[` \t]/, "", p); gsub(/[` \t]/, "", s)
      if (p == want && s != "" && s !~ /^-+$/) { print s; exit }
    }' "$stamp"
}

echo "doctor: $repo"
[ -n "$bundle" ] && echo "bundle: $bundle"
echo

# ---------------------------------------------------------------- 1. layout

if [ ! -d "$skills_dir" ]; then
  info "no $(rel "$skills_dir") — nothing installed in this repo"
  info "(skills may still reach it from a global config dir)"
  [ -z "$bundle" ] && { echo; echo "0 problems"; exit 0; }
fi

vendored_mode=0
[ -f "$stamp" ] && vendored_mode=1

# ---------------------------------------------------------------- 2. entries

installed=""   # newline-separated "<name>\t<physical path>\t<symlink|vendor>"

if [ -d "$skills_dir" ]; then
  for entry in "$skills_dir"/*; do
    [ -e "$entry" ] || [ -L "$entry" ] || continue
    name="$(basename "$entry")"

    if [ -L "$entry" ]; then
      if [ ! -e "$entry" ]; then
        err "DANGLING" "$(rel "$entry") → $(readlink "$entry") (target does not exist)"
        continue
      fi
      phys="$(cd "$entry" 2>/dev/null && pwd -P)" || { err "DANGLING" "$(rel "$entry") is not a directory"; continue; }
      installed="$installed$name	$phys	symlink
"
      continue
    fi

    if [ -d "$entry" ]; then
      sha="$(stamped_sha "$name")"
      if [ -n "$sha" ]; then
        installed="$installed$name	$entry	vendor
"
      elif [ "$name" = "_shared" ]; then
        err "BANNED" "$(rel "$entry") — a project never owns a _shared/ (#11). Unstamped, so it shadows canonical for any copied skill."
      elif [ ! -d "$canonical/$name" ]; then
        # A fork shadows a canonical skill of the same name. With no canonical
        # counterpart there is nothing to shadow and nothing to drift from, so
        # this is a skill the project genuinely owns — the one legitimate reason
        # for a real directory here.
        info "$(rel "$entry") is project-owned (no skill of that name in canonical)"
      else
        err "FORK" "$(rel "$entry") is a real directory, not a symlink, and no stamp claims it — this is a fork"
      fi
      continue
    fi

    case "$name" in
      INSTALL-STAMP.md) ;;
      *) warn "$(rel "$entry") is a loose file in the skills directory" ;;
    esac
  done
fi

# A stamped `_shared/` is legal — vendor mode has no canonical to resolve past the
# copy, so the snapshot is the only global reference there is. Say so out loud,
# because the same directory unstamped is the #11 bug.
if [ "$vendored_mode" -eq 1 ] && [ -d "$skills_dir/_shared" ] && [ -n "$(stamped_sha _shared)" ]; then
  info "$(rel "$skills_dir/_shared") is a stamped vendor snapshot, not a project-owned _shared/"
fi

# Any other `_shared/` under .claude/ is the banned shape wherever it hides.
while IFS= read -r found; do
  [ -n "$found" ] || continue
  [ "$found" = "$skills_dir/_shared" ] && continue
  err "BANNED" "$(rel "$found") — a project never owns a _shared/ (#11)"
done < <(find "$repo/.claude" -type d -name _shared 2>/dev/null)

# ---------------------------------------------------------------- 3. dangling links anywhere under .claude/

while IFS= read -r link; do
  [ -n "$link" ] || continue
  case "$link" in "$skills_dir"/*) continue ;; esac   # already reported above
  err "DANGLING" "$(rel "$link") → $(readlink "$link") (target does not exist)"
done < <(find "$repo/.claude" -type l ! -exec test -e {} \; -print 2>/dev/null)

# ---------------------------------------------------------------- 4. the adapter

needs_adapter=0
while IFS=$'\t' read -r name phys mode; do
  [ -n "$name" ] || continue
  if grep -rqs '\.claude/project/adapter\.md' "$phys" 2>/dev/null; then
    needs_adapter=1
    break
  fi
done <<< "$installed"

if [ "$needs_adapter" -eq 1 ] && [ ! -f "$adapter" ]; then
  err "HOLE" "$(rel "$adapter") is missing, but an installed skill reads it"
elif [ -f "$adapter" ]; then
  # 4a. still a template?
  if head -5 "$adapter" | grep -q 'TEMPLATE'; then
    err "UNFILLED" "$(rel "$adapter") still carries the TEMPLATE marker — it was copied, never filled"
  fi

  # 4b. surviving template placeholders. A token counts only if the template
  # ships it; tokens the template declares as notation are exempt.
  if [ -f "$template" ]; then
    exempt=" $(sed -n 's/.*doctor:not-a-placeholder \(.*\)/\1/p' "$template" | sed 's/--> *$//' | tr '\n' ' ') "
    hits=0
    while IFS= read -r token; do
      [ -n "$token" ] || continue
      case "$exempt" in *" $token "*) continue ;; esac
      if grep -Fq -- "$token" "$adapter"; then
        err "UNFILLED" "$(rel "$adapter") still has the template placeholder $token"
        hits=$((hits + 1))
        [ "$hits" -ge 8 ] && { warn "more placeholders suppressed — this adapter is essentially unfilled"; break; }
      fi
    done < <(grep -o '<[^<>]*>' "$template" | sort -u)
  else
    warn "no adapter template at $template — skipped the placeholder check"
  fi

  # 4c. sibling pointers the adapter registers must exist
  while IFS= read -r ptr; do
    [ -n "$ptr" ] || continue
    target="$project_dir/${ptr#./}"
    if [ ! -f "$target" ]; then
      err "POINTER" "$(rel "$adapter") points at \`$ptr\`, but $(rel "$target") does not exist"
    fi
  done < <(grep -o '\./[A-Za-z0-9._/-]\{1,\}\.md' "$adapter" | sort -u)

  ok "$(rel "$adapter") present"
fi

# ---------------------------------------------------------------- 5. ../_shared/ resolution

while IFS=$'\t' read -r name phys mode; do
  [ -n "$name" ] || continue
  while IFS= read -r ref; do
    [ -n "$ref" ] || continue
    target="$phys/$ref"
    if [ ! -f "$target" ]; then
      err "SHARED" "$name reads $ref, which does not resolve (looked in $(dirname "$phys")/_shared/)"
    fi
  done < <(grep -rhoE '\.\./_shared/[A-Za-z0-9._-]+\.md' "$phys" 2>/dev/null | sort -u)
done <<< "$installed"

# ---------------------------------------------------------------- 6. vendored drift

if [ "$vendored_mode" -eq 1 ]; then
  stamp_canonical="$(sed -n 's/.*\*\*Canonical clone[^:]*:\*\* *`\([^`]*\)`.*/\1/p' "$stamp" | head -1)"
  [ -d "$canonical/.git" ] || [ -z "$stamp_canonical" ] || canonical="$stamp_canonical"

  if [ ! -d "$canonical/.git" ]; then
    warn "no canonical clone reachable (tried $canonical) — cannot check vendored skills for drift"
  else
    while IFS=$'\t' read -r name phys mode; do
      [ "$mode" = "vendor" ] || continue
      sha="$(stamped_sha "$name")"

      if ! git -C "$canonical" cat-file -e "$sha^{commit}" 2>/dev/null; then
        err "STAMP" "$name is stamped at $sha, which is not a commit in $canonical"
        continue
      fi

      behind="$(git -C "$canonical" rev-list --count "$sha"..HEAD -- "$name" 2>/dev/null)"
      [ -n "$behind" ] && [ "$behind" -gt 0 ] &&
        err "STALE" "$name is $behind commit(s) behind canonical (stamped $sha)"

      tmp="$(mktemp -d)"
      if git -C "$canonical" archive "$sha" "$name" 2>/dev/null | tar -x -C "$tmp" 2>/dev/null; then
        changed="$(diff -rq "$tmp/$name" "$phys" 2>/dev/null | wc -l | tr -d ' ')"
        [ "$changed" -gt 0 ] &&
          err "DIVERGED" "$name has $changed local difference(s) from its stamped SHA — edited in place"
      else
        warn "could not extract $name at $sha — skipped its divergence check"
      fi
      rm -rf "$tmp"
    done <<< "$installed"
  fi
fi

# ---------------------------------------------------------------- 7. bundle completeness

if [ -n "$bundle" ]; then
  if [ ! -f "$bundles" ]; then
    warn "no bundle manifest at $bundles — skipped the completeness check"
  else
    line="$(awk -v b="$bundle" '
      $0 ~ "^## `" b "`$" { inb = 1; next }
      /^## / { inb = 0 }
      inb && /^- \*\*Skills:\*\*/ { print; exit }' "$bundles")"

    if [ -z "$line" ]; then
      err "BUNDLE" "no bundle named '$bundle' in $bundles"
    else
      for skill in $(printf '%s' "$line" | grep -o '`[^`]*`' | tr -d '`'); do
        if [ -e "$skills_dir/$skill" ]; then
          continue
        fi
        globally=""
        # personal config first — the others are PWD-scoped and may not apply here
        for cfg in "$HOME/.claude/skills" "$HOME"/.claude-*/skills; do
          [ -e "$cfg/$skill" ] && { globally="$cfg"; break; }
        done
        if [ -n "$globally" ]; then
          info "$skill is not linked in this repo, but is reachable from ~${globally#$HOME}"
        else
          err "MISSING" "$bundle needs $skill, which is reachable neither here nor from any ~/.claude*/skills"
        fi
      done
    fi
  fi
fi

# ---------------------------------------------------------------- summary

echo
if [ "$errors" -eq 0 ] && [ "$warnings" -eq 0 ]; then
  echo "clean — 0 problems"
  exit 0
fi
echo "$errors problem(s), $warnings warning(s)"
[ "$errors" -gt 0 ] && exit 1
exit 0
