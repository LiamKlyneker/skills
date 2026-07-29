#!/usr/bin/env bash
#
# doctor.sh — check that a project's skill wiring still matches the layout.
#
# Every failure class here is one that is silent today: a forked copy that looks
# like an install, a leftover `_shared/` that shadows canonical, an adapter still
# carrying template placeholders, a pointer to a gate file nobody wrote.
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
# and prints nothing, so the config-level scan below it can run even for a repo
# that turns out to have no `.claude/` at all — the case where the layout section
# below stops early. A machine-wide double-load is not the repo's fault and is not
# the repo's to hide.
#
# A skill no longer has to sit in `.claude/skills/` to reach a session — a plugin
# can carry it. That is a lookup, not a judgement call. These are the only places
# a plugin's files ever live, and a skill is plugin-provided exactly when
# `<plugin root>/skills/<name>` exists:
#
#   ~/.claude*/plugins/installed_plugins.json   each install's `installPath`
#   ~/.claude*/plugins/cache/<marketplace>/<plugin>[/<version>]
#   ~/.claude*/skills/<plugin>/                 skills-dir plugins
#   <repo>/plugins/<plugin>/                    a repo that ships its own
#
# Every config dir is scanned, not just ~/.claude: which one a session in this
# repo runs under is decided by $PWD in the user's shell and is not knowable from
# here, so "reachable from some config" is the honest question.

# Enumerated once and reused: section 2 walks this same list to ask which of these
# configs hand-place a skill their own plugins already provide.
config_dirs="$(
  for cfg in "$HOME/.claude" "$HOME"/.claude-*; do
    [ -d "$cfg" ] && printf '%s\n' "$cfg"
  done | sort -u
)"

