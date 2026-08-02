#!/usr/bin/env bash
#
# doctor.sh — check that a project's skill wiring still matches the layout.
#
# Every failure class here is one that is silent today: a leftover `_shared/` that
# shadows canonical, a dangling link, an adapter still carrying template
# placeholders, a pointer to a gate file nobody wrote.
#
# What it deliberately does NOT do is audit what a machine has lying around in a
# `skills/` directory. Skills reach a session one way — an installed plugin — so
# there is no second copy for one to load from, and a project's own skills are the
# project's business. ADR 0007 and ADR 0010.
#
# Usage:
#   doctor.sh [--repo <path>] [--bundle <slug>] [--canonical <path>] [--quiet]
#
#   --repo       project repo root (default: git root of $PWD)
#   --bundle     also check this bundle from install/bundles.md is satisfied here
#   --canonical  path to the canonical skills repo (default: inferred from this
#                script's own location)
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
    -h|--help)   sed -n '2,18p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *)           echo "doctor.sh: unknown argument '$1'" >&2; exit 2 ;;
  esac
done

if [ -z "$repo" ]; then
  repo="$(git rev-parse --show-toplevel 2>/dev/null)" || {
    echo "doctor.sh: not in a git repo and no --repo given" >&2; exit 2; }
fi
[ -d "$repo" ] || { echo "doctor.sh: no such directory: $repo" >&2; exit 2; }
repo="$(cd "$repo" && pwd -P)"

claude_dir="$repo/.claude"
skills_dir="$claude_dir/skills"
project_dir="$claude_dir/project"
adapter="$project_dir/adapter.md"
settings="$claude_dir/settings.json"
template="$canonical/install/adapter.template.md"
bundles="$canonical/install/bundles.md"

err()  { printf '%-9s %s\n' "$1" "$2"; errors=$((errors + 1)); }
warn() { printf '%-9s %s\n' "WARN" "$1"; warnings=$((warnings + 1)); }
info() { [ "$quiet" -eq 1 ] || printf '%-9s %s\n' "INFO" "$1"; }
ok()   { [ "$quiet" -eq 1 ] || printf '%-9s %s\n' "OK" "$1"; }

rel()     { printf '%s' "${1#$repo/}"; }
homerel() { case "$1" in "$HOME"/*) printf '~%s' "${1#$HOME}" ;; *) printf '%s' "$1" ;; esac; }

echo "doctor: $repo"
[ -n "$bundle" ] && echo "bundle: $bundle"
echo

# ---------------------------------------------------------------- 1. plugin inventory
#
# Pure lookup, and deliberately the first thing that runs: it reads no repo state
# and prints nothing.
#
# A skill does not sit in `.claude/skills/` to reach a session — a plugin carries
# it. That is a lookup, not a judgement call. These are the only places a plugin's
# files ever live:
#
#   ~/.claude*/plugins/installed_plugins.json   each install's `installPath`
#   ~/.claude*/plugins/cache/<marketplace>/<plugin>[/<version>]
#   <repo>/plugins/<plugin>/                    a repo that ships its own
#
# Every config dir is scanned, not just ~/.claude: which one a session in this
# repo runs under is decided by $PWD in the user's shell and is not knowable from
# here, so "reachable from some config" is the honest question.

config_dirs="$(
  for cfg in "$HOME/.claude" "$HOME"/.claude-*; do
    [ -d "$cfg" ] && printf '%s\n' "$cfg"
  done | sort -u
)"

