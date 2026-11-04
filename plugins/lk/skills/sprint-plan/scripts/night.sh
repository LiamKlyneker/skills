#!/usr/bin/env bash
#
# night.sh — run the implementation loop once per `runnable` row of a sprint plan,
# serially, under caps the caller sets, and write a per-night report beside the plan.
#
# It reads one input, the plan file, plus the env file beside it. It calls no tracker
# API, reads no git state and posts nothing anywhere. The only thing it reads from a
# run is the exit code: 0 sets the row `ran`, anything else sets it `needs-human`.
# The plan file's shape is defined in the sprint-plan skill's SKILL.md.
#
# Usage:
#   night.sh [--plan <path>] [--env <path>] [--dry-run]
#
#   --plan     the plan file (default: plan.md beside this script)
#   --env      the env file (default: night.env beside the plan); must be mode 0600
#   --dry-run  print the commands a night would run and the states it would set;
#              run nothing, write nothing, take no lock, and accept a missing env file
#
# Env file variables (all optional except the auth token on a real run):
#   CLAUDE_CODE_OAUTH_TOKEN  long-lived token from `claude setup-token`
#   NIGHT_MODEL              orchestrator model, passed as --model
#   NIGHT_WORKER_MODEL       worker model, exported as CLAUDE_CODE_SUBAGENT_MODEL
#   NIGHT_ALLOWED_TOOLS      comma-separated allow-list passed as --allowedTools;
#                            Bash(kill:*) is always added: an unattended Stop ends the run with it
#   NIGHT_PERMISSION_MODE    default dontAsk: a tool off the allow-list is denied
#   NIGHT_MAX_RUNS           rows run per night (default 3)
#   NIGHT_TIMEOUT_SECONDS    outer wall-clock cap per run (default 14400)
#   NIGHT_MAX_TURNS          turn cap per run (default 400)
#   NIGHT_MAX_BUDGET_USD     last-fence dollar cap per run (default 200)
#   NIGHT_CLONES_DIR         where the dedicated clones live (default: the plan's root)
#   NIGHT_CLAUDE_BIN         the claude binary (default: claude)
#
# Exit: 0 night finished (row outcomes are in the report) · 2 usage or setup error
#       · 3 another night holds the lock

set -uo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
plan="$script_dir/plan.md"
env_file=""
dry_run=0

while [ $# -gt 0 ]; do
  case "$1" in
    --plan)    plan="${2:-}"; shift 2 ;;
    --env)     env_file="${2:-}"; shift 2 ;;
    --dry-run) dry_run=1; shift ;;
    -h|--help) sed -n '2,32p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *)         echo "night.sh: unknown argument '$1'" >&2; exit 2 ;;
  esac
done

[ -f "$plan" ] || { echo "night.sh: no plan file at $plan" >&2; exit 2; }
plan="$(cd "$(dirname "$plan")" && pwd -P)/$(basename "$plan")"
sprint_dir="$(dirname "$plan")"
root="$(dirname "$sprint_dir")"
[ -n "$env_file" ] || env_file="$sprint_dir/night.env"

say() { printf '%s\n' "$*"; }

# ---------------------------------------------------------------- env file

file_mode() { stat -c %a "$1" 2>/dev/null || stat -f %Lp "$1" 2>/dev/null; }

if [ -f "$env_file" ]; then
  mode="$(file_mode "$env_file")"
  if [ "$mode" != "600" ]; then
    echo "night.sh: $env_file is mode $mode; it carries a token and must be 0600" >&2
    exit 2
  fi
  set -a
  # shellcheck disable=SC1090
  . "$env_file"
  set +a
elif [ "$dry_run" -eq 1 ]; then
  say "env: no file at $env_file; the dry run uses defaults"
else
  echo "night.sh: no env file at $env_file" >&2
  exit 2
fi

max_runs="${NIGHT_MAX_RUNS:-3}"
timeout_s="${NIGHT_TIMEOUT_SECONDS:-14400}"
max_turns="${NIGHT_MAX_TURNS:-400}"
budget="${NIGHT_MAX_BUDGET_USD:-200}"
perm_mode="${NIGHT_PERMISSION_MODE:-dontAsk}"
allowed="${NIGHT_ALLOWED_TOOLS:-}"
clones="${NIGHT_CLONES_DIR:-$root}"
claude_bin="${NIGHT_CLAUDE_BIN:-claude}"

for n in "$max_runs" "$timeout_s" "$max_turns"; do
  case "$n" in ''|*[!0-9]*) echo "night.sh: caps must be whole numbers, got '$n'" >&2; exit 2 ;; esac
done

