#!/usr/bin/env python3
"""Emits dashboard/catalog.json from the plugin tree.

Every value here is read from a file or is a count of things read. Nothing is
derived, scored, thresholded or judged: the page that consumes this file shows
the runner's own verdicts, so a computed one would be indistinguishable from
a recorded one.
"""

import datetime
import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGINS_DIR = os.path.join(REPO_ROOT, "plugins")
OUT_PATH = os.path.join(REPO_ROOT, "dashboard", "catalog.json")


# ---------------------------------------------------------------- YAML subset

_SCALAR_INT = re.compile(r"^-?\d+$")
_SCALAR_FLOAT = re.compile(r"^-?\d+\.\d+$")


def _scalar(text):
    text = text.strip()
    if text == "" or text in ("~", "null"):
        return None
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        return text[1:-1]
    if text in ("true", "True"):
        return True
    if text in ("false", "False"):
        return False
    if _SCALAR_INT.match(text):
        return int(text)
    if _SCALAR_FLOAT.match(text):
        return float(text)
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        if not inner:
            return []
        return [_scalar(part) for part in inner.split(",")]
    if text.startswith("{") and text.endswith("}"):
        inner = text[1:-1].strip()
        out = {}
        for part in _split_flow(inner):
            if ":" in part:
                k, v = part.split(":", 1)
                out[_scalar(k)] = _scalar(v)
        return out
    return text


def _split_flow(text):
    """Splits a flow mapping's body on commas that are not inside a nested flow."""
    parts, depth, current = [], 0, ""
    for ch in text:
        if ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(current)
            current = ""
        else:
            current += ch
    if current.strip():
        parts.append(current)
    return parts


def _indent(line):
    return len(line) - len(line.lstrip(" "))


def _strip_comment(line):
    out, quote = "", None
    for i, ch in enumerate(line):
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
            break
        out += ch
    return out.rstrip()


def _block_scalar(lines, i, base_indent, style):
    """Consumes an indented block under a `|` or `>` header. Returns (text, next_i)."""
    body = []
    while i < len(lines):
        line = lines[i]
        if line.strip() == "":
            body.append("")
            i += 1
            continue
        if _indent(line) <= base_indent:
            break
        body.append(line)
        i += 1
    while body and body[-1] == "":
        body.pop()
    if not body:
        return "", i
    strip = min(_indent(b) for b in body if b.strip())
    body = [b[strip:] if b.strip() else "" for b in body]
    if style.startswith(">"):
        folded, buf = [], []
        for b in body:
            if b == "":
                folded.append(" ".join(buf))
                buf = []
            else:
                buf.append(b.strip())
        if buf:
            folded.append(" ".join(buf))
        text = "\n".join(folded)
    else:
        text = "\n".join(body)
    if style.endswith("-"):
        return text, i
    return text + "\n", i


def _parse_block(lines, i, indent):
    """Parses a mapping or sequence at `indent`. Returns (value, next_i)."""
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    if i >= len(lines) or _indent(lines[i]) < indent:
        return None, i
    # The caller knows only the minimum indent a child may have. The first child
    # line carries the real one, and every sibling is aligned to it.
    indent = _indent(lines[i])
    if lines[i].lstrip().startswith("- "):
        return _parse_seq(lines, i, indent)
    return _parse_map(lines, i, indent)


def _parse_seq(lines, i, indent):
    items = []
    while i < len(lines):
        line = lines[i]
        if line.strip() == "":
            i += 1
            continue
        if _indent(line) != indent or not line.lstrip().startswith("- "):
            break
        rest = line.lstrip()[2:]
        child_indent = indent + 2
        if ":" in rest and not rest.strip().startswith(("[", "{", '"', "'")):
            # An inline first key starts a mapping whose later keys are indented to it.
            synthetic = [" " * child_indent + rest]
            j = i + 1
            while j < len(lines) and (
                lines[j].strip() == "" or _indent(lines[j]) >= child_indent
            ):
                synthetic.append(lines[j])
                j += 1
            value, _ = _parse_map(synthetic, 0, child_indent)
            items.append(value)
            i = j
        else:
            items.append(_scalar(rest))
            i += 1
    return items, i


def _parse_map(lines, i, indent):
    out = {}
    while i < len(lines):
        line = lines[i]
        if line.strip() == "":
            i += 1
            continue
        here = _indent(line)
        if here < indent or line.lstrip().startswith("- "):
            break
        if here > indent:
            i += 1
            continue
        stripped = line.strip()
        if ":" not in stripped:
            i += 1
            continue
        key, _, rest = stripped.partition(":")
        key = _scalar(key)
        rest = rest.strip()
        if rest.startswith("|") or rest.startswith(">"):
            out[key], i = _block_scalar(lines, i + 1, here, rest)
        elif rest == "":
            child, i = _parse_block(lines, i + 1, here + 1)
            out[key] = child
        else:
            out[key] = _scalar(rest)
            i += 1
    return out, i


