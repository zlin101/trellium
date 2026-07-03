#!/usr/bin/env python3
"""Adopt Agent Native Init assets into a target project."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path
import shutil


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / "skills"
TEMPLATES_ROOT = SKILLS_ROOT / "agent-native-init-zh" / "assets" / "templates"

AGENTS_MARKER_START = "<!-- agent-native-init:start -->"
AGENTS_MARKER_END = "<!-- agent-native-init:end -->"


def fail(message: str) -> int:
    print(f"error: {message}", file=sys.stderr)
    return 1


def print_action(dry_run: bool, message: str) -> None:
    prefix = "would " if dry_run else ""
    print(f"{prefix}{message}")


def copy_file(source: Path, destination: Path, force: bool, dry_run: bool) -> str:
    if destination.exists() and not force:
        return "skipped"

    action = "replace" if destination.exists() else "create"
    print_action(dry_run, f"{action} {destination}")
    if not dry_run:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    return action


def write_text_file(destination: Path, content: str, force: bool, dry_run: bool) -> str:
    if destination.exists() and not force:
        return "skipped"

    action = "replace" if destination.exists() else "create"
    print_action(dry_run, f"{action} {destination}")
    if not dry_run:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
    return action


def append_agent_entry(target: Path, dry_run: bool) -> str:
    agents_path = target / "AGENTS.md"
    if not agents_path.exists():
        return copy_file(TEMPLATES_ROOT / "AGENTS.md", agents_path, force=False, dry_run=dry_run)

    current = agents_path.read_text(encoding="utf-8")
    if AGENTS_MARKER_START in current or "vault/index.md" in current:
        print_action(dry_run, f"keep existing Agent Native Init entry in {agents_path}")
        return "skipped"

    section = f"""

{AGENTS_MARKER_START}
## Agent Native Init

For non-trivial work, read these files before editing:

1. `vault/index.md`
2. `vault/runtime.md`
3. `vault/governance.md`

Use `vault/project.md` on first entry, `vault/handoff.md` when resuming interrupted work, and `vault/tasks/` for tracked or governed tasks.
{AGENTS_MARKER_END}
"""
    print_action(dry_run, f"append Agent Native Init entry to {agents_path}")
    if not dry_run:
        agents_path.write_text(current.rstrip() + section + "\n", encoding="utf-8")
    return "updated"


def project_summary(target: Path) -> str:
    readme = target / "README.md"
    if readme.exists():
        for line in readme.read_text(encoding="utf-8", errors="ignore").splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                return stripped
    return f"{target.name} project."


def render_project(target: Path) -> str:
    return f"""# Project Context

## Summary

{project_summary(target)}

## Goals

- Keep project-specific goals here.

## Current Phase

Existing project adoption via Agent Native Init.

## In Scope

- Existing project behavior.
- Agent collaboration layer.

## Out of Scope

- Business source, dependencies, CI, deployment, secrets, and data models unless explicitly approved.

## Technical Direction

- Follow the existing project structure and tooling.

## Boundaries

Future Agents should preserve existing project behavior and request approval before high-impact changes.
"""


def render_runtime(target: Path) -> str:
    today = date.today().isoformat()
    return f"""# Runtime Context

## Current Phase

Agent Native Init adoption recorded on {today}.

## Active Task

Objective: Maintain the project-specific Agent collaboration layer.

Acceptance: `AGENTS.md`, `vault/`, and `skills/agent-task/SKILL.md` exist and route future Agents to project memory.

Required Check: `python3 scripts/agent-init.py adopt {target} --dry-run` from the Agent Native Init repository, when available.

## Current Progress

- Agent collaboration layer has been initialized or refreshed.

## Constraints

- Keep this file short.
- Move long execution history to `vault/tasks/*`.
- Do not save secrets.

## Recent Changes

- Added Agent Native Init project memory files.

## Known Risks

- Replace template text with project facts as the project evolves.

## Required Checks

```bash
find vault -maxdepth 2 -type f | sort
```

## Next Steps

- Update `vault/project.md` with durable project facts.
- Update `vault/governance.md` only when project-specific governance differs from the default.
"""


def adopt_project(args: argparse.Namespace) -> int:
    target = Path(args.target).expanduser().resolve()
    if not target.exists():
        if args.create:
            print_action(args.dry_run, f"create directory {target}")
            if not args.dry_run:
                target.mkdir(parents=True)
        else:
            return fail(f"target does not exist: {target}")
    if target.exists() and not target.is_dir():
        return fail(f"target is not a directory: {target}")

    if not TEMPLATES_ROOT.exists():
        return fail(f"template directory does not exist: {TEMPLATES_ROOT}")

    changed: list[str] = []
    skipped: list[str] = []

    agent_result = append_agent_entry(target, args.dry_run)
    (changed if agent_result in {"create", "updated"} else skipped).append("AGENTS.md")

    template_files = [
        "vault/index.md",
        "vault/governance.md",
        "vault/decisions.md",
        "vault/handoff.md",
        "vault/collaboration.md",
        "vault/tasks/README.md",
        "skills/agent-task/SKILL.md",
    ]
    for relative in template_files:
        result = copy_file(
            TEMPLATES_ROOT / relative,
            target / relative,
            force=args.force,
            dry_run=args.dry_run,
        )
        (changed if result != "skipped" else skipped).append(relative)

    rendered_files = {
        "vault/project.md": render_project(target),
        "vault/runtime.md": render_runtime(target),
    }
    for relative, content in rendered_files.items():
        result = write_text_file(target / relative, content, force=args.force, dry_run=args.dry_run)
        (changed if result != "skipped" else skipped).append(relative)

    print()
    print(f"adoption target: {target}")
    print(f"changed: {len(changed)}")
    for item in changed:
        print(f"  - {item}")
    if skipped:
        print(f"skipped existing files: {len(skipped)}")
        for item in skipped:
            print(f"  - {item}")
    print("next: ask your Agent to read AGENTS.md, vault/index.md, vault/runtime.md, and vault/governance.md")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Adopt Agent Native Init into a target project.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    adopt = subparsers.add_parser("adopt", help="add Agent collaboration files to a project")
    adopt.add_argument("target", nargs="?", default=".", help="target project directory")
    adopt.add_argument("--create", action="store_true", help="create target directory if missing")
    adopt.add_argument("--force", action="store_true", help="replace existing generated files")
    adopt.add_argument("--dry-run", action="store_true", help="print actions without writing")
    adopt.set_defaults(func=adopt_project)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