# Order matters and survives the dedupe below: every config's *live* installPath
# first, then the cache directories. `uninstall` and `update` leave the old cache
# directory behind, so `cache/<mkt>/<plugin>/` accumulates one per version ever
# installed and only the one named in installed_plugins.json is live. Reporting
# the first lexical match would name a stale copy — 1.1.0 ahead of 1.3.0 — which
# reads exactly like a consumer who never updated.
config_roots="$(
  {
    while IFS= read -r cfg; do
      [ -n "$cfg" ] || continue
      inst="$cfg/plugins/installed_plugins.json"
      [ -f "$inst" ] && grep -o '"installPath"[[:space:]]*:[[:space:]]*"[^"]*"' "$inst" |
        sed 's/.*"\(.*\)"$/\1/'
      true
    done <<< "$config_dirs"

    while IFS= read -r cfg; do
      [ -n "$cfg" ] || continue
      for d in "$cfg"/plugins/cache/*/* "$cfg"/plugins/cache/*/*/*; do
        [ -f "$d/.claude-plugin/plugin.json" ] && printf '%s\n' "$d"
      done
      true
    done <<< "$config_dirs"
  }
)"

# A repo that ships its own plugins. Resolved to a physical path so it dedupes
# against anything already found above.
#
# No apostrophes in the comments inside the substitution below, deliberately:
# bash 3.2 (the macOS system bash, and what this script runs under) does not strip
# `#` comments inside `$( )` before scanning for quotes, so one apostrophe there
# is a syntax error at a line 100+ further down.
repo_roots="$(
  for d in "$repo"/plugins/*; do
    [ -f "$d/.claude-plugin/plugin.json" ] && printf '%s\n' "$(cd "$d" && pwd -P)"
  done
  true
)"

# Deduped with awk rather than `sort -u`, so the live-install-first ordering above
# is preserved instead of being replaced by lexical order.
plugin_roots="$(
  {
    printf '%s\n' "$config_roots"
    printf '%s\n' "$repo_roots"
  } | grep -v '^[[:space:]]*$' | awk '!seen[$0]++'
)"

# Print the root of the plugin *named* $1, nothing if it is not reachable.
# Matched on the manifest's own name rather than on a path segment, so a cache
# layout with or without a version directory both work.
plugin_root_named() {
  local root
  while IFS= read -r root; do
    [ -n "$root" ] || continue
    [ -f "$root/.claude-plugin/plugin.json" ] || continue
    if grep -q "\"name\"[[:space:]]*:[[:space:]]*\"$1\"" "$root/.claude-plugin/plugin.json"; then
      printf '%s\n' "$root"; return 0
    fi
  done <<< "$plugin_roots"
  return 1
}

# ---------------------------------------------------------------- 2. layout

if [ ! -d "$claude_dir" ]; then
  info "no $(rel "$claude_dir") — nothing is wired in this repo"
  [ -z "$bundle" ] && { echo; echo "0 problems"; exit 0; }
fi

if [ ! -d "$skills_dir" ]; then
  info "no $(rel "$skills_dir") — this repo owns no skills of its own"
  info "(normal: a published skill reaches a session from an installed plugin)"
fi

# ---------------------------------------------------------------- 3. plugins this repo enables
#
# A project can enable a plugin in its own committed settings — the third place
# a skill can come from, and the only one that travels with the repo.

needs_adapter=0
enabled_plugins=""
if [ -f "$settings" ]; then
  # Flatten first: settings.json is hand-edited and turns up both pretty-printed
  # and on a single line, and a line-oriented parse silently reads nothing from
  # the second shape. Values in this object are booleans, so the first `}` after
  # the key really is the end of it.
  enabled_plugins="$(tr -d '\n' < "$settings" |
    sed -n 's/.*"enabledPlugins"[[:space:]]*:[[:space:]]*{\([^}]*\)}.*/\1/p' |
    grep -o '"[^"]*@[^"]*"' | tr -d '"')"
fi

while IFS= read -r plug; do
  [ -n "$plug" ] || continue
  pname="${plug%@*}"
  if proot="$(plugin_root_named "$pname")"; then
    info "$plug is enabled by $(rel "$settings") and reachable at $(homerel "$proot")"
    # Its skills read the adapter → this repo owes one, even with no .claude/skills/.
    grep -rqs '\.claude/project/adapter\.md' "$proot" 2>/dev/null && needs_adapter=1
  else
    info "$plug is enabled by $(rel "$settings") but is in no local plugin cache yet — it installs on next session start there"
  fi
done <<< "$enabled_plugins"

