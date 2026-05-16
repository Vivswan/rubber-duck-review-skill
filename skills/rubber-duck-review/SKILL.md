---
name: rubber-duck-review
description: Cross-model code review using a second agent, tool, or read-only CLI fallback. This skill should be used when someone asks to rubber duck a change, get a second opinion, or run an independent review focused on correctness, future-proofing, and design quality.
license: MIT
metadata:
  author: Vivswan
  version: "1.0.0"
---

# Rubber Duck Review

Get a second opinion on code changes from a different model while you keep ownership of the task.

## When to Apply

Use this skill when someone asks for:

- `/rubber-duck-review`
- "rubber duck my changes"
- "get a second opinion on this"
- "review this with another model"

## Workflow

### 1. Pick the reviewer

- Prefer a dedicated review tool when one is available.
- Use a reviewer that is different from the current model when possible.
- If no dedicated tool exists, fall back to a read-only CLI invocation and try the first one that exists:
  - If you are currently using Claude:
    1. `codex exec --sandbox read-only "[prompt]"`
    2. `copilot -p --deny-tool='write' --deny-tool='shell' "[prompt]"`
  - If you are currently using Codex or GitHub Copilot:
    1. `claude -p --permission-mode plan "[prompt]"`
    2. `copilot -p --deny-tool='write' --deny-tool='shell' "[prompt]"`
- Never let the reviewer write files, edit code, or run unrestricted shell commands.

### 2. Craft the prompt

- Ask for a review of the relevant changes and surrounding context only.
- Always include: `This is a review-only task. Do not edit, write, or modify any files. Only read and report findings.`
- Do not paste diffs unless the environment forces you to. Prefer letting the reviewer inspect the codebase directly so it can follow imports and cross-file behavior.
- Ask the reviewer to look for:
  - Correctness issues
  - Future-proofing risks
  - Naming or design choices that will become awkward as the codebase grows
  - Hardcoded assumptions that may become misleading later
- If the user has already declined or reverted something in this thread, add a short `Already decided / out of scope` section so the reviewer does not keep re-raising it.

For a reusable prompt template, see `references/reviewer-prompt.md`.

### 3. Run the review in parallel

- Launch the review in the background when your environment supports it.
- Keep working while the review runs instead of blocking on it.
- Wait for the completed review only when you need the findings to decide the next step.

### 4. Apply findings thoughtfully

- Treat valid "non-blocking" feedback as real work, especially when it highlights design traps or future maintenance issues.
- Do not blindly accept every finding. If you disagree, explain why.
- If a finding conflicts with an explicit user decision, follow the user and record that the issue was intentionally skipped.

### 5. Re-review after fixes

- After addressing valid findings, run the rubber-duck review again.
- Repeat until there are no remaining issues worth acting on.