# "<config dir><TAB><plugin root>". Keeping the association is what lets a later
# check ask "reachable from *this* config" rather than "reachable from anywhere":
# the configs share no plugin state, so a plugin cached under one says nothing
# about a symlink under another.
config_roots="$(
  while IFS= read -r cfg; do
    [ -n "$cfg" ] || continue
    {
      inst="$cfg/plugins/installed_plugins.json"
      [ -f "$inst" ] && grep -o '"installPath"[[:space:]]*:[[:space:]]*"[^"]*"' "$inst" |
        sed 's/.*"\(.*\)"$/\1/'
      for d in "$cfg"/plugins/cache/*/* "$cfg"/plugins/cache/*/*/* "$cfg"/skills/*; do
        [ -f "$d/.claude-plugin/plugin.json" ] && printf '%s\n' "$d"
      done
      true
    } | sort -u | awk -v c="$cfg" 'NF { print c "\t" $0 }'
  done <<< "$config_dirs"
)"

# A repo that ships its own, plus a plugin dropped into the skills dir of this
# repo — the project-scoped half of skills-dir mode, which `claude plugin list`
# reports as `<name>@skills-dir` with `Scope: project`. Resolved to a physical
# path so a project link pointing at a plugin already found above dedupes into
# one root rather than reading as two.
#
# No apostrophes in the comments inside the substitution below, deliberately:
# bash 3.2 (the macOS system bash, and what this script runs under) does not strip
# `#` comments inside `$( )` before scanning for quotes, so one apostrophe there
# is a syntax error at a line 100+ further down.
repo_roots="$(
  for d in "$repo"/plugins/* "$skills_dir"/*; do
    [ -f "$d/.claude-plugin/plugin.json" ] && printf '%s\n' "$(cd "$d" && pwd -P)"
  done
  true
)"

plugin_roots="$(
  {
    printf '%s\n' "$config_roots" | cut -f2-
    printf '%s\n' "$repo_roots"
  } | grep -v '^[[:space:]]*$' | sort -u
)"

# Print the root of a plugin that provides skill $1, nothing if none does.
# $2, when given, is the newline-separated root list to search; it defaults to
# every root reachable from anywhere, which is the honest question for a repo
# whose config is not knowable from here. The config-level scan passes one
# config's roots instead, because "loads twice" is only true within one config.
plugin_provides() {
  local root
  while IFS= read -r root; do
    [ -n "$root" ] || continue
    [ -d "$root/skills/$1" ] && { printf '%s\n' "$root"; return 0; }
  done <<< "${2-$plugin_roots}"
  return 1
}

# Print the root of the plugin *named* $1, nothing if it is not reachable.
# Matched on the manifest's own name rather than on a path segment, so cache
# layout (with or without a version directory) and skills-dir plugins both work.
# $2 narrows the search the same way it does for plugin_provides.
plugin_root_named() {
  local root
  while IFS= read -r root; do
    [ -n "$root" ] || continue
    [ -f "$root/.claude-plugin/plugin.json" ] || continue
    if grep -q "\"name\"[[:space:]]*:[[:space:]]*\"$1\"" "$root/.claude-plugin/plugin.json"; then
      printf '%s\n' "$root"; return 0
    fi
  done <<< "${2-$plugin_roots}"
  return 1
}

# ---------------------------------------------------------------- 2. config skills dirs
#
# Section 4 asks whether a plugin can reach *this repo*. This asks the other half,
# which no project can see from the inside: does a config directory hand-place a
# skill that a plugin installed in that same config already provides. Both routes
# load, so the skill loads twice — the same failure the entries pass below catches
# inside `.claude/skills/`, one level out, where the repo has no visibility.
#
# Scoped per config, deliberately. Asked globally this check would report
# `~/.claude/skills/grill-me` as a double-load because an unrelated plugin in a
# *different* config happens to ship a skill of that name.
#
# The walk is announced whether or not it finds anything. A checker that silently
# skipped its input is indistinguishable from a clean one, and that is precisely
# the failure class this check exists to catch rather than inherit.

while IFS= read -r cfg; do
  [ -n "$cfg" ] || continue
  cfg_skills="$cfg/skills"

  if [ ! -d "$cfg_skills" ]; then
    info "double-load scan: $(homerel "$cfg") has no skills/ — nothing hand-placed there"
    continue
  fi

  cfg_roots="$(printf '%s\n' "$config_roots" | awk -F'\t' -v c="$cfg" '$1 == c { print $2 }')"

  n_seen=0; n_skills=0; n_roots=0; n_skipped=""
  for entry in "$cfg_skills"/*; do
    [ -e "$entry" ] || [ -L "$entry" ] || continue
    n_seen=$((n_seen + 1))
    name="$(basename "$entry")"

    # A plugin root parked in a skills dir is not a skill: its skills sit one
    # level down, so name-matching it as one matches it against itself and reports
    # every skills-dir plugin as its own duplicate. The real duplication for one of
    # these is the same plugin *also* installed from a marketplace into this config
    # — both routes load, and every skill it carries loads twice.
    if [ -f "$entry/.claude-plugin/plugin.json" ]; then
      n_roots=$((n_roots + 1))
      pname="$(grep -o '"name"[[:space:]]*:[[:space:]]*"[^"]*"' "$entry/.claude-plugin/plugin.json" |
               head -1 | sed 's/.*"\(.*\)"$/\1/')"
      others="$(printf '%s\n' "$cfg_roots" | grep -vxF "$entry")"
      if [ -n "$pname" ] && dup="$(plugin_root_named "$pname" "$others")"; then
        case "$dup" in
          "$repo"/*|"$canonical"/*) ;;
          *) info "$(homerel "$entry") is a skills-dir plugin and $pname is also installed at $(homerel "$dup") — every skill it carries loads twice under $(homerel "$cfg")" ;;
        esac
      fi
      continue
    fi

    # Another repo's shared reference, not a skill of ours —
    # `~/.claude-schmiede/skills/_shared` is the live example. Out of scope here,
    # and named in the count rather than quietly dropped from it.
    if [ "$name" = "_shared" ]; then
      n_skipped="${n_skipped:+$n_skipped, }$name"
      continue
    fi

    n_skills=$((n_skills + 1))
    # Same judgement the entries pass makes: a plugin root inside the canonical
    # repo (or the repo under test) is *source*, not a second install, so a link
    # pointing into a checkout is one copy of the skill and not two.
    if proot="$(plugin_provides "$name" "$cfg_roots")"; then
      case "$proot" in
        "$repo"/*|"$canonical"/*) ;;
        *) info "$(homerel "$entry") is symlinked here and also provided by the plugin at $(homerel "$proot") — $name loads twice under $(homerel "$cfg")" ;;
      esac
    fi
  done

  # Phrased "label: count" so it reads correctly at any count, including 1.
  detail="skills: $n_skills"
  [ "$n_roots" -gt 0 ] && detail="$detail, skills-dir plugin roots: $n_roots"
  [ -n "$n_skipped" ] && detail="$detail; skipped $n_skipped"
  info "double-load scan: $(homerel "$cfg_skills") — $n_seen entries, $((n_skills + n_roots)) checked ($detail)"
done <<< "$config_dirs"

# ---------------------------------------------------------------- 3. layout

if [ ! -d "$claude_dir" ]; then
  info "no $(rel "$claude_dir") — nothing is wired in this repo"
  [ -z "$bundle" ] && { echo; echo "0 problems"; exit 0; }
fi

if [ ! -d "$skills_dir" ]; then
  info "no $(rel "$skills_dir") — no skills are placed inside this repo"
  info "(normal: skills reach a session from a plugin or a global config dir)"
fi

# ---------------------------------------------------------------- 4. plugins this repo enables
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

# ---------------------------------------------------------------- 5. entries

installed=""   # newline-separated "<name>\t<physical path>"

if [ -d "$skills_dir" ]; then
  for entry in "$skills_dir"/*; do
    [ -e "$entry" ] || [ -L "$entry" ] || continue
    name="$(basename "$entry")"

    # An entry here can be a *plugin root* rather than a skill — skills-dir mode,
    # and how this repo self-hosts its own plugin while keeping edit-in-place
    # authoring. A plugin is not a skill: its skills sit one level down at
    # `<plugin>/skills/<name>/`, so `../_shared/` resolves from *there*. Checking
    # the plugin root as though it were a skill invents SHARED failures for every
    # shared file its skills legitimately read. Register the skills it carries
    # instead, at their real paths.
    if entry_phys="$(cd "$entry" 2>/dev/null && pwd -P)" &&
       [ -f "$entry_phys/.claude-plugin/plugin.json" ]; then
      info "$(rel "$entry") is a skills-dir plugin root — its skills load from the plugin, not as entries here"
      for sk in "$entry_phys"/skills/*; do
        [ -d "$sk" ] || continue
        skname="$(basename "$sk")"
        [ "$skname" = "_shared" ] && continue
        installed="$installed$skname	$(cd "$sk" && pwd -P)
"
      done
      continue
    fi

    if [ -L "$entry" ]; then
      if [ ! -e "$entry" ]; then
        err "DANGLING" "$(rel "$entry") → $(readlink "$entry") (target does not exist)"
        continue
      fi
      phys="$(cd "$entry" 2>/dev/null && pwd -P)" || { err "DANGLING" "$(rel "$entry") is not a directory"; continue; }
      installed="$installed$name	$phys
"
      # Same skill from two directions loads twice. A root inside this repo is
      # source, not an install, so it does not count as a second copy.
      if proot="$(plugin_provides "$name")"; then
        case "$proot" in
          "$repo"/*) ;;
          *) info "$(rel "$entry") is symlinked here and also provided by the plugin at $(homerel "$proot") — $name loads twice" ;;
        esac
      fi
      continue
    fi

    if [ -d "$entry" ]; then
      if [ "$name" = "_shared" ]; then
        err "BANNED" "$(rel "$entry") — a project never owns a _shared/ (#11); it shadows canonical for any copied skill"
      elif [ -d "$canonical/$name" ]; then
        err "FORK" "$(rel "$entry") is a real directory, not a symlink — it shadows the canonical skill of the same name"
      elif proot="$(plugin_provides "$name")"; then
        err "FORK" "$(rel "$entry") is a real directory, not a symlink — it shadows the $name skill the plugin at $(homerel "$proot") provides"
      else
        # Nothing of that name in canonical and no plugin providing it: there is
        # nothing to shadow, so this is a skill the project genuinely owns — the
        # one legitimate reason for a real directory here.
        info "$(rel "$entry") is project-owned (no skill of that name in canonical or in any reachable plugin)"
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

# ---------------------------------------------------------------- 6. dangling links anywhere under .claude/

while IFS= read -r link; do
  [ -n "$link" ] || continue
  case "$link" in "$skills_dir"/*) continue ;; esac   # already reported above
  err "DANGLING" "$(rel "$link") → $(readlink "$link") (target does not exist)"
done < <(find "$claude_dir" -type l ! -exec test -e {} \; -print 2>/dev/null)

# ---------------------------------------------------------------- 7. the adapter

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

# ---------------------------------------------------------------- 8. ../_shared/ resolution

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

# ---------------------------------------------------------------- 9. bundle
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
