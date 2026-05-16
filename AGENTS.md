# AGENTS.md

This file provides guidance to AI coding agents working in this repository.

## Repository Overview

A collection of installable skills for coding agents. Skills are packaged instructions and resources that extend agent capabilities.

## Repository Layout

```text
skills/
  <skill-name>/
    SKILL.md
    README.md
    .codex-plugin/plugin.json
    .mcp.json
    references/
    scripts/
template/
  SKILL.md
  README.md
  .codex-plugin/plugin.json
  .mcp.json.example
```

## Creating a New Skill

### Naming Conventions

- Keep every public skill in `skills/<skill-name>/`.
- Use kebab-case for directory names and skill names.
- `SKILL.md` must stay uppercase and use valid YAML frontmatter.

### Skill Structure

- Keep `SKILL.md` focused on activation logic and workflow.
- Put supporting detail in `references/`.
- Add `scripts/` only when the skill needs executable helpers.
- Keep each skill folder plugin-ready by maintaining `.codex-plugin/plugin.json`.
- If a skill grows MCP, hooks, or app integrations later, add those files inside the same skill folder instead of changing the repo layout.
- If a skill uses MCP, `SKILL.md` must still explain how to complete the task when the MCP server is unavailable.
- Treat `npx skills add ...` and the plain skill content as the compatibility baseline for Claude Code, Codex, and GitHub Copilot.

### Publishing Hygiene

- Update the root `README.md` whenever you add, rename, or remove a skill.
- Keep the files in `template/` useful as the starter for the next skill.
- Run `uv run python scripts/validate-skills.py` before publishing or opening a PR.

## Publishing Notes

- Collection installs should use `npx skills add Vivswan/skills`.
- Single-skill installs can target the repo path or use `--skill <name>`.
- Preserve the Git author email as `58091053+Vivswan@users.noreply.github.com` for commits made from this repo.
- Follow [`docs/authoring.md`](./docs/authoring.md) for the shared skill-core plus plugin-layer model.
