#!/usr/bin/env python3
"""Validate ajiaskill SKILL.md files with the portable frontmatter contract."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ALLOWED_FIELDS = {"name", "description", "license"}
REQUIRED_FIELDS = {"name", "description"}
MAX_NAME = 64
MAX_DESCRIPTION = 1024
RECOMMENDED_DESCRIPTION = 500
MAX_LINES = 500


def parse_frontmatter(text: str) -> tuple[dict[str, str], str, list[str]]:
    errors: list[str] = []
    if not text.startswith("---\n"):
        return {}, text, ["file must start with a YAML frontmatter block"]
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text, ["frontmatter block is not closed with ---"]
    raw = text[4:end]
    body = text[end + 5:]
    fields: dict[str, str] = {}
    for lineno, line in enumerate(raw.splitlines(), start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            errors.append(f"frontmatter line {lineno}: expected key: value")
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value in {">", "|"}:
            errors.append(
                f"frontmatter line {lineno}: use a single-line value, not a block scalar"
            )
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        if key in fields:
            errors.append(f"frontmatter line {lineno}: duplicate field {key!r}")
        fields[key] = value
    return fields, body, errors


def validate_skill(path: Path) -> list[str]:
    rel = path.relative_to(ROOT)
    errors: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"{rel}: cannot read: {exc}"]

    fields, body, parse_errors = parse_frontmatter(text)
    errors.extend(f"{rel}: {e}" for e in parse_errors)

    extra = set(fields) - ALLOWED_FIELDS
    if extra:
        errors.append(f"{rel}: unsupported frontmatter fields: {', '.join(sorted(extra))}")
    for required in REQUIRED_FIELDS:
        if not fields.get(required):
            errors.append(f"{rel}: missing or empty {required!r}")

    name = fields.get("name", "")
    description = fields.get("description", "")
    if name and not NAME_RE.fullmatch(name):
        errors.append(f"{rel}: name must match {NAME_RE.pattern}")
    if len(name) > MAX_NAME:
        errors.append(f"{rel}: name is {len(name)} chars; max {MAX_NAME}")
    if name and name != path.parent.name:
        errors.append(f"{rel}: name {name!r} must match directory {path.parent.name!r}")
    if description and len(description) > MAX_DESCRIPTION:
        errors.append(
            f"{rel}: description is {len(description)} chars; max {MAX_DESCRIPTION}"
        )
    if description and len(description) > RECOMMENDED_DESCRIPTION:
        print(
            f"warn {rel}: description is {len(description)} chars; "
            f"keep it under {RECOMMENDED_DESCRIPTION} if possible"
        )
    if not body.strip():
        errors.append(f"{rel}: body is empty")
    line_count = len(text.splitlines())
    if line_count > MAX_LINES:
        errors.append(f"{rel}: {line_count} lines; max {MAX_LINES}")
    return errors


def main() -> int:
    if not SKILLS_DIR.is_dir():
        print(f"error: {SKILLS_DIR} does not exist", file=sys.stderr)
        return 1

    paths = sorted(SKILLS_DIR.glob("*/SKILL.md"))
    if not paths:
        print("error: no skills/*/SKILL.md files found", file=sys.stderr)
        return 1

    errors: list[str] = []
    seen: dict[str, Path] = {}
    for path in paths:
        errors.extend(validate_skill(path))
        try:
            fields, _, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
            name = fields.get("name", "")
        except OSError:
            name = ""
        if name:
            if name in seen:
                errors.append(
                    f"{path.relative_to(ROOT)}: duplicate name {name!r} "
                    f"(also in {seen[name].relative_to(ROOT)})"
                )
            else:
                seen[name] = path

    if errors:
        for error in errors:
            print(f"error {error}")
        print(f"\n{len(errors)} error(s) in {len(paths)} skill(s)")
        return 1

    print(f"ok {len(paths)} skill(s): {', '.join(sorted(seen))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
