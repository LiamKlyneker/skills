#!/usr/bin/env python3
"""Enumerate a Tailwind-based design system into the generated half of a catalog.

Reads a bundled TypeScript declaration file and a theme stylesheet, and writes the four
mechanical sections of `catalog-contract.md` — `## Components`, `## Tokens`,
`## Typography`, `## Icons`. It never writes `## Conventions`, never writes a `status:`
field, and never guesses: anything it cannot resolve is listed under `## Unresolved`, for
the overlay's author to answer.

Standard library only, and no argument names a skill, a workflow or a plugin — the whole
file is intended to move into a design-system package unchanged.
"""

from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import re
import sys

# A declaration merged by a bundler carries every internal type too. A component is
# recognised by its *value* declaration, since only those are renderable.
COMPONENT_DECL = re.compile(
    r"^\s*declare\s+const\s+(?P<name>[A-Z]\w*)\s*:\s*(?P<type>.+?);\s*$", re.M
)
FUNCTION_DECL = re.compile(
    r"^\s*declare\s+function\s+(?P<name>[A-Z]\w*)\s*\((?P<params>.*?)\)", re.M | re.S
)
EXPORT_LIST = re.compile(r"^\s*export\s*\{(?P<body>[^}]*)\}", re.M | re.S)
PROPS_REF = re.compile(r"\b(?P<props>\w*Props)\b")
INTERFACE_BLOCK = re.compile(
    r"^\s*(?:declare\s+)?(?:interface|type)\s+(?P<name>\w*Props)\b[^{]*\{(?P<body>.*?)^\s*\}",
    re.M | re.S,
)
PROP_LINE = re.compile(r"^\s*(?P<name>\w+)(?P<optional>\?)?\s*:\s*(?P<type>[^;]+);", re.M)
STRING_LITERAL = re.compile(r"""['"]([^'"]+)['"]""")

CSS_VAR = re.compile(r"^\s*(--[\w-]+)\s*:\s*([^;]+);", re.M)
CSS_RULE = re.compile(r"^\s*\.([\w-]+)\s*\{(.*?)\}", re.M | re.S)
CSS_DECL = re.compile(r"([\w-]+)\s*:\s*([^;]+)")

TYPOGRAPHY_PROPS = {
    "font-size",
    "line-height",
    "font-weight",
    "letter-spacing",
    "text-transform",
    "font-family",
}