# ---------------------------------------------------------------- 4. entries
#
# A project may keep its own skills in `.claude/skills/`. That is the project's
# business and this script does not second-guess it: no shadow check, no fork
# check, no comparison against what a plugin happens to provide. Skills reach a
# session from an installed plugin, so an entry here is a project-owned skill
# rather than a competing copy of a published one.
#
# What is still checked is what is broken rather than merely different: a link
# with no target, and a `_shared/` the project must never own (#11).

installed=""   # newline-separated "<name>\t<physical path>"

if [ -d "$skills_dir" ]; then
  for entry in "$skills_dir"/*; do
    [ -e "$entry" ] || [ -L "$entry" ] || continue
    name="$(basename "$entry")"

    if [ -L "$entry" ]; then
      if [ ! -e "$entry" ]; then
        err "DANGLING" "$(rel "$entry") -> $(readlink "$entry") (target does not exist)"
        continue
      fi
      phys="$(cd "$entry" 2>/dev/null && pwd -P)" || { err "DANGLING" "$(rel "$entry") is not a directory"; continue; }
      installed="$installed$name	$phys
"
      info "$(rel "$entry") -> $(homerel "$phys")"
      continue
    fi

    if [ -d "$entry" ]; then
      if [ "$name" = "_shared" ]; then
        err "BANNED" "$(rel "$entry") — a project never owns a _shared/ (#11); it shadows canonical for any copied skill"
      else
        info "$(rel "$entry") is project-owned"
      fi
      continue
    fi

    warn "$(rel "$entry") is a loose file in the skills directory"
  done
fi

# Any `_shared/` under .claude/ is the banned shape wherever it hides.
while IFS= read -r found; do
  [ -n "$found" ] || continue
  [ "$found" = "$skills_dir/_shared" ] && continue   # already reported above
  err "BANNED" "$(rel "$found") — a project never owns a _shared/ (#11)"
done < <(find "$claude_dir" -type d -name _shared 2>/dev/null)

# ---------------------------------------------------------------- 5. dangling links anywhere under .claude/

while IFS= read -r link; do
  [ -n "$link" ] || continue
  case "$link" in "$skills_dir"/*) continue ;; esac   # already reported above
  err "DANGLING" "$(rel "$link") → $(readlink "$link") (target does not exist)"
done < <(find "$claude_dir" -type l ! -exec test -e {} \; -print 2>/dev/null)

# ---------------------------------------------------------------- 6. the adapter

while IFS=$'\t' read -r name phys; do
  [ -n "$name" ] || continue
  if grep -rqs '\.claude/project/adapter\.md' "$phys" 2>/dev/null; then
    needs_adapter=1
    break
  fi
done <<< "$installed"

if [ "$needs_adapter" -eq 1 ] && [ ! -f "$adapter" ]; then
  err "HOLE" "$(rel "$adapter") is missing, but a skill reaching this repo reads it"
elif [ -f "$adapter" ]; then
  # 7a. still a template?
  if head -5 "$adapter" | grep -q 'TEMPLATE'; then
    err "UNFILLED" "$(rel "$adapter") still carries the TEMPLATE marker — it was copied, never filled"
  fi

  # 7b. surviving template placeholders. A token counts only if the template
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

  # 7c. sibling pointers registered in the adapter's `## Project gates` table
  # must exist. A gate is only ever named there — the registry is what keeps
  # canonical skills generic instead of forked to hardcode a project's
  # filename — so scope the search to that section rather than the whole
  # file. Whole-file prose routinely mentions `../_shared/x.md` (this repo's
  # own adapter does, describing the layout in `## Repo discipline`), and
  # that literally contains the substring `./_shared/x.md`, so strip real
  # `../`-relative paths first before looking for `./`-relative pointers —
  # otherwise their tail gets mistaken for a sibling pointer.
  gates_section="$(awk '/^## Project gates/{flag=1; next} /^## /{flag=0} flag' "$adapter")"
  while IFS= read -r ptr; do
    [ -n "$ptr" ] || continue
    target="$project_dir/${ptr#./}"
    if [ ! -f "$target" ]; then
      err "POINTER" "$(rel "$adapter") points at \`$ptr\`, but $(rel "$target") does not exist"
    fi
  done < <(printf '%s\n' "$gates_section" | sed -E 's#\.\./[A-Za-z0-9._/-]+\.md##g' | grep -o '\./[A-Za-z0-9._/-]\{1,\}\.md' | sort -u)

  ok "$(rel "$adapter") present"
fi

# ---------------------------------------------------------------- 7. ../_shared/ resolution

while IFS=$'\t' read -r name phys; do
  [ -n "$name" ] || continue
  while IFS= read -r ref; do
    [ -n "$ref" ] || continue
    target="$phys/$ref"
    if [ ! -f "$target" ]; then
      err "SHARED" "$name reads $ref, which does not resolve (looked in $(dirname "$phys")/_shared/)"
    fi
  done < <(grep -rhoE '\.\./_shared/[A-Za-z0-9._-]+\.md' "$phys" 2>/dev/null | sort -u)
done <<< "$installed"

# ---------------------------------------------------------------- 8. bundle
#
# A bundle declares adapter sections and gate templates. It does **not** list
# skills — placing skills is the platform's job — so "is what this bundle needs
# reachable here?" is answered against those two fields, plus a look at whether a
# plugin of the same name is reachable. Bundle and plugin are separate namespaces
# (`prd-qa` ships as plain skills and has no plugin at all), so a bundle with no
# matching plugin is INFO, never an error.

if [ -n "$bundle" ]; then
  if [ ! -f "$bundles" ]; then
    warn "no bundle manifest at $bundles — skipped the bundle check"
  else
    section="$(awk -v b="$bundle" '
      $0 ~ "^## `" b "`$" { inb = 1; next }
      /^## / { inb = 0 }
      inb' "$bundles")"

    if [ -z "${section//[[:space:]]/}" ]; then
      err "BUNDLE" "no bundle named '$bundle' in $bundles"
    else
      status="$(printf '%s\n' "$section" | sed -n 's/^- \*\*Status:\*\* *//p' | head -1)"
      case "$status" in
        ready) ;;
        "")    warn "$bundle declares no Status in $bundles" ;;
        *)     err "BUNDLE" "$bundle is '$status' in $bundles — not bootstrappable here" ;;
      esac

      # Adapter sections: the one thing no distribution mechanism delivers, so
      # the one thing worth checking. Headings are matched by prefix, the same
      # rule bundles.md states.
      wanted="$(printf '%s\n' "$section" | sed -n 's/^- \*\*Adapter sections:\*\* *//p' | head -1 |
                grep -o '`[^`]*`' | tr -d '`')"
      if [ -n "$wanted" ]; then
        if [ ! -f "$adapter" ]; then
          err "HOLE" "$(rel "$adapter") is missing, but bundle '$bundle' needs sections filled in it"
        else
          while IFS= read -r sec; do
            [ -n "$sec" ] || continue
            awk -v s="$sec" 'index($0, s) == 1 { found = 1 } END { exit !found }' "$adapter" ||
              err "UNFILLED" "$(rel "$adapter") has no \`$sec\` section, which bundle '$bundle' needs"
          done <<< "$wanted"
        fi
      fi

      # Gate templates the bundle offers have to exist in canonical, or the
      # install step that offers them copies nothing.
      while IFS= read -r gate; do
        [ -n "$gate" ] || continue
        [ -f "$canonical/$gate" ] ||
          err "MISSING" "$bundle offers the gate template \`$gate\`, which $canonical does not ship"
      done < <(printf '%s\n' "$section" | sed -n 's/^- \*\*Gates:\*\* *//p' | head -1 |
               grep -o '`install/gates/[^`]*`' | tr -d '`')

      # Skills themselves: reachable, or not, via plugins.
      if proot="$(plugin_root_named "$bundle")"; then
        case "$proot" in
          "$repo"/*) info "the \`$bundle\` plugin is shipped by this repo itself ($(rel "$proot")) — self-hosted, not installed from a marketplace" ;;
          *)         info "the \`$bundle\` plugin is reachable at $(homerel "$proot")" ;;
        esac
      else
        info "no plugin named \`$bundle\` is reachable from any ~/.claude*/plugins — expected when the bundle ships as plain skills, otherwise install it from the marketplace"
      fi
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
