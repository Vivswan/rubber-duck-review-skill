#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def require_file(path: Path) -> None:
    if not path.is_file():
        fail(f"Missing required file: {path.relative_to(ROOT)}")


def parse_frontmatter(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(f"{path.relative_to(ROOT)}: missing YAML frontmatter start")
    try:
        end = text.index("\n---\n", 4)
    except ValueError as exc:
        fail(f"{path.relative_to(ROOT)}: missing YAML frontmatter end")
        raise AssertionError("unreachable") from exc

    block = text[4:end].splitlines()
    data: dict[str, object] = {}
    current: str | None = None

    for raw in block:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.startswith("  ") and current:
            stripped = raw.strip()
            if ":" not in stripped:
                continue
            key, value = stripped.split(":", 1)
            nested = data.setdefault(current, {})
            if not isinstance(nested, dict):
                fail(f"{path.relative_to(ROOT)}: invalid nested frontmatter under '{current}'")
            nested[key.strip()] = value.strip().strip("\"'")
            continue
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value:
            data[key] = value.strip("\"'")
            current = None
        else:
            data[key] = {}
            current = key

    return data


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{path.relative_to(ROOT)}: invalid JSON ({exc.msg})")
        raise AssertionError("unreachable") from exc


def validate_marketplace() -> None:
    marketplace_path = ROOT / ".claude-plugin" / "marketplace.json"
    marketplace = load_json(marketplace_path)
    if not isinstance(marketplace, dict):
        fail(".claude-plugin/marketplace.json: root must be an object")
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list):
        fail(".claude-plugin/marketplace.json: missing plugins array")
    for plugin in plugins:
        if not isinstance(plugin, dict):
            fail(".claude-plugin/marketplace.json: each plugin entry must be an object")
        skills = plugin.get("skills")
        if not isinstance(skills, list):
            fail(".claude-plugin/marketplace.json: plugin missing skills list")
        for skill_path in skills:
            if not isinstance(skill_path, str):
                fail(".claude-plugin/marketplace.json: skill paths must be strings")
            full_path = ROOT / skill_path
            if not full_path.exists():
                fail(f".claude-plugin/marketplace.json: missing referenced path {skill_path}")


def validate_skill_dirs() -> None:
    skills_dir = ROOT / "skills"
    if not skills_dir.is_dir():
        fail("skills/: missing skills directory")

    skill_dirs = sorted(path for path in skills_dir.iterdir() if path.is_dir())
    if not skill_dirs:
        fail("skills/: no public skills found")

    for skill_dir in skill_dirs:
        skill_md = skill_dir / "SKILL.md"
        readme = skill_dir / "README.md"
        plugin_json = skill_dir / ".codex-plugin" / "plugin.json"

        require_file(skill_md)
        require_file(readme)
        require_file(plugin_json)

        frontmatter = parse_frontmatter(skill_md)
        name = frontmatter.get("name")
        description = frontmatter.get("description")
        if not isinstance(name, str) or not name:
            fail(f"{skill_md.relative_to(ROOT)}: missing frontmatter name")
        if not isinstance(description, str) or not description:
            fail(f"{skill_md.relative_to(ROOT)}: missing frontmatter description")
        if name != skill_dir.name:
            fail(
                f"{skill_md.relative_to(ROOT)}: frontmatter name '{name}' does not match folder '{skill_dir.name}'"
            )

        plugin_data = load_json(plugin_json)
        if not isinstance(plugin_data, dict):
            fail(f"{plugin_json.relative_to(ROOT)}: root must be an object")
        if plugin_data.get("name") != skill_dir.name:
            fail(f"{plugin_json.relative_to(ROOT)}: name does not match folder '{skill_dir.name}'")

        mcp_json = skill_dir / ".mcp.json"
        if mcp_json.exists():
            load_json(mcp_json)


def validate_template() -> None:
    template_paths = [
        ROOT / "template" / "SKILL.md",
        ROOT / "template" / "README.md",
        ROOT / "template" / ".codex-plugin" / "plugin.json",
        ROOT / "template" / ".mcp.json.example",
    ]
    for path in template_paths:
        require_file(path)

    template_frontmatter = parse_frontmatter(ROOT / "template" / "SKILL.md")
    metadata = template_frontmatter.get("metadata")
    if not isinstance(metadata, dict) or str(metadata.get("internal", "")).lower() != "true":
        fail("template/SKILL.md: metadata.internal must be true")

    load_json(ROOT / "template" / ".codex-plugin" / "plugin.json")
    load_json(ROOT / "template" / ".mcp.json.example")


def main() -> None:
    for path in [
        ROOT / "README.md",
        ROOT / "AGENTS.md",
        ROOT / ".claude-plugin" / "marketplace.json",
    ]:
        require_file(path)

    validate_marketplace()
    validate_skill_dirs()
    validate_template()
    print("Skill validation passed.")


if __name__ == "__main__":
    main()