def parse_yaml_subset(text):
    lines = [_strip_comment(l) for l in text.replace("\t", "  ").splitlines()]
    value, _ = _parse_block(lines, 0, 0)
    return value if isinstance(value, dict) else {}


# ------------------------------------------------------------------ frontmatter


def parse_frontmatter(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    return parse_yaml_subset(text[text.index("\n", 3) + 1 : end])


# ----------------------------------------------------------------- collection


def read_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def collect_skills(plugin_dir):
    skills_dir = os.path.join(plugin_dir, "skills")
    skills = []
    if not os.path.isdir(skills_dir):
        return skills
    for entry in sorted(os.listdir(skills_dir)):
        skill_md = os.path.join(skills_dir, entry, "SKILL.md")
        if not os.path.isfile(skill_md):
            continue
        front = parse_frontmatter(skill_md)
        skills.append(
            {
                "name": front.get("name") or entry,
                "description": front.get("description"),
                "path": os.path.relpath(skill_md, REPO_ROOT),
            }
        )
    return skills


def collect_agents(plugin_dir):
    agents_dir = os.path.join(plugin_dir, "agents")
    agents = []
    if not os.path.isdir(agents_dir):
        return agents
    for entry in sorted(os.listdir(agents_dir)):
        if not entry.endswith(".md"):
            continue
        path = os.path.join(agents_dir, entry)
        front = parse_frontmatter(path)
        agents.append(
            {
                "name": front.get("name") or entry[:-3],
                "path": os.path.relpath(path, REPO_ROOT),
            }
        )
    return agents


def grader_target_summary(grader):
    """Renders a grader's target as the source file states it, or null if it states none."""
    for key in ("target", "focus"):
        target = grader.get(key)
        if target is None:
            continue
        if isinstance(target, dict):
            source = target.get("source")
            path = target.get("path")
            if source and path:
                return "%s:%s" % (source, path)
            return source or path
        return str(target)
    if grader.get("tool"):
        return "tool:%s" % grader["tool"]
    if grader.get("path"):
        return "path:%s" % grader["path"]
    return None


def collect_cases(plugin_dir):
    evals_dir = os.path.join(plugin_dir, "evals")
    cases = []
    if not os.path.isdir(evals_dir):
        return cases
    for entry in sorted(os.listdir(evals_dir)):
        case_yaml = os.path.join(evals_dir, entry, "case.yaml")
        if not os.path.isfile(case_yaml):
            continue
        rel = os.path.relpath(case_yaml, REPO_ROOT)
        try:
            with open(case_yaml, encoding="utf-8") as fh:
                doc = parse_yaml_subset(fh.read())
            execution = doc.get("execution") or {}
            graders = []
            for grader in doc.get("graders") or []:
                if not isinstance(grader, dict):
                    continue
                graders.append(
                    {
                        "type": grader.get("type"),
                        "name": grader.get("name"),
                        "target": grader_target_summary(grader),
                    }
                )
            cases.append(
                {
                    "name": doc.get("name") or entry,
                    "dir": entry,
                    "description": doc.get("description"),
                    "tags": doc.get("tags") or [],
                    "runs": doc.get("runs"),
                    "model": execution.get("model"),
                    "graders": graders,
                    "graderCount": len(graders),
                    "path": rel,
                    "parse_error": None,
                }
            )
        except Exception as exc:  # a malformed case is listed, never fatal
            cases.append(
                {
                    "name": entry,
                    "dir": entry,
                    "description": None,
                    "tags": [],
                    "runs": None,
                    "model": None,
                    "graders": [],
                    "graderCount": 0,
                    "path": rel,
                    "parse_error": "%s: %s" % (type(exc).__name__, exc),
                }
            )
    return cases


def collect_runs(plugin_name, plugin_dir):
    results_dir = os.path.join(plugin_dir, "evals", "results")
    runs = []
    if not os.path.isdir(results_dir):
        return runs
    for stamp in sorted(os.listdir(results_dir)):
        path = os.path.join(results_dir, stamp, "aggregate-result.json")
        if not os.path.isfile(path):
            continue
        try:
            data = read_json(path)
        except Exception as exc:
            runs.append(
                {
                    "plugin": plugin_name,
                    "stamp": stamp,
                    "parse_error": "%s: %s" % (type(exc).__name__, exc),
                    "cases": [],
                }
            )
            continue
        suite = data.get("suite") or {}
        plugins = suite.get("plugins") or []
        report = os.path.join(results_dir, stamp, "report.html")
        runs.append(
            {
                "plugin": plugin_name,
                "stamp": stamp,
                "pluginVersion": plugins[0].get("version") if plugins else None,
                "schemaVersion": data.get("schemaVersion"),
                "claudeVersion": data.get("claudeVersion"),
                "startedAt": data.get("startedAt"),
                "durationSeconds": data.get("durationSeconds"),
                "costUsd": data.get("costUsd"),
                "partial": data.get("partial"),
                "model": suite.get("modelOverride"),
                "judgeModel": suite.get("judgeModel"),
                "threshold": suite.get("threshold"),
                "ablation": suite.get("ablation"),
                "caseFilter": suite.get("caseFilter"),
                "tagFilters": suite.get("tagFilters") or [],
                "concurrency": suite.get("concurrency"),
                "casesTotal": (data.get("aggregates") or {}).get("casesTotal"),
                "casesPassed": (data.get("aggregates") or {}).get("casesPassed"),
                "overallScore": (data.get("aggregates") or {}).get("overallScore"),
                "overallPassRate": (data.get("aggregates") or {}).get("overallPassRate"),
                "reportPath": (
                    os.path.relpath(report, os.path.join(REPO_ROOT, "dashboard"))
                    if os.path.isfile(report)
                    else None
                ),
                "cases": [run_case(case) for case in data.get("cases") or []],
                "parse_error": None,
            }
        )
    return runs


def run_case(case):
    arms = case.get("arms") or {}
    aggregates = case.get("aggregates") or {}
    attempts = []
    for arm_name in sorted(arms):
        for attempt in arms[arm_name] or []:
            attempts.append(
                {
                    "arm": arm_name,
                    "passed": attempt.get("passed"),
                    "score": attempt.get("score"),
                    "turns": attempt.get("turns"),
                    "costUsd": attempt.get("costUsd"),
                    "judgeCostUsd": attempt.get("judgeCostUsd"),
                    "durationSeconds": attempt.get("durationSeconds"),
                    "startedAt": attempt.get("startedAt"),
                    "error": attempt.get("error"),
                    "graders": [
                        {
                            "name": grader.get("name"),
                            "type": grader_type(case, grader.get("name")),
                            "passed": grader.get("passed"),
                            "score": grader.get("score"),
                            "weight": grader.get("weight"),
                            "explanation": grader.get("explanation"),
                        }
                        for grader in attempt.get("graders") or []
                    ],
                }
            )
    # The runner records `passed` per attempt and never at case level. One attempt
    # therefore has a recorded verdict; several would need a rule this file has no
    # business inventing, so the verdict stays null and `passRate` speaks instead.
    passed = attempts[0]["passed"] if len(attempts) == 1 else None
    return {
        "name": case.get("name"),
        "dir": case.get("dir"),
        "model": case.get("model"),
        "runsPerCase": case.get("runsPerCase"),
        "maxTurns": case.get("maxTurns"),
        "timeoutSeconds": case.get("timeoutSeconds"),
        "passed": passed,
        "score": aggregates.get("score"),
        "passRate": aggregates.get("passRate"),
        "attempts": attempts,
    }


def grader_type(case, name):
    for grader in case.get("graders") or []:
        if grader.get("name") == name:
            return grader.get("type")
    return None


def main():
    if not os.path.isdir(PLUGINS_DIR):
        sys.exit("no plugins directory at %s" % PLUGINS_DIR)
    plugins, runs = [], []
    for entry in sorted(os.listdir(PLUGINS_DIR)):
        plugin_dir = os.path.join(PLUGINS_DIR, entry)
        manifest_path = os.path.join(plugin_dir, ".claude-plugin", "plugin.json")
        if not os.path.isfile(manifest_path):
            continue
        manifest = read_json(manifest_path)
        name = manifest.get("name") or entry
        skills = collect_skills(plugin_dir)
        cases = collect_cases(plugin_dir)
        plugins.append(
            {
                "name": name,
                "dir": entry,
                "version": manifest.get("version"),
                "description": manifest.get("description"),
                "skills": skills,
                "agents": collect_agents(plugin_dir),
                "cases": cases,
                "skillCount": len(skills),
                "caseCount": len(cases),
            }
        )
        runs.extend(collect_runs(name, plugin_dir))

    catalog = {
        "generatedAt": datetime.datetime.now(datetime.timezone.utc)
        .replace(microsecond=0)
        .isoformat(),
        "repoRoot": REPO_ROOT,
        "plugins": plugins,
        "runs": runs,
        "counts": {
            "plugins": len(plugins),
            "skills": sum(p["skillCount"] for p in plugins),
            "agents": sum(len(p["agents"]) for p in plugins),
            "cases": sum(p["caseCount"] for p in plugins),
            "runs": len(runs),
        },
    }
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(catalog, fh, indent=2)
        fh.write("\n")
    print(json.dumps(catalog["counts"], indent=2))
    print("wrote %s" % OUT_PATH)


if __name__ == "__main__":
    main()