def read(path: pathlib.Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        sys.exit(f"cannot read {path}: {exc}")


def exported_names(src: str) -> set[str]:
    """Names in an `export { … }` list, which is the public surface when one exists.

    A declaration file routinely declares far more than it exports, and the difference is
    the filtering the export map performs. An absent export list means every declaration
    is public, which is the other real shape.
    """
    names: set[str] = set()
    for block in EXPORT_LIST.finditer(src):
        for item in block.group("body").split(","):
            item = item.strip()
            if not item:
                continue
            if " as " in item:
                item = item.split(" as ")[-1].strip()
            names.add(item.lstrip("type ").strip())
    return names


def props_blocks(src: str) -> dict[str, str]:
    return {m.group("name"): m.group("body") for m in INTERFACE_BLOCK.finditer(src)}


def axes_from_props(body: str) -> tuple[list[tuple[str, list[str]]], list[str]]:
    """Split a props body into enumerable axes and props whose values are unbounded.

    Only a union of string literals is a closed set. `variant?: string` is the first of the
    five known static-reading failures wearing a type annotation, so it is reported as
    unresolved rather than recorded as an axis with no values.
    """
    axes: list[tuple[str, list[str]]] = []
    open_ended: list[str] = []
    for prop in PROP_LINE.finditer(body):
        name, ptype = prop.group("name"), prop.group("type").strip()
        literals = STRING_LITERAL.findall(ptype)
        stripped = STRING_LITERAL.sub("", ptype)
        # A union of literals leaves only separators behind once the literals are removed.
        if literals and not re.search(r"[A-Za-z]", stripped):
            axes.append((name, literals))
        elif re.fullmatch(r"string", ptype) and name in {
            "variant",
            "size",
            "color",
            "tone",
            "appearance",
            "kind",
            "intent",
        }:
            open_ended.append(name)
    return axes, open_ended


def collect_components(src: str, subpath: str, icons: set[str]) -> tuple[list[dict], list[str]]:
    public = exported_names(src)
    blocks = props_blocks(src)
    unresolved: list[str] = []
    found: dict[str, dict] = {}

    def record(name: str, type_text: str) -> None:
        # An icon gets its own section, and listing it here as well would double-count
        # the component inventory an existence check reads.
        if name in icons or (public and name not in public):
            return
        ref = PROPS_REF.search(type_text)
        axes: list[tuple[str, list[str]]] = []
        if ref and ref.group("props") in blocks:
            axes, open_ended = axes_from_props(blocks[ref.group("props")])
            for prop in open_ended:
                unresolved.append(
                    f"`{name}` declares `{prop}` as an unbounded `string` — the legal set is "
                    f"declared somewhere other than the signature. Ask for the exact values."
                )
        elif ref:
            unresolved.append(
                f"`{name}` refers to `{ref.group('props')}`, which is not declared in this "
                f"file — its variant axes could not be read."
            )
        found[name] = {"name": name, "reference": subpath, "axes": axes}

    for m in COMPONENT_DECL.finditer(src):
        record(m.group("name"), m.group("type"))
    for m in FUNCTION_DECL.finditer(src):
        record(m.group("name"), m.group("params"))

    return sorted(found.values(), key=lambda c: c["name"]), unresolved


def collect_tokens(css: str) -> dict[str, list[tuple[str, str]]]:
    """Group custom properties into tiers by their first name segment.

    The grouping is a proposal, not a claim: a design system's real tier names come from the
    overlay, and the caller is told to confirm them.
    """
    tiers: dict[str, list[tuple[str, str]]] = {}
    for name, value in CSS_VAR.findall(css):
        segments = name.lstrip("-").split("-")
        tier = segments[0] if len(segments) > 1 else "ungrouped"
        tiers.setdefault(tier, []).append((name, value.strip()))
    for entries in tiers.values():
        entries.sort()
    return dict(sorted(tiers.items()))


def collect_typography(css: str) -> list[tuple[str, list[tuple[str, str]]]]:
    out: list[tuple[str, list[tuple[str, str]]]] = []
    for cls, body in CSS_RULE.findall(css):
        decls = [
            (p.strip(), v.strip())
            for p, v in CSS_DECL.findall(body)
            if p.strip() in TYPOGRAPHY_PROPS
        ]
        if decls:
            out.append((cls, decls))
    out.sort()
    return out


def collect_icons(src: str, pattern: str) -> list[str]:
    rx = re.compile(pattern)
    public = exported_names(src)
    names = {n for n in public if rx.search(n)} if public else set()
    if not names:
        names = {
            m.group("name")
            for m in COMPONENT_DECL.finditer(src)
            if rx.search(m.group("name"))
        }
    return sorted(names)


def table(rows: list[list[str]], headers: list[str]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for row in rows:
        lines.append("| " + " | ".join(cell.replace("|", "\\|") for cell in row) + " |")
    return "\n".join(lines)


def render(args, components, unresolved, tiers, typography, icons) -> str:
    today = datetime.date.today().isoformat()
    out = [
        f"# {args.name} catalog — generated half "
        f"(fingerprint: {args.version} · generated: {today})",
        "",
        f"Enumerated mechanically from `{args.types}`"
        + (f" and `{args.theme}`" if args.theme else "")
        + f" at version `{args.version}`. The fingerprint is that version: this half is "
        "exactly as current as the installed package.",
        "",
        "**Regenerate this file; never hand-edit it.** Every judgement — `status:` fields, "
        "successors, conventions, idiom mappings — lives in the overlay, which is the half "
        "a human owns and this script never touches.",
        "",
        "## Components",
        "",
    ]

    if components:
        rows = []
        for c in components:
            axes = (
                " · ".join(f"`{a}`: {', '.join('`' + v + '`' for v in vs)}" for a, vs in c["axes"])
                if c["axes"]
                else "—"
            )
            rows.append([c["name"], f"`{c['reference']}`", axes])
        out.append(table(rows, ["Component", "Reference", "Variant axes / values"]))
    else:
        out.append("None — no component value declarations found in the declaration file.")

    out += ["", "## Tokens", ""]
    if tiers:
        out.append(
            "Tiers are grouped by the first segment of each custom property's name. "
            "**The grouping is mechanical and the tier names are not the project's** — "
            "confirm both in the overlay's `## Conventions`."
        )
        for tier, entries in tiers.items():
            out += [
                "",
                f"### {tier}",
                "",
                f"{len(entries)} " + ("entry" if len(entries) == 1 else "entries")
                + ", enumerated.",
                "",
                table([[f"`{n}`", f"`{v}`"] for n, v in entries], ["Custom property", "Value"]),
            ]
    else:
        out.append("None — no CSS custom properties were read (no theme stylesheet given).")

    out += ["", "## Typography", ""]
    if typography:
        rows = [
            [f"`.{cls}`", " · ".join(f"{p}: {v}" for p, v in decls)]
            for cls, decls in typography
        ]
        out.append(table(rows, ["Utility", "Sets"]))
    else:
        out.append(
            "None — no class rule in the stylesheet sets a typographic property. "
            "A design system whose text utilities are emitted by a plugin call rather than "
            "declared as rules reads exactly like this; confirm which it is."
        )

    out += ["", "## Icons", ""]
    if icons:
        out += [
            f"### {args.name} icon exports",
            "",
            f"Referenced as a component from `{args.types_subpath}`. "
            f"{len(icons)} exports match `{args.icon_pattern}`, enumerated.",
            "",
            ", ".join(f"`{n}`" for n in icons),
            "",
            "**Whether this is the project's only icon source is not readable here.** "
            "Icon sources are plural by default; the overlay names the rest.",
        ]
    else:
        out.append(
            f"None — no export matches `{args.icon_pattern}`. That is a real answer only if "
            "this package ships no icons; otherwise the pattern is wrong or the icons live "
            "elsewhere."
        )

    out += ["", "## Unresolved", ""]
    if unresolved:
        out.append(
            "Read but not settled. Each one is a question for the overlay's author; none of "
            "them is a gap in the design system."
        )
        out.append("")
        out += [f"- {u}" for u in sorted(set(unresolved))]
    else:
        out.append("None — every declaration read resolved to an enumerated entry.")

    return "\n".join(out) + "\n"


RANGE = re.compile(r"[\^~*x><|\s]|\.\.")


def resolve_version(args) -> str:
    """The fingerprint is the version actually installed, so a range is refused.

    A dependency range resolves to a different version on two machines and on two days,
    which would make a stamp that matches prove nothing. Point --manifest at the installed
    package's own package.json, whose `version` is exact.
    """
    candidate = args.version
    if candidate is None and args.manifest:
        data = json.loads(read(pathlib.Path(args.manifest)))
        if "version" in data and (not args.package or data.get("name") == args.package):
            candidate = data["version"]
        else:
            for field in ("dependencies", "devDependencies", "peerDependencies"):
                if args.package and args.package in data.get(field, {}):
                    candidate = data[field][args.package]
                    break
    if candidate is None:
        sys.exit("no version: pass --version, or --manifest with --package")
    if RANGE.search(candidate):
        sys.exit(
            f"'{candidate}' is a range, not an installed version. A range resolves "
            "differently on two machines, so a fingerprint built from one proves nothing. "
            "Point --manifest at the installed package's own package.json, or pass the "
            "exact version as --version."
        )
    return candidate


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--types", required=True, help="bundled .d.ts to enumerate")
    ap.add_argument("--theme", help="stylesheet carrying the custom properties and utilities")
    ap.add_argument("--name", required=True, help="the design system's name, for the title line")
    ap.add_argument("--version", help="the installed version; becomes the fingerprint")
    ap.add_argument("--manifest", help="package.json to read the version from")
    ap.add_argument("--package", help="dependency name to look up in --manifest")
    ap.add_argument(
        "--types-subpath",
        default="the package root",
        help="how a consumer imports what --types declares",
    )
    ap.add_argument("--icon-pattern", default=r"Icon$", help="regex marking an icon export")
    ap.add_argument("--out", required=True, help="file to write")
    args = ap.parse_args()

    args.version = resolve_version(args)
    src = read(pathlib.Path(args.types))
    css = read(pathlib.Path(args.theme)) if args.theme else ""

    icons = collect_icons(src, args.icon_pattern)
    components, unresolved = collect_components(src, args.types_subpath, set(icons))
    tiers = collect_tokens(css)
    typography = collect_typography(css)

    pathlib.Path(args.out).write_text(render(args, components, unresolved, tiers, typography, icons))

    print(f"wrote {args.out}")
    print(
        f"  {len(components)} components · {len(tiers)} token tiers "
        f"({sum(len(v) for v in tiers.values())} entries) · "
        f"{len(typography)} typography utilities · {len(icons)} icons · "
        f"{len(set(unresolved))} unresolved"
    )


if __name__ == "__main__":
    main()
