## What changes, and why

<!-- If this changes a skill's behaviour, say what an agent will now do differently. -->

## Checklist

- [ ] `python3 .github/scripts/validate_skills.py` passes
- [ ] I ran the affected skill end to end at least once
- [ ] Frontmatter `description` says *when to invoke*, not only what it does
- [ ] No new instruction to fetch remote content, send data anywhere, or run commands
      beyond what the skill's stated purpose needs (see `SECURITY.md`)
- [ ] Any subagent type named is spelled for the right route — `plugin:agent` inside a
      plugin, bare name only on the plain-skill route

## Notes for review

<!-- Anything you weren't sure about, or that you'd like pushed back on. -->