if [ "$dry_run" -eq 0 ]; then
  [ -n "${CLAUDE_CODE_OAUTH_TOKEN:-}${ANTHROPIC_API_KEY:-}" ] || {
    echo "night.sh: the env file sets no CLAUDE_CODE_OAUTH_TOKEN" >&2; exit 2; }
  [ -n "$allowed" ] || {
    echo "night.sh: the env file sets no NIGHT_ALLOWED_TOOLS; a night with no allow-list can do nothing" >&2; exit 2; }
  command -v "$claude_bin" >/dev/null || { echo "night.sh: '$claude_bin' not on PATH" >&2; exit 2; }
  command -v timeout >/dev/null || { echo "night.sh: 'timeout' (coreutils) not on PATH" >&2; exit 2; }
fi
case ",$allowed," in *",Bash(kill:*),"*) ;; *) allowed="${allowed:+$allowed,}Bash(kill:*)" ;; esac
[ -n "${NIGHT_WORKER_MODEL:-}" ] && export CLAUDE_CODE_SUBAGENT_MODEL="$NIGHT_WORKER_MODEL"

# ---------------------------------------------------------------- lock

lock="$sprint_dir/night.lock"
if [ "$dry_run" -eq 0 ]; then
  if ! mkdir "$lock" 2>/dev/null; then
    holder="$(cat "$lock/pid" 2>/dev/null || true)"
    if [ -n "$holder" ] && kill -0 "$holder" 2>/dev/null; then
      echo "night.sh: another night holds $lock (pid $holder); exiting" >&2
      exit 3
    fi
    # The holder is gone without releasing the lock, so it was killed; take it over.
    say "lock: stale lock from pid ${holder:-unknown} removed"
    rm -rf "$lock"
    mkdir "$lock" || { echo "night.sh: cannot take $lock" >&2; exit 3; }
  fi
  echo $$ > "$lock/pid"
  trap 'rm -rf "$lock"' EXIT
fi

# ---------------------------------------------------------------- plan file

# Rows of the `## Groups` table as `id<TAB>repo<TAB>state<TAB>prd`. Columns are found
# by header name, so a developer who reorders them breaks nothing.
rows() {
  awk -F'|' '
    function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
    /^## / { in_groups = ($0 ~ /^## Groups[ \t]*$/); hdr = 0; next }
    !in_groups || $0 !~ /^[ \t]*\|/ { next }
    !hdr {
      for (i = 2; i < NF; i++) col[trim($i)] = i
      hdr = 1; next
    }
    $0 ~ /^[ \t]*\|[ \t:|-]+$/ { next }
    { printf "%s\t%s\t%s\t%s\n", trim($col["Id"]), trim($col["Repo"]), trim($col["State"]), trim($col["PRD"]) }
  ' "$plan"
}

set_state() {
  local id="$1" state="$2" tmp
  tmp="$(mktemp "$sprint_dir/.plan.XXXXXX")" || return 1
  awk -F'|' -v OFS='|' -v id="$id" -v state="$state" '
    function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
    /^## / { in_groups = ($0 ~ /^## Groups[ \t]*$/); hdr = 0; print; next }
    !in_groups || $0 !~ /^[ \t]*\|/ { print; next }
    !hdr { for (i = 2; i < NF; i++) col[trim($i)] = i; hdr = 1; print; next }
    trim($col["Id"]) == id { $col["State"] = " " state " " }
    { print }
  ' "$plan" > "$tmp" && mv "$tmp" "$plan"
}

grep -q '^## Groups[[:space:]]*$' "$plan" || { echo "night.sh: $plan has no '## Groups' table" >&2; exit 2; }
missing="$(awk -F'|' '
  function trim(s) { gsub(/^[ \t]+|[ \t]+$/, "", s); return s }
  /^## / { in_groups = ($0 ~ /^## Groups[ \t]*$/); next }
  in_groups && /^[ \t]*\|/ {
    for (i = 2; i < NF; i++) col[trim($i)] = 1
    split("Id Repo State PRD", need, " ")
    for (k in need) if (!(need[k] in col)) printf "%s ", need[k]
    exit
  }
' "$plan")"
[ -z "$missing" ] || { echo "night.sh: the Groups table has no column: $missing" >&2; exit 2; }

# ---------------------------------------------------------------- report

night="$(date +%Y-%m-%d)"
night_dir="$sprint_dir/nights/$night"
report="$sprint_dir/nights/$night.md"

note() {
  if [ "$dry_run" -eq 1 ]; then say "$*"; else printf '%s\n' "$*" >> "$report"; fi
}

if [ "$dry_run" -eq 0 ]; then
  mkdir -p "$night_dir" || exit 2
  { printf '# Night %s\n\n' "$night"
    printf -- '- Plan: %s\n- Started: %s\n- Caps: %s runs · %ss wall-clock · %s turns · %s USD last fence\n\n' \
      "$plan" "$(date '+%Y-%m-%d %H:%M:%S %z')" "$max_runs" "$timeout_s" "$max_turns" "$budget"
  } >> "$report"
else
  say "dry run: plan $plan"
  say "dry run: caps $max_runs runs · ${timeout_s}s wall-clock · $max_turns turns · $budget USD last fence"
fi

