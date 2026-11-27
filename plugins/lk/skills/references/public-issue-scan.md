# Public issue scan

The mechanical scan a skill runs over a title file and a body file before it posts them to
`LiamKlyneker/skills`, a public repo where an issue is permanent. The scan checks text against the
project the session runs in. It does not decide what a body may contain: each skill that uses it
states its own rule for permitted content, and the scan runs after that rule is applied.

## Inputs

- `<dir>`: the skill's scratchpad directory for this post, such as `<scratch>/report`. The scan
  writes `remote-terms.txt` and `denylist.txt` there.
- `<title>` and `<body>`: the files that are posted, written before the scan, so the text the scan
  checked is byte-identical to the text that is posted.

## The scan

Build the deny-list from the project, then grep:

```bash
r=<dir>; title=<title>; body=<body>
git remote 2>/dev/null | xargs -n1 git remote get-url 2>/dev/null | sort -u \
  | sed -E 's#\.git$##; s#^[a-z+]+://##; s#^[^@/]*@##' | tr '/:' '\n\n' \
  | grep -v '^$' > "$r/remote-terms.txt"
if [ -n "$(git remote 2>/dev/null)" ] && [ ! -s "$r/remote-terms.txt" ]; then
  echo "deny-list: the repo has a remote but no remote terms were built" >&2; exit 1
fi
{
  basename "$(git rev-parse --show-toplevel 2>/dev/null)"
  cat "$r/remote-terms.txt"
  git config user.email 2>/dev/null
  cat ~/.config/lk/report-denylist 2>/dev/null
} | grep -vixE '_git|v3|github\.com|gitlab\.com|bitbucket\.org|dev\.azure\.com|ssh\.dev\.azure\.com|skills|LiamKlyneker' \
  | awk 'length >= 3' | sort -u > "$r/denylist.txt"
cat "$title" "$body" | grep -inFf "$r/denylist.txt"
cat "$title" "$body" | grep -inE \
  '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}|https?://|/Users/|/home/|[A-Z]:\\|gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,}|xox[abpr]-|AKIA[0-9A-Z]{16}|[A-Fa-f0-9]{32,}|\b[A-Z][A-Z0-9]+-[0-9]+\b'
```

If the script stops with `deny-list:`, the scan did not run. Fix the build and run it again; never
treat that output as a clean scan. The harness replaces a dollar sign followed by a digit in a
loaded skill file with a skill argument, so the script never refers to a field by number.

`~/.config/lk/report-denylist` is optional, one term per line, and lives on the machine only —
company and client names the project's git metadata does not carry. Never commit it anywhere.

## A hit

**Any hit is rewritten under the calling skill's rule for permitted content, and the scan runs
again.** Some hits are false positives: a `github.com/LiamKlyneker/skills` link, a hash quoted from
this repo, a shape like `UTF-8`. Name each one in the last message, so the check is against the rule
rather than against taste.

**A hit that can be neither rewritten nor explained stops that item.** Post nothing for it. Show its
title, body and hit, and ask how to proceed.