# A row still `running` with no lock holder was cut off by a crash or a reboot.
while IFS=$'\t' read -r id repo state prd; do
  [ "$state" = "running" ] || continue
  note "- $id: left \`running\` by an earlier night; set \`needs-human\`"
  [ "$dry_run" -eq 1 ] || set_state "$id" needs-human
done < <(rows)

loop_command() {
  case "$1" in
    '#'[0-9]*)                       printf '/prd-workflow:work-on-prd %s --gate=end --unattended' "$1" ;;
    https://github.com/*/issues/*)   printf '/prd-workflow:work-on-prd %s --gate=end --unattended' "$1" ;;
    https://dev.azure.com/*|https://*.visualstudio.com/*)
                                     printf '/ado-workflow:work-on-spec %s --gate=end --unattended' "$1" ;;
    *) return 1 ;;
  esac
}

new_session_id() {
  if command -v uuidgen >/dev/null; then uuidgen | tr '[:upper:]' '[:lower:]'
  else cat /proc/sys/kernel/random/uuid
  fi
}

# One line of the result JSON's fields, for the report. Any missing tool or field
# degrades to a pointer at the raw file.
summarise() {
  local json="$1"
  if command -v jq >/dev/null; then
    jq -r '"turns \(.num_turns // "?") · cost estimate \(.total_cost_usd // "?") USD · \(.subtype // "?")"' "$json" 2>/dev/null && return
  elif command -v python3 >/dev/null; then
    python3 -I -c 'import json,sys
d=json.load(open(sys.argv[1]))
print("turns %s · cost estimate %s USD · %s" % (d.get("num_turns","?"), d.get("total_cost_usd","?"), d.get("subtype","?")))' "$json" 2>/dev/null && return
  fi
  printf 'result JSON unreadable; raw output at %s' "$json"
}

# ---------------------------------------------------------------- the night

ran=0
while IFS=$'\t' read -r id repo state prd; do
  [ "$state" = "runnable" ] || continue
  if [ "$ran" -ge "$max_runs" ]; then
    note "- $id: not run; the night's cap of $max_runs runs is reached"
    continue
  fi

  clone="$clones/$repo"
  if ! cmd="$(loop_command "$prd")"; then
    note "- $id: PRD cell '$prd' names no GitHub PRD or Azure DevOps spec; set \`needs-human\`"
    [ "$dry_run" -eq 1 ] || set_state "$id" needs-human
    continue
  fi
  if [ -z "$repo" ] || [ ! -d "$clone" ]; then
    note "- $id: no clone at $clone; set \`needs-human\`"
    [ "$dry_run" -eq 1 ] || set_state "$id" needs-human
    continue
  fi

  sid="$(new_session_id)"
  argv=(timeout --kill-after=60 "$timeout_s" "$claude_bin" -p "$cmd"
        --session-id "$sid" --output-format json
        --permission-mode "$perm_mode" --max-turns "$max_turns" --max-budget-usd "$budget")
  [ -n "$allowed" ]              && argv+=(--allowedTools "$allowed")
  [ -n "${NIGHT_MODEL:-}" ]      && argv+=(--model "$NIGHT_MODEL")
  ran=$((ran + 1))

  if [ "$dry_run" -eq 1 ]; then
    say "- $id: set running"
    say "  cd $(printf '%q' "$clone")"
    printf '  '; printf '%q ' "${argv[@]}"; printf '\n'
    say "  then set ran on exit 0, needs-human on any other exit"
    continue
  fi

  set_state "$id" running
  out="$night_dir/$id.json"
  err="$night_dir/$id.stderr"
  started="$(date +%s)"
  ( cd "$clone" && "${argv[@]}" ) > "$out" 2> "$err" < /dev/null
  rc=$?
  elapsed=$(( $(date +%s) - started ))

  if [ "$rc" -eq 0 ]; then new_state=ran; else new_state=needs-human; fi
  set_state "$id" "$new_state"

  why=""
  [ "$rc" -eq 124 ] && why=" (wall-clock cap)"
  # shellcheck disable=SC2016
  { printf '## %s\n\n' "$id"
    printf -- '- Command: `%s` in `%s`\n' "$cmd" "$clone"
    printf -- '- Session: `%s`\n' "$sid"
    printf -- '- Exit: %s%s → `%s`\n' "$rc" "$why" "$new_state"
    printf -- '- Wall-clock: %ss\n' "$elapsed"
    printf -- '- Result: %s\n' "$(summarise "$out")"
    printf -- '- Raw: `nights/%s/%s.json`, `nights/%s/%s.stderr`\n\n' "$night" "$id" "$night" "$id"
  } >> "$report"
done < <(rows)

if [ "$ran" -eq 0 ]; then note "- No row was \`runnable\`."; fi
if [ "$dry_run" -eq 1 ]; then
  say "dry run: nothing run, nothing written"
else
  printf -- '\nFinished: %s\n' "$(date '+%Y-%m-%d %H:%M:%S %z')" >> "$report"
fi
exit 0
