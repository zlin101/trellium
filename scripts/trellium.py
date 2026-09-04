#!/usr/bin/env python3
"""Adopt Trellium assets into a target project and upgrade them in place."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import secrets
import shutil
import stat
import subprocess
import sys
import tarfile
import urllib.error
import urllib.request
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Iterator


# The script runs from two layouts:
# - repository checkout: scripts/trellium.py, templates under
#   skills/trellium-zh/assets/templates, protocol under init/
# - installed Skill package: assets/trellium.py, templates under
#   assets/templates, protocol under references/protocol-source/init
# Each Skill package uses its own locale templates.
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
SKILL_LAYOUT = (SCRIPT_DIRECTORY / "templates" / "vault" / "index.md").is_file()
if SKILL_LAYOUT:
    TEMPLATES_ROOT = SCRIPT_DIRECTORY / "templates"
    PROTOCOL_INIT_DIRECTORY = SCRIPT_DIRECTORY.parent / "references" / "protocol-source" / "init"
else:
    REPO_ROOT = SCRIPT_DIRECTORY.parent
    TEMPLATES_ROOT = REPO_ROOT / "skills" / "trellium-zh" / "assets" / "templates"
    PROTOCOL_INIT_DIRECTORY = REPO_ROOT / "init"

TEMPLATE_FILES = (
    "vault/index.md",
    "vault/governance.md",
    "vault/decisions.md",
    "vault/handoff.md",
    "vault/parked.md",
    "vault/collaboration.md",
    "vault/tasks/README.md",
    "skills/agent-task/SKILL.md",
)
RENDERED_FILES = ("vault/project.md", "vault/runtime.md")

# Upgrade scope. "data" files are project memory: the upgrader never writes
# them. "merge" and "template" files are protocol carriers: they may be
# refreshed while local modifications are preserved. "marker" scopes the
# managed region inside AGENTS.md. Keep this in sync with TEMPLATE_FILES,
# RENDERED_FILES and the AGENTS.md entry.
FILE_ROLES = {
    "AGENTS.md": "marker",
    "vault/index.md": "merge",
    "vault/governance.md": "merge",
    "vault/collaboration.md": "data",
    "vault/decisions.md": "data",
    "vault/handoff.md": "data",
    "vault/parked.md": "data",
    "vault/project.md": "data",
    "vault/runtime.md": "data",
    "vault/tasks/README.md": "template",
    "skills/agent-task/SKILL.md": "template",
}
WRITABLE_ROLES = frozenset({"marker", "merge", "template"})

STAMP_RELATIVE = "vault/.agent-init.json"
PROPOSAL_DIRECTORY = "vault/.upgrade"
BACKUP_DIRECTORY = ".agent-init-backup"
VERSION_FILE = PROTOCOL_INIT_DIRECTORY / "VERSION"
MIGRATIONS_FILE = PROTOCOL_INIT_DIRECTORY / "MIGRATIONS.md"

# --fetch pulls the latest tagged release from GitHub and re-executes the
# fetched updater against the fetched tree, so protocol-content updates do
# not require reinstalling the Skill package.
FETCH_REPOSITORY = "zlin101/trellium"
FETCH_TAGS_URL = f"https://api.github.com/repos/{FETCH_REPOSITORY}/tags"
FETCH_TARBALL_TEMPLATE = f"https://codeload.github.com/{FETCH_REPOSITORY}/tar.gz/refs/tags/{{tag}}"
FETCH_CACHE_ROOT = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "trellium"
FETCH_MARKER_NAME = ".trellium-fetched"
FETCH_TIMEOUT_SECONDS = 30

EXIT_ACTIONABLE = 2
EXIT_CONFLICT = 3

ANCHORED_WRITES_SUPPORTED = (
    hasattr(os, "O_DIRECTORY")
    and hasattr(os, "O_NOFOLLOW")
    and hasattr(os, "fchmod")
    and os.open in os.supports_dir_fd
    and os.mkdir in os.supports_dir_fd
    and os.stat in os.supports_dir_fd
    and os.stat in os.supports_follow_symlinks
    and os.unlink in os.supports_dir_fd
    and os.rename in os.supports_dir_fd
)
DIRECTORY_OPEN_FLAGS = (
    os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
)
FILE_CREATE_FLAGS = (
    os.O_WRONLY
    | os.O_CREAT
    | os.O_EXCL
    | getattr(os, "O_NOFOLLOW", 0)
    | getattr(os, "O_BINARY", 0)
)
FILE_READ_FLAGS = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0)

AGENTS_MARKER_START = "<!-- agent-native-init:start -->"
AGENTS_MARKER_END = "<!-- agent-native-init:end -->"


class AdoptionError(Exception):
    """Raised when an adoption plan cannot be applied safely."""


def fail(message: str) -> int:
    print(f"error: {message}", file=sys.stderr)
    return 1


def print_action(dry_run: bool, message: str) -> None:
    prefix = "would " if dry_run else ""
    print(f"{prefix}{message}")


def is_within(path: Path, directory: Path) -> bool:
    try:
        path.relative_to(directory)
    except ValueError:
        return False
    return True


def validate_output_metadata(metadata: os.stat_result, path: Path) -> None:
    if stat.S_ISLNK(metadata.st_mode):
        raise AdoptionError(f"refusing to write through symbolic link: {path}")
    if not stat.S_ISREG(metadata.st_mode):
        raise AdoptionError(f"output path is not a regular file: {path}")
    if metadata.st_nlink > 1:
        raise AdoptionError(f"refusing to replace file with multiple hard links: {path}")


def validate_output_paths(target: Path, destinations: list[Path]) -> None:
    """Reject output paths that could escape the resolved target directory."""
    for destination in destinations:
        if not is_within(destination, target) or destination == target:
            raise AdoptionError(f"output path is outside the adoption target: {destination}")

        relative = destination.relative_to(target)
        current = target
        for index, part in enumerate(relative.parts):
            current = current / part
            try:
                metadata = current.lstat()
            except FileNotFoundError:
                continue

            if stat.S_ISLNK(metadata.st_mode):
                raise AdoptionError(f"refusing to write through symbolic link: {current}")

            is_destination = index == len(relative.parts) - 1
            if is_destination:
                validate_output_metadata(metadata, current)
            elif not stat.S_ISDIR(metadata.st_mode):
                raise AdoptionError(f"output parent is not a directory: {current}")

        resolved = destination.resolve(strict=False)
        if not is_within(resolved, target):
            raise AdoptionError(f"output path resolves outside the adoption target: {destination}")


def validate_template_sources(relative_files: tuple[str, ...]) -> None:
    for relative in relative_files:
        source = TEMPLATES_ROOT / relative
        if not source.is_file():
            raise AdoptionError(f"template file does not exist: {source}")


def validate_relative_output(relative: Path) -> None:
    if (
        relative.is_absolute()
        or not relative.parts
        or any(part in {"", ".", ".."} for part in relative.parts)
    ):
        raise AdoptionError(f"invalid relative output path: {relative}")


def open_child_directory(parent_descriptor: int, name: str, create: bool) -> int:
    try:
        return os.open(name, DIRECTORY_OPEN_FLAGS, dir_fd=parent_descriptor)
    except FileNotFoundError:
        if not create:
            raise
        try:
            os.mkdir(name, 0o777, dir_fd=parent_descriptor)
        except FileExistsError:
            pass
        return os.open(name, DIRECTORY_OPEN_FLAGS, dir_fd=parent_descriptor)


def open_target_directory(target: Path, create: bool) -> int:
    """Open an absolute target from its filesystem root without following links."""
    if not target.is_absolute():
        raise AdoptionError(f"adoption target is not absolute: {target}")

    anchor = Path(target.anchor)
    if target == anchor:
        raise AdoptionError(f"refusing to adopt into filesystem root: {target}")

    descriptor = os.open(anchor, DIRECTORY_OPEN_FLAGS)
    try:
        for part in target.relative_to(anchor).parts:
            child_descriptor = open_child_directory(descriptor, part, create=create)
            os.close(descriptor)
            descriptor = child_descriptor
        return descriptor
    except Exception:
        os.close(descriptor)
        raise


@contextmanager
def open_parent_directory(
    target_descriptor: int,
    relative: Path,
    create: bool,
) -> Iterator[tuple[int, str]]:
    """Open an output parent one component at a time without following links."""
    validate_relative_output(relative)
    descriptor = os.dup(target_descriptor)
    try:
        for part in relative.parts[:-1]:
            child_descriptor = open_child_directory(descriptor, part, create=create)
            os.close(descriptor)
            descriptor = child_descriptor
        yield descriptor, relative.parts[-1]
    finally:
        os.close(descriptor)


def output_metadata_at(parent_descriptor: int, name: str) -> os.stat_result | None:
    try:
        return os.stat(name, dir_fd=parent_descriptor, follow_symlinks=False)
    except FileNotFoundError:
        return None


def staging_file_at(parent_descriptor: int, destination_name: str) -> tuple[int, str]:
    for _ in range(100):
        staging_name = f".{destination_name}.{secrets.token_hex(8)}.tmp"
        try:
            descriptor = os.open(
                staging_name,
                FILE_CREATE_FLAGS,
                0o666,
                dir_fd=parent_descriptor,
            )
        except FileExistsError:
            continue
        return descriptor, staging_name
    raise AdoptionError(f"could not allocate a staging file for: {destination_name}")


def unlink_at_if_present(parent_descriptor: int, name: str) -> None:
    try:
        os.unlink(name, dir_fd=parent_descriptor)
    except FileNotFoundError:
        pass


def atomic_copy_file_at(
    source: Path,
    parent_descriptor: int,
    destination_name: str,
) -> None:
    descriptor, staging_name = staging_file_at(parent_descriptor, destination_name)
    staging_pending = True
    try:
        source_mode = stat.S_IMODE(source.stat().st_mode)
        with source.open("rb") as source_handle, os.fdopen(descriptor, "wb") as destination_handle:
            descriptor = -1
            os.fchmod(destination_handle.fileno(), source_mode)
            shutil.copyfileobj(source_handle, destination_handle)
            destination_handle.flush()
            os.fsync(destination_handle.fileno())
        os.replace(
            staging_name,
            destination_name,
            src_dir_fd=parent_descriptor,
            dst_dir_fd=parent_descriptor,
        )
        staging_pending = False
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if staging_pending:
            unlink_at_if_present(parent_descriptor, staging_name)


def atomic_write_text_at(
    parent_descriptor: int,
    destination_name: str,
    content: str,
    mode: int | None,
) -> None:
    descriptor, staging_name = staging_file_at(parent_descriptor, destination_name)
    staging_pending = True
    try:
        if mode is not None:
            os.fchmod(descriptor, mode)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            descriptor = -1
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(
            staging_name,
            destination_name,
            src_dir_fd=parent_descriptor,
            dst_dir_fd=parent_descriptor,
        )
        staging_pending = False
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if staging_pending:
            unlink_at_if_present(parent_descriptor, staging_name)


def read_text_at(parent_descriptor: int, name: str, display_path: Path) -> str:
    descriptor = os.open(name, FILE_READ_FLAGS, dir_fd=parent_descriptor)
    try:
        validate_output_metadata(os.fstat(descriptor), display_path)
        with os.fdopen(descriptor, "r", encoding="utf-8") as handle:
            descriptor = -1
            return handle.read()
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def staging_file(destination: Path) -> tuple[int, Path]:
    for _ in range(100):
        staging = destination.parent / f".{destination.name}.{secrets.token_hex(8)}.tmp"
        try:
            descriptor = os.open(staging, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o666)
        except FileExistsError:
            continue
        return descriptor, staging
    raise AdoptionError(f"could not allocate a staging file for: {destination}")


def set_staging_mode(descriptor: int, staging: Path, mode: int) -> None:
    fchmod = getattr(os, "fchmod", None)
    if fchmod is not None:
        fchmod(descriptor, mode)
    else:
        os.chmod(staging, mode)


def atomic_copy_file(source: Path, destination: Path) -> None:
    descriptor, staging = staging_file(destination)
    staging_pending = True
    try:
        source_mode = stat.S_IMODE(source.stat().st_mode)
        with source.open("rb") as source_handle, os.fdopen(descriptor, "wb") as destination_handle:
            descriptor = -1
            set_staging_mode(destination_handle.fileno(), staging, source_mode)
            shutil.copyfileobj(source_handle, destination_handle)
            destination_handle.flush()
            os.fsync(destination_handle.fileno())
        os.replace(staging, destination)
        staging_pending = False
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if staging_pending and staging.exists():
            staging.unlink()


def atomic_write_text(destination: Path, content: str) -> None:
    mode: int | None = None
    try:
        metadata = destination.lstat()
    except FileNotFoundError:
        pass
    else:
        if stat.S_ISREG(metadata.st_mode):
            mode = stat.S_IMODE(metadata.st_mode)

    descriptor, staging = staging_file(destination)
    staging_pending = True
    try:
        if mode is not None:
            set_staging_mode(descriptor, staging, mode)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            descriptor = -1
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(staging, destination)
        staging_pending = False
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if staging_pending and staging.exists():
            staging.unlink()


def copy_file(
    source: Path,
    destination: Path,
    target: Path,
    force: bool,
    dry_run: bool,
    target_descriptor: int | None,
) -> str:
    if target_descriptor is not None and not dry_run:
        relative = destination.relative_to(target)
        with open_parent_directory(target_descriptor, relative, create=True) as (
            parent_descriptor,
            destination_name,
        ):
            metadata = output_metadata_at(parent_descriptor, destination_name)
            if metadata is not None:
                validate_output_metadata(metadata, destination)
                if not force:
                    return "skipped"

            action = "replace" if metadata is not None else "create"
            print_action(False, f"{action} {destination}")
            atomic_copy_file_at(source, parent_descriptor, destination_name)
            return action

    if not dry_run:
        validate_output_paths(target, [destination])
    if destination.exists() and not force:
        return "skipped"

    action = "replace" if destination.exists() else "create"
    print_action(dry_run, f"{action} {destination}")
    if not dry_run:
        destination.parent.mkdir(parents=True, exist_ok=True)
        atomic_copy_file(source, destination)
    return action


def write_text_file(
    destination: Path,
    content: str,
    target: Path,
    force: bool,
    dry_run: bool,
    target_descriptor: int | None,
) -> str:
    if target_descriptor is not None and not dry_run:
        relative = destination.relative_to(target)
        with open_parent_directory(target_descriptor, relative, create=True) as (
            parent_descriptor,
            destination_name,
        ):
            metadata = output_metadata_at(parent_descriptor, destination_name)
            if metadata is not None:
                validate_output_metadata(metadata, destination)
                if not force:
                    return "skipped"

            action = "replace" if metadata is not None else "create"
            print_action(False, f"{action} {destination}")
            mode = stat.S_IMODE(metadata.st_mode) if metadata is not None else None
            atomic_write_text_at(parent_descriptor, destination_name, content, mode)
            return action

    if not dry_run:
        validate_output_paths(target, [destination])
    if destination.exists() and not force:
        return "skipped"

    action = "replace" if destination.exists() else "create"
    print_action(dry_run, f"{action} {destination}")
    if not dry_run:
        destination.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_text(destination, content)
    return action


def append_agent_entry(
    target: Path,
    dry_run: bool,
    target_descriptor: int | None,
) -> str:
    agents_path = target / "AGENTS.md"
    if target_descriptor is not None and not dry_run:
        with open_parent_directory(target_descriptor, Path("AGENTS.md"), create=True) as (
            parent_descriptor,
            destination_name,
        ):
            metadata = output_metadata_at(parent_descriptor, destination_name)
            if metadata is None:
                print_action(False, f"create {agents_path}")
                atomic_copy_file_at(TEMPLATES_ROOT / "AGENTS.md", parent_descriptor, destination_name)
                return "create"

            validate_output_metadata(metadata, agents_path)
            current = read_text_at(parent_descriptor, destination_name, agents_path)
            if AGENTS_MARKER_START in current or "vault/index.md" in current:
                print_action(False, f"keep existing Trellium entry in {agents_path}")
                return "skipped"

            section = agent_entry_section()
            print_action(False, f"append Trellium entry to {agents_path}")
            atomic_write_text_at(
                parent_descriptor,
                destination_name,
                current.rstrip() + section + "\n",
                stat.S_IMODE(metadata.st_mode),
            )
            return "updated"

    if not dry_run:
        validate_output_paths(target, [agents_path])
    if not agents_path.exists():
        return copy_file(
            TEMPLATES_ROOT / "AGENTS.md",
            agents_path,
            target,
            force=False,
            dry_run=dry_run,
            target_descriptor=None,
        )

    current = agents_path.read_text(encoding="utf-8")
    if AGENTS_MARKER_START in current or "vault/index.md" in current:
        print_action(dry_run, f"keep existing Trellium entry in {agents_path}")
        return "skipped"

    section = agent_entry_section()

    print_action(dry_run, f"append Trellium entry to {agents_path}")
    if not dry_run:
        atomic_write_text(agents_path, current.rstrip() + section + "\n")
    return "updated"


def agent_entry_section() -> str:
    return f"""

{AGENTS_MARKER_START}
## Trellium

For non-trivial work, read these files before editing:

1. `vault/index.md` (includes the task-level and authority cheat sheet)
2. `vault/runtime.md`

Read `vault/governance.md` in full for Level B or Level C work, unclear classification, or governance-rule changes.

Use `vault/project.md` on first entry, `vault/handoff.md` when resuming interrupted work, and `vault/tasks/` for tracked or governed tasks.
{AGENTS_MARKER_END}
"""


def safe_project_readme(target: Path, target_descriptor: int | None) -> str | None:
    readme = target / "README.md"
    if target_descriptor is not None:
        try:
            with open_parent_directory(target_descriptor, Path("README.md"), create=False) as (
                parent_descriptor,
                readme_name,
            ):
                metadata = output_metadata_at(parent_descriptor, readme_name)
                if (
                    metadata is None
                    or not stat.S_ISREG(metadata.st_mode)
                    or metadata.st_nlink > 1
                ):
                    return None

                descriptor = os.open(readme_name, FILE_READ_FLAGS, dir_fd=parent_descriptor)
                try:
                    opened_metadata = os.fstat(descriptor)
                    if not stat.S_ISREG(opened_metadata.st_mode) or opened_metadata.st_nlink > 1:
                        return None
                    with os.fdopen(descriptor, "r", encoding="utf-8", errors="ignore") as handle:
                        descriptor = -1
                        return handle.read()
                finally:
                    if descriptor >= 0:
                        os.close(descriptor)
        except OSError:
            return None

    try:
        metadata = readme.lstat()
    except OSError:
        return None
    if (
        not stat.S_ISREG(metadata.st_mode)
        or metadata.st_nlink > 1
        or not is_within(readme.resolve(strict=False), target)
    ):
        return None
    try:
        return readme.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None


def project_summary(target: Path, target_descriptor: int | None) -> str:
    readme_content = safe_project_readme(target, target_descriptor)
    if readme_content is not None:
        for line in readme_content.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                return stripped
    return f"{target.name} project."


def render_project(target: Path, target_descriptor: int | None) -> str:
    return f"""# Project Context

## Summary

{project_summary(target, target_descriptor)}

## Goals

- Keep project-specific goals here.

## Current Phase

Existing project adoption via Trellium.

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

Trellium adoption recorded on {today}.

## Focus

- ADOPTION

## Active Tasks

One line per parallel task; keep bodies in `vault/tasks/<task-id>.md`, this
table holds pointers only.

| Task | Objective | Status | Next Action |
| --- | --- | --- | --- |
| ADOPTION | Maintain the Agent collaboration layer. | active | Update `vault/project.md` with durable facts. |

Status values: draft | active | blocked | ready_for_review | accepted |
superseded. For a task with a task file, the status here is a projection of
its `trellium-task-state` block: update the block first, then this row.
Focus names the current attention, not lifecycle; a status change edits only
the matching row. Demote paused-and-shelved tasks to `vault/parked.md`.

Acceptance: `AGENTS.md`, `vault/`, and `skills/agent-task/SKILL.md` exist and route future Agents to project memory.

Required Check: `python3 trellium.py adopt {target} --dry-run` from a Trellium checkout or Skill package, when available.

## Current Progress

- Agent collaboration layer has been initialized or refreshed.

## Constraints

- Move long execution history to `vault/tasks/*`.
- Demote paused tasks to `vault/parked.md` entries.
- Do not save secrets.
- Keep this file short; current line and entry budgets live in the `trellium-policy` block in `vault/index.md`.

## Recent Changes

- Added Trellium project memory files.

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


# --- Upgrade mechanism -----------------------------------------------------
#
# Project data is never replaced by upgrades. Protocol files follow the
# upstream template when the project has not modified them; diverging copies
# produce a proposal that the agent merges and the user confirms.


PLAN_SECTIONS = (
    ("pending", "?", "pending proposals from a previous upgrade"),
    ("conflict", "!", "local and upstream both changed; a proposal is written for agent merge"),
    ("apply", "~", "local copy is pristine; refresh from the upstream template"),
    ("add", "+", "new protocol file; create from the template"),
    ("add_skip", "+", "new protocol file already exists locally; kept"),
    ("remove", "-", "no longer shipped; local copy is pristine; remove"),
    ("remove_keep", "-", "no longer shipped; local copy was modified; kept"),
    ("keep", "o", "locally customized; upstream unchanged; kept"),
    ("protected", "x", "project data; never touched by upgrades"),
    ("missing", "!", "tracked file is missing"),
    ("in_sync", "=", "already matches upstream"),
)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_path(path: Path) -> str | None:
    try:
        return sha256_hex(path.read_bytes())
    except OSError:
        return None


def marker_region(text: str) -> str | None:
    start = text.find(AGENTS_MARKER_START)
    if start < 0:
        return None
    end = text.find(AGENTS_MARKER_END, start)
    if end < 0:
        return None
    return text[start : end + len(AGENTS_MARKER_END)]


def upstream_marker_region() -> str:
    region = marker_region(agent_entry_section())
    if region is None:
        raise AdoptionError("agent entry section is missing its markers")
    return region


def replace_marker_region(text: str, new_region: str) -> str:
    start = text.find(AGENTS_MARKER_START)
    end = text.find(AGENTS_MARKER_END, start)
    if start < 0 or end < 0:
        raise AdoptionError("Trellium marker region not found")
    end += len(AGENTS_MARKER_END)
    return text[:start] + new_region + text[end:]


def read_protocol_version() -> str:
    try:
        version = VERSION_FILE.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise AdoptionError(
            f"protocol version file is missing: {VERSION_FILE}; it must ship with the repository"
        ) from exc
    if not version:
        raise AdoptionError(f"protocol version file is empty: {VERSION_FILE}")
    return version


def parse_version(version: str | None) -> tuple[int, ...] | None:
    if not version:
        return None
    try:
        return tuple(int(part) for part in version.split("."))
    except ValueError:
        return None


def read_migration_sections() -> list[tuple[str, str]]:
    """Return (version, title) pairs for every release section in MIGRATIONS.md."""
    try:
        content = MIGRATIONS_FILE.read_text(encoding="utf-8")
    except OSError:
        return []
    sections: list[tuple[str, str]] = []
    for line in content.splitlines():
        if not line.startswith("## "):
            continue
        header = line[3:].strip()
        parts = header.split(None, 1)
        if not parts or parse_version(parts[0]) is None:
            continue
        title = parts[1].strip() if len(parts) > 1 else ""
        title = title.lstrip("—–- ").strip()
        sections.append((parts[0], title))
    return sections


def migrations_after(version: str | None) -> list[tuple[str, str]]:
    installed = parse_version(version)
    if installed is None:
        return read_migration_sections()
    return [
        section
        for section in read_migration_sections()
        if (parsed := parse_version(section[0])) is not None and parsed > installed
    ]


def stamp_path(target: Path) -> Path:
    return target / STAMP_RELATIVE


def read_stamp(target: Path) -> dict | None:
    path = stamp_path(target)
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise AdoptionError(f"could not read adoption stamp: {path}: {exc}") from exc
    try:
        stamp = json.loads(raw)
    except ValueError as exc:
        raise AdoptionError(f"adoption stamp is not valid JSON: {path}") from exc
    if not isinstance(stamp, dict) or not isinstance(stamp.get("files"), dict):
        raise AdoptionError(f"adoption stamp has an unexpected schema: {path}")
    return stamp


def assert_upgrade_writable(target: Path, relative: str) -> None:
    """Refuse writes outside the protocol-carrier scope during upgrades."""
    if relative == STAMP_RELATIVE:
        return
    if relative.startswith(f"{PROPOSAL_DIRECTORY}/"):
        return
    if relative.startswith(f"{BACKUP_DIRECTORY}/"):
        return
    role = FILE_ROLES.get(relative)
    if role in WRITABLE_ROLES:
        return
    if role == "data" and not (target / relative).exists():
        # Creating an absent starter template never discards project data.
        return
    raise AdoptionError(
        f"refusing to write outside the protocol upgrade scope: {relative} (role: {role or 'untracked'})"
    )


def local_hash_for_role(target: Path, relative: str, role: str) -> str | None:
    if role != "marker":
        return hash_path(target / relative)
    try:
        text = (target / relative).read_text(encoding="utf-8")
    except OSError:
        return None
    region = marker_region(text)
    if region is None:
        return None
    return sha256_hex(region.encode("utf-8"))


def upstream_hash_for_role(relative: str, role: str) -> str | None:
    if role == "marker":
        return sha256_hex(upstream_marker_region().encode("utf-8"))
    return hash_path(TEMPLATES_ROOT / relative)


def open_upgrade_descriptor(target: Path) -> int | None:
    if not ANCHORED_WRITES_SUPPORTED:
        return None
    return open_target_directory(target, create=False)


def resolve_existing_target(value: str) -> Path:
    try:
        target = Path(value).expanduser().resolve()
    except (OSError, RuntimeError) as exc:
        raise AdoptionError(f"could not resolve target: {exc}") from exc
    if target == Path(target.anchor):
        raise AdoptionError(f"refusing to operate on filesystem root: {target}")
    if not target.is_dir():
        raise AdoptionError(f"target is not an existing directory: {target}")
    return target


def write_stamp_file(target: Path, stamp: dict, target_descriptor: int | None) -> None:
    content = json.dumps(stamp, indent=2, sort_keys=True) + "\n"
    if target_descriptor is not None:
        relative = Path(STAMP_RELATIVE)
        with open_parent_directory(target_descriptor, relative, create=True) as (
            parent_descriptor,
            name,
        ):
            metadata = output_metadata_at(parent_descriptor, name)
            mode = stat.S_IMODE(metadata.st_mode) if metadata is not None else None
            if metadata is not None:
                validate_output_metadata(metadata, target / STAMP_RELATIVE)
            atomic_write_text_at(parent_descriptor, name, content, mode)
        return
    destination = target / STAMP_RELATIVE
    destination.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(destination, content)


def write_adoption_stamp(
    target: Path,
    actions: dict[str, str],
    rendered_files: dict[str, str],
    target_descriptor: int | None,
) -> None:
    previous = read_stamp(target) or {}
    previous_files = previous.get("files", {}) if isinstance(previous, dict) else {}
    files: dict[str, dict] = {}
    for relative, role in FILE_ROLES.items():
        action = actions.get(relative, "skipped")
        if relative == "AGENTS.md":
            # Two flavors: a template file copied wholesale (whole-file "merge"
            # semantics) or a marker section appended to a user file ("marker"
            # semantics). The stamp records which one was installed.
            if action == "create":
                template_hash = hash_path(TEMPLATES_ROOT / "AGENTS.md")
                if template_hash is None:
                    raise AdoptionError(f"template file does not exist: {TEMPLATES_ROOT / 'AGENTS.md'}")
                entry = {"role": "merge", "baseline": template_hash}
            elif action == "updated":
                entry = {"role": "marker", "baseline": sha256_hex(upstream_marker_region().encode("utf-8"))}
            else:
                try:
                    agents_text = (target / relative).read_text(encoding="utf-8")
                except OSError:
                    continue
                region = marker_region(agents_text)
                if region is not None:
                    entry = {"role": "marker", "baseline": sha256_hex(region.encode("utf-8"))}
                else:
                    entry = {"role": "merge", "baseline": sha256_hex(agents_text.encode("utf-8"))}
        elif relative in rendered_files:
            if action != "skipped":
                entry = {"role": role, "baseline": sha256_hex(rendered_files[relative].encode("utf-8"))}
            else:
                baseline = local_hash_for_role(target, relative, role)
                if baseline is None:
                    continue
                entry = {"role": role, "baseline": baseline}
        else:
            template_hash = hash_path(TEMPLATES_ROOT / relative)
            if template_hash is None:
                raise AdoptionError(f"template file does not exist: {TEMPLATES_ROOT / relative}")
            if action != "skipped":
                entry = {"role": role, "baseline": template_hash}
            else:
                baseline = local_hash_for_role(target, relative, role)
                if baseline is None:
                    entry = {"role": role, "baseline": template_hash}
                else:
                    entry = {"role": role, "baseline": baseline}
        if action == "skipped":
            preserved = previous_files.get(relative)
            if preserved is not None and preserved.get("baseline") == entry["baseline"]:
                entry = dict(preserved)
            else:
                # We did not write these bytes; they are only observed, so later
                # upstream changes must produce proposals instead of auto-replace.
                entry["observed"] = True
        files[relative] = entry
    stamp = {
        "schema_version": 1,
        "protocol_version": read_protocol_version(),
        "adopted_at": previous.get("adopted_at") or date.today().isoformat(),
        "last_upgrade": previous.get("last_upgrade"),
        "trust": previous.get("trust", "versioned"),
        "files": files,
    }
    write_stamp_file(target, stamp, target_descriptor)


def build_upgrade_plan(target: Path, stamp: dict) -> dict[str, list[dict]]:
    trust = stamp.get("trust", "versioned")
    entries: dict[str, dict] = stamp["files"]
    plan: dict[str, list[dict]] = {key: [] for key, _, _ in PLAN_SECTIONS}

    for relative, entry in sorted(entries.items()):
        role = entry.get("role") or FILE_ROLES.get(relative, "template")
        if entry.get("pending"):
            plan["pending"].append(
                {"path": relative, "role": role, "reason": "resolve the proposal, then run upgrade --complete"}
            )
            continue
        if relative not in FILE_ROLES:
            local = local_hash_for_role(target, relative, role)
            if local is None:
                plan["missing"].append({"path": relative, "role": role, "reason": "no longer shipped and missing locally"})
            elif local == entry.get("baseline"):
                plan["remove"].append({"path": relative, "role": role, "reason": "no longer shipped; local copy is pristine"})
            else:
                plan["remove_keep"].append({"path": relative, "role": role, "reason": "no longer shipped; local copy was modified"})
            continue
        if role == "data":
            plan["protected"].append({"path": relative, "role": role, "reason": "project data is never replaced by upgrades"})
            continue
        upstream = upstream_hash_for_role(relative, role)
        local = local_hash_for_role(target, relative, role)
        baseline = entry.get("baseline")
        observed = bool(entry.get("observed")) or trust == "unversioned"
        if upstream is None:
            plan["missing"].append({"path": relative, "role": role, "reason": "upstream template is missing from this repository"})
        elif local is None:
            if role == "marker":
                plan["add"].append({"path": relative, "role": role, "reason": "marker region absent; append the Trellium entry"})
            else:
                plan["missing"].append({"path": relative, "role": role, "reason": "file is missing locally; re-run adopt or restore it"})
        elif local == upstream:
            plan["in_sync"].append({"path": relative, "role": role})
        elif local == baseline:
            if observed:
                if upstream == entry.get("absorbed_upstream"):
                    plan["in_sync"].append(
                        {"path": relative, "role": role, "reason": "this upstream version is already absorbed"}
                    )
                else:
                    plan["conflict"].append(
                        {"path": relative, "role": role, "reason": "baseline was observed, not written; upstream changed"}
                    )
            else:
                plan["apply"].append({"path": relative, "role": role, "reason": "local copy is pristine; upstream updated"})
        elif upstream == baseline:
            plan["keep"].append({"path": relative, "role": role, "reason": "locally customized; upstream unchanged"})
        else:
            plan["conflict"].append({"path": relative, "role": role, "reason": "local and upstream both changed"})

    for relative, role in sorted(FILE_ROLES.items()):
        if relative in entries or relative in RENDERED_FILES:
            continue
        if role == "marker":
            try:
                text = (target / relative).read_text(encoding="utf-8")
            except OSError:
                text = ""
            if marker_region(text) is not None:
                plan["add_skip"].append({"path": relative, "role": role, "reason": "marker region present but untracked; kept"})
            elif "vault/index.md" in text:
                plan["add_skip"].append({"path": relative, "role": role, "reason": "agent entry already routes to the vault; kept"})
            else:
                plan["add"].append({"path": relative, "role": role, "reason": "append the Trellium entry"})
            continue
        if (target / relative).exists():
            plan["add_skip"].append(
                {"path": relative, "role": role, "reason": "exists locally but untracked; kept (run baseline to track it)"}
            )
        else:
            plan["add"].append({"path": relative, "role": role, "reason": "new protocol file"})

    return plan


def plan_exit_code(plan: dict[str, list[dict]]) -> int:
    if plan["conflict"] or plan["pending"]:
        return EXIT_CONFLICT
    if plan["apply"] or plan["add"] or plan["remove"]:
        return EXIT_ACTIONABLE
    return 0


def print_plan(plan: dict[str, list[dict]]) -> None:
    for key, symbol, description in PLAN_SECTIONS:
        items = plan.get(key, [])
        if not items:
            continue
        print(f"{key} ({description}):")
        for item in items:
            reason = item.get("reason")
            suffix = f"  # {reason}" if reason else ""
            print(f"  {symbol} {item['path']}{suffix}")
        print()


def print_upgrade_header(target: Path, stamp: dict) -> None:
    installed = stamp.get("protocol_version") or "unknown (unversioned baseline)"
    available = read_protocol_version()
    relationship = "==" if installed == available else "->"
    print(f"upgrade report for {target}")
    print(f"installed protocol: {installed} {relationship} available: {available}")
    print()


def print_playbook(sections: list[tuple[str, str]]) -> None:
    if not sections:
        return
    print("migration playbook (init/MIGRATIONS.md):")
    for version, title in sections:
        print(f"  * {version} - {title}")
    print()


# --- Vault check (read-only) -----------------------------------------------
#
# `check` validates the minimal canonical state layer: the trellium-task-state
# block in Level B/C task files, the trellium-policy block in vault/index.md,
# the runtime projection of task lifecycles, hot-file budgets, and TASK
# storage versus Git. It never writes, never executes content, and never
# follows symbolic links into vault inputs.

CHECK_ERROR_EXIT = 2

TASK_STATE_MARKER = "trellium-task-state"
POLICY_MARKER = "trellium-policy"
COMMENT_BLOCK_END = "-->"

TASK_ID_PATTERN = r"TASK-[0-9]{4,}"
TASK_ID_RE = re.compile(rf"^{TASK_ID_PATTERN}$")
TASK_FILE_ID_RE = re.compile(rf"^({TASK_ID_PATTERN})(?:-|\.md$)")
REVIEW_LEDGER_RE = re.compile(rf"^{TASK_ID_PATTERN}-review\.md$")

LIFECYCLE_VALUES = ("draft", "active", "blocked", "ready_for_review", "accepted", "superseded")
GATE_VALUES = ("pending", "in_progress", "passed", "partial", "blocked", "not_authorized", "not_applicable")
TASK_STORAGE_VALUES = ("tracked", "local")

STATE_REQUIRED_FIELDS = ("schema_version", "task_id", "level", "authority_level", "lifecycle")
STATE_OPTIONAL_FIELDS = ("current_slice", "gates")

BUDGET_FILE_KEYS = {
    "runtime": ("max_lines", "max_recent_entries"),
    "handoff": ("max_lines", "max_entries"),
    "decisions": ("max_lines", "max_records"),
    "parked": ("max_lines", "max_entries"),
    "tasks": ("max_active_tasks",),
}
# Maps a configured policy threshold to the measurement key it constrains.
BUDGET_MEASUREMENT_KEYS = {
    "runtime": {"max_lines": "lines", "max_recent_entries": "recent_entries"},
    "handoff": {"max_lines": "lines", "max_entries": "entries"},
    "decisions": {"max_lines": "lines", "max_records": "records"},
    "parked": {"max_lines": "lines", "max_entries": "entries"},
}

REQUIRED_VAULT_FILES = (
    "vault/index.md",
    "vault/project.md",
    "vault/governance.md",
    "vault/runtime.md",
    "vault/handoff.md",
    "vault/decisions.md",
    "vault/parked.md",
    "vault/tasks/README.md",
)

FINDING_PHASES = (
    "required-files",
    "policy",
    "task-state",
    "runtime-projection",
    "budgets",
    "storage",
)


def _reject_json_constant(name: str) -> None:
    raise ValueError(f"non-standard JSON constant: {name}")


def is_strict_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def extract_comment_blocks(text: str, marker: str) -> tuple[list[str], str | None]:
    """Return the payloads of every `<!-- marker ... -->` block in the text."""
    start_token = f"<!-- {marker}"
    payloads: list[str] = []
    index = 0
    while True:
        start = text.find(start_token, index)
        if start < 0:
            return payloads, None
        following = text[start + len(start_token) : start + len(start_token) + 1]
        if following and following not in ("\n", "\r"):
            # A different marker that merely shares the prefix (e.g.
            # trellium-policy-history) is not a block of this marker.
            index = start + len(start_token)
            continue
        end = text.find(COMMENT_BLOCK_END, start)
        if end < 0:
            return [], f"unterminated <!-- {marker} ... --> block"
        payloads.append(text[start + len(start_token) : end].strip())
        index = end + len(COMMENT_BLOCK_END)


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_block_object(payload: str) -> tuple[dict | None, str]:
    try:
        value = json.loads(
            payload,
            parse_constant=_reject_json_constant,
            object_pairs_hook=_reject_duplicate_keys,
        )
    except ValueError as exc:
        return None, f"invalid JSON ({exc})"
    if not isinstance(value, dict):
        return None, "block content is not a JSON object"
    return value, ""


def validate_state_object(state: dict) -> list[str]:
    errors: list[str] = []
    known = set(STATE_REQUIRED_FIELDS) | set(STATE_OPTIONAL_FIELDS)
    unknown = sorted(set(state) - known)
    if unknown:
        errors.append(f"unknown field(s): {', '.join(unknown)}")
    missing = [field for field in STATE_REQUIRED_FIELDS if field not in state]
    if missing:
        errors.append(f"missing field(s): {', '.join(missing)}")

    if "schema_version" in state:
        if not is_strict_int(state["schema_version"]) or state["schema_version"] != 1:
            errors.append("schema_version must be the integer 1")
    if "task_id" in state:
        task_id = state["task_id"]
        if not isinstance(task_id, str) or TASK_ID_RE.match(task_id) is None:
            errors.append(f"task_id must match {TASK_ID_PATTERN}")
    if "level" in state:
        if state["level"] not in ("B", "C"):
            errors.append('level must be "B" or "C"')
    if "authority_level" in state:
        authority = state["authority_level"]
        if not is_strict_int(authority) or not 0 <= authority <= 4:
            errors.append("authority_level must be an integer in 0..4")
    if "lifecycle" in state:
        if state["lifecycle"] not in LIFECYCLE_VALUES:
            errors.append(f"lifecycle must be one of: {', '.join(LIFECYCLE_VALUES)}")
    if "current_slice" in state:
        current_slice = state["current_slice"]
        if not isinstance(current_slice, str) or not current_slice.strip():
            errors.append("current_slice must be a non-empty string")
    if "gates" in state:
        gates = state["gates"]
        if not isinstance(gates, dict):
            errors.append("gates must be an object")
        else:
            for gate_id, gate_value in gates.items():
                if not isinstance(gate_id, str) or not gate_id.strip():
                    errors.append("gate ids must be non-empty strings")
                elif gate_value not in GATE_VALUES:
                    errors.append(
                        f"gate {gate_id!r} must be one of: {', '.join(GATE_VALUES)}"
                    )
    return errors


def validate_policy_object(policy: dict) -> list[str]:
    errors: list[str] = []
    known = {"schema_version", "task_storage", "budgets"}
    unknown = sorted(set(policy) - known)
    if unknown:
        errors.append(f"unknown field(s): {', '.join(unknown)}")
    missing = [field for field in ("schema_version", "task_storage") if field not in policy]
    if missing:
        errors.append(f"missing field(s): {', '.join(missing)}")
    if "schema_version" in policy:
        if not is_strict_int(policy["schema_version"]) or policy["schema_version"] != 1:
            errors.append("schema_version must be the integer 1")
    if "task_storage" in policy:
        if policy["task_storage"] not in TASK_STORAGE_VALUES:
            errors.append(f"task_storage must be one of: {', '.join(TASK_STORAGE_VALUES)}")
    if "budgets" in policy:
        budgets = policy["budgets"]
        if not isinstance(budgets, dict):
            errors.append("budgets must be an object")
        else:
            for file_key, thresholds in budgets.items():
                allowed = BUDGET_FILE_KEYS.get(file_key)
                if allowed is None:
                    errors.append(f"unknown budgets key: {file_key}")
                    continue
                if not isinstance(thresholds, dict):
                    errors.append(f"budgets.{file_key} must be an object")
                    continue
                for threshold_key, threshold_value in thresholds.items():
                    if threshold_key not in allowed:
                        errors.append(
                            f"unknown threshold budgets.{file_key}.{threshold_key}"
                        )
                    elif not is_strict_int(threshold_value) or threshold_value <= 0:
                        errors.append(
                            f"budgets.{file_key}.{threshold_key} must be a positive integer"
                        )
    return errors


def read_regular_text(path: Path) -> tuple[str | None, str | None]:
    """Read a file without following symlinks; (None, None) means missing."""
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return None, None
    except OSError as exc:
        return None, f"unreadable: {exc}"
    if stat.S_ISLNK(metadata.st_mode):
        return None, "symlink"
    if not stat.S_ISREG(metadata.st_mode):
        return None, "not a regular file"
    try:
        return path.read_text(encoding="utf-8"), None
    except (OSError, UnicodeError) as exc:
        return None, f"unreadable: {exc}"


def markdown_section_lines(text: str, title: str) -> list[str]:
    """Return the body lines of a `## <title>` section, stopping at the next heading."""
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == f"## {title}":
            body: list[str] = []
            for candidate in lines[index + 1 :]:
                if candidate.startswith("## "):
                    break
                body.append(candidate)
            return body
    return []


def parse_runtime_task_pointers(runtime_text: str) -> tuple[list[tuple[str, str]], list[str], list[tuple[str, str]]]:
    """Return (task rows, focus pointers, problems) from fixed runtime sections."""
    rows: list[tuple[str, str]] = []
    focus: list[str] = []
    problems: list[tuple[str, str]] = []

    for line in markdown_section_lines(runtime_text, "Focus"):
        stripped = line.strip()
        if stripped.startswith("- "):
            candidate = stripped[2:].strip()
            if TASK_ID_RE.match(candidate):
                focus.append(candidate)

    for line in markdown_section_lines(runtime_text, "Active Tasks"):
        stripped = line.strip()
        if not (stripped.startswith("|") and stripped.endswith("|")):
            continue
        cells = [cell.strip() for cell in stripped[1:-1].split("|")]
        if all(set(cell) <= {"-", ":", ""} for cell in cells):
            continue
        if not cells[0].startswith("TASK-"):
            continue
        if len(cells) < 4:
            problems.append(("invalid", f"malformed Active Tasks row: {stripped}"))
            continue
        if TASK_ID_RE.match(cells[0]) is None:
            problems.append(("invalid", f"malformed task id in Active Tasks row: {cells[0]}"))
            continue
        rows.append((cells[0], cells[2]))
    return rows, focus, problems


def count_recent_entries(runtime_text: str) -> int:
    return sum(
        1
        for line in markdown_section_lines(runtime_text, "Recent Changes")
        if re.match(r"^\s*-\s+", line)
    )


def count_handoff_entries(handoff_text: str) -> int:
    return sum(1 for line in handoff_text.splitlines() if re.match(r"^##\s+(TASK-|SESSION)", line))


def count_decision_records(decisions_text: str) -> int:
    total = 0
    for line in decisions_text.splitlines():
        if re.match(r"^\s*-\s*D-[0-9]", line) or re.match(r"^##\s*[0-9]{4}-[0-9]{2}-[0-9]{2}", line):
            total += 1
    return total


def count_parked_entries(parked_text: str) -> int:
    return sum(1 for line in parked_text.splitlines() if re.match(r"^\s*-\s*P-[0-9]", line))


def git_run(target: Path, arguments: list[str], input_bytes: bytes | None = None) -> subprocess.CompletedProcess | None:
    try:
        return subprocess.run(
            ["git", *arguments],
            cwd=target,
            input=input_bytes,
            capture_output=True,
            check=False,
        )
    except OSError:
        return None


def git_in_worktree(target: Path) -> bool:
    """True when the target sits inside a usable Git worktree."""
    result = git_run(target, ["rev-parse", "--show-toplevel"])
    return result is not None and result.returncode == 0


def git_tracked_files(target: Path) -> set[str] | None:
    result = git_run(target, ["ls-files", "-z", "--", "."])
    if result is None or result.returncode != 0:
        return None
    return {
        name.decode("utf-8", "surrogateescape")
        for name in result.stdout.split(b"\0")
        if name
    }


def git_ignored_files(target: Path, relatives: list[str]) -> set[str] | None:
    if not relatives:
        return set()
    input_bytes = b"".join(
        relative.encode("utf-8", "surrogateescape") + b"\0" for relative in relatives
    )
    result = git_run(target, ["check-ignore", "-z", "--stdin", "--"], input_bytes=input_bytes)
    if result is None or result.returncode not in (0, 1):
        return None
    return {
        name.decode("utf-8", "surrogateescape")
        for name in result.stdout.split(b"\0")
        if name
    }


class VaultCheckRun:
    """Accumulates findings and measurements for one read-only check run."""

    def __init__(self, target: Path) -> None:
        self.target = target
        self.findings: list[tuple[int, dict, str]] = []
        self.measurements: dict = {}

    def add(self, phase: str, code: str, severity: str, path: str, message: str, task_id: str | None = None) -> None:
        finding = {"code": code, "severity": severity, "path": path, "message": message}
        if task_id is not None:
            finding["task_id"] = task_id
        self.findings.append((FINDING_PHASES.index(phase), finding, path))

    def sorted_findings(self) -> list[dict]:
        ordered = sorted(self.findings, key=lambda item: (item[0], item[2], item[1]["code"], item[1]["message"]))
        return [finding for _phase, finding, _path in ordered]

    @property
    def errors(self) -> list[dict]:
        return [finding for finding in self.sorted_findings() if finding["severity"] == "error"]

    @property
    def warnings(self) -> list[dict]:
        return [finding for finding in self.sorted_findings() if finding["severity"] == "warning"]


def check_required_files(run: VaultCheckRun) -> dict[str, str]:
    """Read the fixed vault files; report missing/symlinked inputs."""
    texts: dict[str, str] = {}
    vault = run.target / "vault"
    tasks_dir = vault / "tasks"
    try:
        tasks_metadata = tasks_dir.lstat()
    except FileNotFoundError:
        run.add("required-files", "REQUIRED_FILE_MISSING", "warning", "vault/tasks", "required vault directory is missing: vault/tasks/")
    else:
        if stat.S_ISLNK(tasks_metadata.st_mode):
            run.add("required-files", "SYMLINK_INPUT", "error", "vault/tasks", "vault/tasks/ is a symbolic link; refusing to follow it")
        elif not stat.S_ISDIR(tasks_metadata.st_mode):
            run.add("required-files", "REQUIRED_FILE_MISSING", "warning", "vault/tasks", "vault/tasks/ is not a directory")

    for relative in REQUIRED_VAULT_FILES:
        text, error = read_regular_text(run.target / relative)
        if error == "symlink":
            run.add("required-files", "SYMLINK_INPUT", "error", relative, f"{relative} is a symbolic link; refusing to follow it")
        elif error is not None:
            run.add("required-files", "FILE_UNREADABLE", "error", relative, f"could not read {relative}: {error}")
        elif text is None:
            run.add("required-files", "REQUIRED_FILE_MISSING", "warning", relative, f"required vault file is missing: {relative}")
        else:
            texts[relative] = text
    return texts


def check_policy_block(run: VaultCheckRun, index_text: str | None) -> dict | None:
    if index_text is None:
        run.add("policy", "POLICY_MISSING", "warning", "vault/index.md", "no vault/index.md to hold a trellium-policy block; project budgets and TASK storage are unresolved (legacy)")
        return None
    blocks, error = extract_comment_blocks(index_text, POLICY_MARKER)
    if error is not None:
        run.add("policy", "POLICY_INVALID", "error", "vault/index.md", error)
        return None
    if not blocks:
        run.add("policy", "POLICY_MISSING", "warning", "vault/index.md", "no trellium-policy block in vault/index.md; project budgets and TASK storage are unresolved (legacy)")
        return None
    if len(blocks) > 1:
        run.add("policy", "POLICY_INVALID", "error", "vault/index.md", f"expected at most one {POLICY_MARKER} block, found {len(blocks)}")
        return None
    policy, error = parse_block_object(blocks[0])
    if policy is None:
        run.add("policy", "POLICY_INVALID", "error", "vault/index.md", f"invalid {POLICY_MARKER} block: {error}")
        return None
    validation_errors = validate_policy_object(policy)
    if validation_errors:
        run.add("policy", "POLICY_INVALID", "error", "vault/index.md", f"invalid {POLICY_MARKER} block: " + "; ".join(validation_errors))
        return None
    return policy


def discover_task_files(run: VaultCheckRun) -> tuple[list[dict], list[str], list[str]]:
    """Collect current task entities plus review-ledger and archive paths."""
    tasks_dir = run.target / "vault" / "tasks"
    current: list[dict] = []
    ledgers: list[str] = []
    archive: list[str] = []
    if tasks_dir.is_symlink():
        # Reported by check_required_files; never enumerate through the link.
        return current, ledgers, archive
    try:
        entries = sorted(tasks_dir.iterdir(), key=lambda path: path.name)
    except OSError as exc:
        run.add("task-state", "FILE_UNREADABLE", "error", "vault/tasks", f"could not list vault/tasks/: {exc}")
        return current, ledgers, archive

    for entry in entries:
        relative = entry.relative_to(run.target).as_posix()
        if entry.name.startswith("."):
            continue
        if entry.is_symlink():
            run.add("task-state", "SYMLINK_INPUT", "error", relative, f"{relative} is a symbolic link; refusing to follow it")
            if REVIEW_LEDGER_RE.match(entry.name):
                ledgers.append(relative)
            elif TASK_FILE_ID_RE.match(entry.name) and entry.name.endswith(".md"):
                current.append({"path": relative, "task_id": TASK_FILE_ID_RE.match(entry.name).group(1), "lifecycle": None, "legacy": False, "valid": False})
            continue
        if REVIEW_LEDGER_RE.match(entry.name):
            ledgers.append(relative)
            continue
        match = TASK_FILE_ID_RE.match(entry.name)
        if match is None or not entry.name.endswith(".md"):
            continue
        text, error = read_regular_text(entry)
        if error is not None or text is None:
            # (None, None): the entry vanished between listing and reading.
            if error is not None:
                run.add("task-state", "FILE_UNREADABLE", "error", relative, f"could not read {relative}: {error}")
            continue
        state, failures = parse_task_state_block(text)
        if failures is None:
            # (None, None): a legacy task file carries no state block.
            run.add(
                "task-state",
                "TASK_STATE_MISSING",
                "warning",
                relative,
                "legacy task file without a trellium-task-state block; lifecycle is unresolved",
                task_id=match.group(1),
            )
            current.append({"path": relative, "task_id": match.group(1), "lifecycle": None, "legacy": True, "valid": False})
            continue
        if failures:
            for code, message in failures:
                run.add("task-state", code, "error", relative, message, task_id=match.group(1))
            current.append({"path": relative, "task_id": match.group(1), "lifecycle": None, "legacy": False, "valid": False})
            continue
        if state["task_id"] != match.group(1):
            run.add(
                "task-state",
                "TASK_ID_MISMATCH",
                "error",
                relative,
                f"trellium-task-state task_id {state['task_id']!r} does not match the file name prefix {match.group(1)}",
                task_id=match.group(1),
            )
            current.append({"path": relative, "task_id": match.group(1), "lifecycle": None, "legacy": False, "valid": False})
            continue
        current.append({"path": relative, "task_id": match.group(1), "lifecycle": state["lifecycle"], "legacy": False, "valid": True})

    archive_dir = tasks_dir / "archive"
    if archive_dir.is_symlink():
        run.add("task-state", "SYMLINK_INPUT", "error", "vault/tasks/archive", "vault/tasks/archive/ is a symbolic link; refusing to follow it")
    elif archive_dir.is_dir():
        for entry in sorted(archive_dir.iterdir(), key=lambda path: path.name):
            if not (TASK_FILE_ID_RE.match(entry.name) and entry.name.endswith(".md")):
                continue
            relative = entry.relative_to(run.target).as_posix()
            if entry.is_symlink():
                run.add("task-state", "SYMLINK_INPUT", "error", relative, f"{relative} is a symbolic link; refusing to follow it")
            archive.append(relative)

    id_counts: dict[str, int] = {}
    for task in current:
        id_counts[task["task_id"]] = id_counts.get(task["task_id"], 0) + 1
    for task in current:
        if id_counts[task["task_id"]] > 1:
            run.add(
                "task-state",
                "TASK_ID_DUPLICATE",
                "error",
                task["path"],
                f"task_id {task['task_id']} is declared by {id_counts[task['task_id']]} task files; keep exactly one current task per id",
                task_id=task["task_id"],
            )
            task["valid"] = False
    return current, ledgers, archive


def parse_task_state_block(text: str) -> tuple[dict | None, list[tuple[str, str]] | None]:
    """Return (state, []) on success, (None, None) for legacy, or (None, failures)."""
    blocks, error = extract_comment_blocks(text, TASK_STATE_MARKER)
    if error is not None:
        return None, [("TASK_STATE_INVALID", error)]
    if not blocks:
        return None, None
    if len(blocks) > 1:
        return None, [
            ("TASK_STATE_DUPLICATE", f"expected at most one {TASK_STATE_MARKER} block, found {len(blocks)}")
        ]
    state, error = parse_block_object(blocks[0])
    if state is None:
        return None, [("TASK_STATE_INVALID", f"invalid {TASK_STATE_MARKER} block: {error}")]
    validation_errors = validate_state_object(state)
    if validation_errors:
        return None, [
            ("TASK_STATE_INVALID", f"invalid {TASK_STATE_MARKER} block: {message}")
            for message in validation_errors
        ]
    return state, []


def check_runtime_projection(run: VaultCheckRun, runtime_text: str | None, tasks: list[dict]) -> None:
    if runtime_text is None:
        return
    by_id: dict[str, list[dict]] = {}
    for task in tasks:
        by_id.setdefault(task["task_id"], []).append(task)

    def resolve(task_id: str) -> None:
        matches = by_id.get(task_id)
        if not matches:
            run.add("runtime-projection", "TASK_RUNTIME_MISSING", "error", "vault/runtime.md", f"runtime points to a task file that does not exist: {task_id}", task_id=task_id)
            return
        task = matches[0]
        if task["legacy"]:
            run.add("runtime-projection", "TASK_RUNTIME_UNRESOLVED", "warning", "vault/runtime.md", f"runtime row for {task_id} cannot be verified: the task file has no trellium-task-state block (legacy)", task_id=task_id)
        elif task.get("lifecycle") is None:
            run.add("runtime-projection", "TASK_RUNTIME_UNRESOLVED", "warning", "vault/runtime.md", f"runtime row for {task_id} cannot be verified: the task state block is invalid", task_id=task_id)

    rows, focus, problems = parse_runtime_task_pointers(runtime_text)
    for _kind, detail in problems:
        run.add("runtime-projection", "TASK_RUNTIME_INVALID", "error", "vault/runtime.md", detail)

    row_counts: dict[str, int] = {}
    for task_id, _status in rows:
        row_counts[task_id] = row_counts.get(task_id, 0) + 1
    for task_id, count in row_counts.items():
        if count > 1:
            run.add(
                "runtime-projection",
                "TASK_RUNTIME_DUPLICATE",
                "error",
                "vault/runtime.md",
                f"Active Tasks table has {count} rows for {task_id}; keep one row per task",
                task_id=task_id,
            )

    projected = set(row_counts)
    closed = {"accepted", "superseded"}
    for task in tasks:
        if not task["valid"] or task["lifecycle"] in closed:
            continue
        if task["task_id"] not in projected:
            run.add(
                "runtime-projection",
                "TASK_PROJECTION_MISSING",
                "error",
                "vault/runtime.md",
                f"open task {task['task_id']} ({task['lifecycle']}) has no Active Tasks row in runtime.md; the runtime projection is missing",
                task_id=task["task_id"],
            )

    for task_id, status in rows:
        resolve(task_id)
        matches = by_id.get(task_id) or []
        task = matches[0] if matches else None
        if task is None or task["legacy"] or task.get("lifecycle") is None:
            continue
        if status not in LIFECYCLE_VALUES:
            run.add("runtime-projection", "TASK_RUNTIME_INVALID", "error", "vault/runtime.md", f"Active Tasks row for {task_id} uses status {status!r} outside the lifecycle enum", task_id=task_id)
        elif status != task["lifecycle"]:
            run.add(
                "runtime-projection",
                "TASK_RUNTIME_DRIFT",
                "error",
                "vault/runtime.md",
                f"runtime row for {task_id} says {status!r} but the trellium-task-state block says {task['lifecycle']!r}",
                task_id=task_id,
            )
    for task_id in focus:
        resolve(task_id)


def measure_hot_files(run: VaultCheckRun, texts: dict[str, str]) -> None:
    definitions = (
        ("runtime", "vault/runtime.md", "recent_entries", count_recent_entries),
        ("handoff", "vault/handoff.md", "entries", count_handoff_entries),
        ("decisions", "vault/decisions.md", "records", count_decision_records),
        ("parked", "vault/parked.md", "entries", count_parked_entries),
    )
    for key, relative, entry_key, counter in definitions:
        text = texts.get(relative)
        if text is None:
            continue
        lines = text.splitlines()
        encoded = text.encode("utf-8")
        run.measurements[key] = {
            "lines": len(lines),
            "bytes": len(encoded),
            "max_line_bytes": max((len(line.encode("utf-8")) for line in lines), default=0),
            entry_key: counter(text),
        }


def check_budgets(run: VaultCheckRun, policy: dict | None) -> None:
    if policy is None:
        return
    budgets = policy.get("budgets") or {}
    for file_key, measurement in run.measurements.items():
        thresholds = budgets.get(file_key)
        if not isinstance(thresholds, dict):
            continue
        for threshold_key, measured_key in BUDGET_MEASUREMENT_KEYS.get(file_key, {}).items():
            limit = thresholds.get(threshold_key)
            if limit is None:
                continue
            measured = measurement[measured_key]
            if measured > limit:
                run.add(
                    "budgets",
                    "BUDGET_EXCEEDED",
                    "error",
                    f"vault/{file_key}.md",
                    f"{file_key}.{measured_key} is {measured}, above the configured limit {threshold_key}={limit}",
                )


def check_task_budget(run: VaultCheckRun, policy: dict | None, tasks: list[dict], ledgers: list[str], archive: list[str]) -> None:
    limit = None
    if policy is not None:
        thresholds = (policy.get("budgets") or {}).get("tasks")
        if isinstance(thresholds, dict):
            limit = thresholds.get("max_active_tasks")
    closed = {"accepted", "superseded"}
    unresolved = [task for task in tasks if not task["valid"]]
    active = [task for task in tasks if task["valid"] and task["lifecycle"] not in closed]
    run.measurements["tasks"] = {
        "current_task_files": len(tasks),
        "active_tasks": len(active),
        "closed_tasks": len(tasks) - len(active) - len(unresolved),
        "legacy_tasks": len(unresolved),
        "review_ledgers": len(ledgers),
        "archive_files": len(archive),
    }
    if limit is None:
        return
    if unresolved:
        run.add(
            "budgets",
            "TASK_COUNT_UNRESOLVED",
            "warning",
            "vault/tasks",
            f"cannot verify budgets.tasks.max_active_tasks={limit}: {len(unresolved)} task file(s) have no valid trellium-task-state block",
        )
        return
    if len(active) > limit:
        run.add(
            "budgets",
            "BUDGET_EXCEEDED",
            "error",
            "vault/tasks",
            f"{len(active)} open task files exceed the configured limit max_active_tasks={limit}",
        )


def check_task_storage(run: VaultCheckRun, policy: dict | None, tasks: list[dict], ledgers: list[str], archive: list[str]) -> None:
    task_paths = [task["path"] for task in tasks] + ledgers + archive
    if not task_paths:
        return
    if not git_in_worktree(run.target):
        run.add("storage", "GIT_CHECK_SKIPPED", "warning", "vault/tasks", "not a Git worktree or Git is unavailable; TASK storage was not verified")
        return
    if policy is None:
        # POLICY_MISSING already reports the unresolved project strategy.
        return
    storage = policy.get("task_storage")
    tracked = git_tracked_files(run.target)
    if tracked is None:
        run.add("storage", "GIT_CHECK_SKIPPED", "warning", "vault/tasks", "git ls-files failed; TASK storage was not verified")
        return

    if storage == "local":
        for relative in task_paths:
            if relative in tracked:
                run.add(
                    "storage",
                    "TASK_STORAGE_MISMATCH",
                    "error",
                    relative,
                    f"task_storage=local but {relative} is tracked or staged in Git; remove it from the index as the project owner decided",
                    task_id=task_id_of(relative),
                )
        return

    ignored = git_ignored_files(run.target, task_paths)
    if ignored is None:
        run.add("storage", "GIT_CHECK_SKIPPED", "warning", "vault/tasks", "git check-ignore failed; TASK storage was not verified")
        return
    for relative in task_paths:
        if relative in ignored:
            run.add(
                "storage",
                "TASK_STORAGE_MISMATCH",
                "error",
                relative,
                f"task_storage=tracked but {relative} is Git-ignored",
                task_id=task_id_of(relative),
            )
    for relative in archive:
        if relative not in tracked:
            run.add(
                "storage",
                "TASK_STORAGE_MISMATCH",
                "error",
                relative,
                f"task_storage=tracked but archived task file {relative} is not tracked",
                task_id=task_id_of(relative),
            )
    closed = {"accepted", "superseded"}
    for task in tasks:
        if task["path"] in tracked:
            continue
        if task["legacy"] or not task["valid"]:
            reason = "legacy" if task["legacy"] else "its state block is invalid"
            run.add(
                "storage",
                "TASK_STORAGE_UNRESOLVED",
                "warning",
                task["path"],
                f"task_storage=tracked but {task['path']} is not tracked and its lifecycle is unresolved ({reason})",
                task_id=task["task_id"],
            )
        elif task["lifecycle"] in closed:
            run.add(
                "storage",
                "TASK_STORAGE_MISMATCH",
                "error",
                task["path"],
                f"task_storage=tracked but closed task ({task['lifecycle']}) {task['path']} is not tracked",
                task_id=task["task_id"],
            )
        else:
            run.add(
                "storage",
                "TASK_STORAGE_PENDING",
                "warning",
                task["path"],
                f"task_storage=tracked but {task['path']} is not tracked yet (allowed until the task is committed)",
                task_id=task["task_id"],
            )


def task_id_of(relative: str) -> str | None:
    match = TASK_FILE_ID_RE.match(Path(relative).name)
    return match.group(1) if match else None


def run_vault_checks(target: Path) -> VaultCheckRun:
    run = VaultCheckRun(target)
    if (target / "vault").is_symlink():
        run.add("required-files", "SYMLINK_INPUT", "error", "vault", "vault/ is a symbolic link; refusing to follow it")
        return run
    texts = check_required_files(run)
    policy = check_policy_block(run, texts.get("vault/index.md"))
    tasks, ledgers, archive = discover_task_files(run)
    check_runtime_projection(run, texts.get("vault/runtime.md"), tasks)
    measure_hot_files(run, texts)
    check_budgets(run, policy)
    check_task_budget(run, policy, tasks, ledgers, archive)
    check_task_storage(run, policy, tasks, ledgers, archive)
    return run


def render_check_text(run: VaultCheckRun) -> None:
    print(f"vault check: {run.target}")
    for finding in run.sorted_findings():
        task_suffix = f" [{finding['task_id']}]" if "task_id" in finding else ""
        print(f"  {finding['severity'].upper():<7} {finding['code']} {finding['path']}{task_suffix}: {finding['message']}")
    if run.measurements:
        print("measurements:")
        for key in sorted(run.measurements):
            parts = [f"{name}={value}" for name, value in run.measurements[key].items()]
            print(f"  {key}: {', '.join(parts)}")
    errors, warnings = len(run.errors), len(run.warnings)
    print(f"summary: {errors} error(s), {warnings} warning(s)")
    if errors:
        print("result: failed")
    elif warnings:
        print("result: passed with warnings")
    else:
        print("result: ok")


def check_project(args: argparse.Namespace) -> int:
    try:
        target = resolve_existing_target(args.target)
    except (AdoptionError, OSError) as exc:
        return fail(str(exc))
    if args.format not in ("text", "json"):
        return fail(f"unknown format: {args.format} (expected text or json)")
    if not (target / "vault").is_dir():
        return fail(f"target has no vault/ directory; run 'adopt' first: {target}")

    run = run_vault_checks(target)
    if args.format == "json":
        payload = {
            "schema_version": 1,
            "target": str(target),
            "summary": {"errors": len(run.errors), "warnings": len(run.warnings)},
            "findings": run.sorted_findings(),
            "measurements": run.measurements,
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        render_check_text(run)
    return CHECK_ERROR_EXIT if run.errors else 0



# --- Release fetching (--fetch) --------------------------------------------


def latest_release_tag() -> str:
    """Return the newest CalVer tag of the upstream repository."""
    request = urllib.request.Request(
        FETCH_TAGS_URL,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "trellium-fetch"},
    )
    with urllib.request.urlopen(request, timeout=FETCH_TIMEOUT_SECONDS) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, list):
        raise AdoptionError(f"unexpected tag listing from {FETCH_TAGS_URL}")
    candidates = []
    for entry in payload:
        if isinstance(entry, dict):
            name = str(entry.get("name", ""))
            if parse_version(name) is not None:
                candidates.append((parse_version(name), name))
    if not candidates:
        raise AdoptionError(f"no version tags found for {FETCH_REPOSITORY}; publish a tag first")
    # GitHub lists recently created tags first, but sort defensively anyway.
    return max(candidates)[1]


def safe_extract_tarball(tarball_path: Path, destination: Path) -> None:
    """Extract a release tarball while refusing anything but plain files and directories."""
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()
    with tarfile.open(tarball_path, "r:gz") as archive:
        for member in archive.getmembers():
            if member.issym() or member.islnk() or member.isdev():
                raise AdoptionError(f"refusing non-regular file in release tarball: {member.name}")
            target = (root / member.name).resolve()
            if not target.is_relative_to(root):
                raise AdoptionError(f"refusing path escape in release tarball: {member.name}")
        archive.extractall(destination)


def fetch_release_tree(tag: str) -> Path:
    """Return the extracted release tree for a tag, downloading it once."""
    destination = FETCH_CACHE_ROOT / tag
    if (
        (destination / FETCH_MARKER_NAME).is_file()
        and (destination / "scripts" / "trellium.py").is_file()
        and (destination / "init" / "VERSION").is_file()
    ):
        return destination

    FETCH_CACHE_ROOT.mkdir(parents=True, exist_ok=True)
    staging_tarball = FETCH_CACHE_ROOT / f".{tag}.{secrets.token_hex(8)}.tar.gz"
    staging_extract = FETCH_CACHE_ROOT / f".{tag}.extracting.{secrets.token_hex(8)}"
    try:
        request = urllib.request.Request(
            FETCH_TARBALL_TEMPLATE.format(tag=tag),
            headers={"User-Agent": "trellium-fetch"},
        )
        with urllib.request.urlopen(request, timeout=FETCH_TIMEOUT_SECONDS) as response, staging_tarball.open("wb") as handle:
            shutil.copyfileobj(response, handle)
        safe_extract_tarball(staging_tarball, staging_extract)
        entries = [child for child in staging_extract.iterdir()]
        if len(entries) != 1 or not entries[0].is_dir():
            raise AdoptionError(f"release tarball for {tag} has an unexpected layout")
        if destination.exists():
            shutil.rmtree(destination)
        entries[0].rename(destination)
        (destination / FETCH_MARKER_NAME).write_text(f"{tag}\n", encoding="utf-8")
    finally:
        if staging_tarball.exists():
            staging_tarball.unlink()
        if staging_extract.exists():
            shutil.rmtree(staging_extract)
    return destination


def fetch_and_run(args: argparse.Namespace, forwarded: list[str]) -> int:
    """Resolve the latest release and re-execute the fetched updater."""
    try:
        tag = latest_release_tag()
        release_dir = fetch_release_tree(tag)
        fetched_version = (release_dir / "init" / "VERSION").read_text(encoding="utf-8").strip()
    except (AdoptionError, OSError, ValueError, tarfile.TarError) as exc:
        return fail(
            f"could not fetch the latest release: {exc}; "
            "rerun without --fetch to use the bundled content"
        )

    target_value = getattr(args, "target", None)
    if target_value:
        try:
            target = Path(target_value).expanduser().resolve()
            stamp = read_stamp(target)
        except (AdoptionError, OSError, RuntimeError):
            stamp = None
        if stamp is not None:
            installed = parse_version(stamp.get("protocol_version"))
            fetched = parse_version(fetched_version)
            if installed is not None and fetched is not None and fetched < installed:
                return fail(
                    f"latest release {tag} ({fetched_version}) is older than the target's "
                    f"installed protocol {stamp.get('protocol_version')}; "
                    "rerun without --fetch to use the bundled content"
                )

    package_name = TEMPLATES_ROOT.parent.parent.name
    fetched_script = release_dir / "scripts" / "trellium.py"
    fetched_templates = release_dir / "skills" / package_name / "assets" / "templates"
    if not fetched_script.is_file() or not (fetched_templates / "AGENTS.md").is_file():
        return fail(f"release {tag} is missing the updater script or the {package_name} templates")

    command = [sys.executable, str(fetched_script), *forwarded, "--templates", str(fetched_templates)]
    print(f"fetch: using {FETCH_REPOSITORY} tag {tag} (protocol {fetched_version})")
    result = subprocess.run(command, check=False, text=True, capture_output=True)
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    return result.returncode


def git_dirty_paths(target: Path, relatives: list[str]) -> list[str]:
    if not (target / ".git").exists():
        return []
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "--", *relatives],
            cwd=target,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return []
    if result.returncode != 0:
        return []
    dirty = []
    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue
        dirty.append(line[3:].strip().strip('"'))
    return dirty


def selection_filter(args: argparse.Namespace):
    skip = set(args.skip or [])
    only = set(args.only or []) if args.only else None
    unknown = (skip | (only or set())) - set(FILE_ROLES)
    if unknown:
        raise AdoptionError(f"unknown paths in --only/--skip: {', '.join(sorted(unknown))}")

    def selected(relative: str) -> bool:
        if relative in skip:
            return False
        return only is None or relative in only

    return selected


def apply_protocol_file(
    target: Path,
    relative: str,
    role: str,
    force: bool,
    target_descriptor: int | None,
) -> str:
    if role == "marker":
        return update_agent_entry_region(target, target_descriptor)
    return copy_file(
        TEMPLATES_ROOT / relative,
        target / relative,
        target,
        force=force,
        dry_run=False,
        target_descriptor=target_descriptor,
    )


def update_agent_entry_region(target: Path, target_descriptor: int | None) -> str:
    new_region = upstream_marker_region()
    agents_path = target / "AGENTS.md"
    if target_descriptor is not None:
        with open_parent_directory(target_descriptor, Path("AGENTS.md"), create=True) as (
            parent_descriptor,
            name,
        ):
            metadata = output_metadata_at(parent_descriptor, name)
            if metadata is None:
                raise AdoptionError(f"agent entry file disappeared during upgrade: {agents_path}")
            validate_output_metadata(metadata, agents_path)
            current = read_text_at(parent_descriptor, name, agents_path)
            if marker_region(current) is None:
                raise AdoptionError(f"Trellium marker region missing in {agents_path}")
            atomic_write_text_at(
                parent_descriptor,
                name,
                replace_marker_region(current, new_region),
                stat.S_IMODE(metadata.st_mode),
            )
            return "updated"

    validate_output_paths(target, [agents_path])
    current = agents_path.read_text(encoding="utf-8")
    if marker_region(current) is None:
        raise AdoptionError(f"Trellium marker region missing in {agents_path}")
    atomic_write_text(agents_path, replace_marker_region(current, new_region))
    return "updated"


def remove_tracked_file(target: Path, relative: str, target_descriptor: int | None) -> None:
    if target_descriptor is not None:
        with open_parent_directory(target_descriptor, Path(relative), create=False) as (
            parent_descriptor,
            name,
        ):
            unlink_at_if_present(parent_descriptor, name)
        return
    try:
        (target / relative).unlink()
    except FileNotFoundError:
        pass


def backup_upgraded_file(
    target: Path,
    relative: str,
    version: str,
    target_descriptor: int | None,
) -> None:
    source = target / relative
    if not source.is_file():
        return
    backup = f"{BACKUP_DIRECTORY}/{version}/{relative}"
    copy_file(source, target / backup, target, force=True, dry_run=False, target_descriptor=target_descriptor)


def proposal_relative(version: str, relative: str) -> str:
    flattened = relative.replace("/", "__")
    return f"{PROPOSAL_DIRECTORY}/{version}/{flattened}.proposal.md"


def render_proposal(target: Path, version: str, item: dict) -> str:
    relative, role = item["path"], item["role"]
    reason = item.get("reason", "")
    if role == "marker":
        upstream_text = upstream_marker_region()
        try:
            local_text = marker_region((target / relative).read_text(encoding="utf-8")) or ""
        except OSError:
            local_text = ""
    else:
        upstream_text = (TEMPLATES_ROOT / relative).read_text(encoding="utf-8")
        try:
            local_text = (target / relative).read_text(encoding="utf-8")
        except OSError:
            local_text = ""
    diff = "\n".join(
        difflib.unified_diff(
            upstream_text.splitlines(),
            local_text.splitlines(),
            fromfile=f"upstream/{relative}",
            tofile=f"local/{relative}",
            lineterm="",
        )
    )
    return (
        f"# Upgrade Proposal - {version}\n\n"
        f"- File: `{relative}`\n"
        f"- Role: {role}\n"
        f"- Reason: {reason}\n\n"
        "The upstream template and the local file both changed. Merge the upstream\n"
        "version into the local file while preserving every local customization,\n"
        "then propose the result to the user. Project data is never at risk here,\n"
        "and the previous content stays recoverable through git.\n\n"
        f"## Upstream template\n\n````md\n{upstream_text.rstrip()}\n````\n\n"
        f"## Differences (upstream -> local)\n\n````diff\n{diff}\n````\n"
    )


def updated_stamp_after_apply(
    target: Path,
    stamp: dict,
    version: str,
    apply_items: list[dict],
    add_items: list[dict],
    remove_items: list[dict],
    conflict_items: list[dict],
    applied: dict[str, str],
) -> dict:
    files = {relative: dict(entry) for relative, entry in stamp["files"].items()}
    for item in (*apply_items, *add_items):
        relative, role = item["path"], item["role"]
        if applied.get(relative) == "skipped":
            continue
        baseline = upstream_hash_for_role(relative, role)
        if baseline is None:
            continue
        files[relative] = {"role": role, "baseline": baseline}
    for item in remove_items:
        files.pop(item["path"], None)
    for item in conflict_items:
        entry = files.get(item["path"])
        if entry is None:
            entry = {
                "role": item["role"],
                "baseline": local_hash_for_role(target, item["path"], item["role"]) or "",
            }
        # Remember which upstream revision the pending proposal merges in, so
        # a completed merge is recognized as absorbed instead of re-proposed.
        absorbed = upstream_hash_for_role(item["path"], item["role"])
        if absorbed is not None:
            entry["absorbed_upstream"] = absorbed
        entry["pending"] = True
        files[item["path"]] = entry
    updated = dict(stamp)
    updated["files"] = files
    updated["target_version"] = version
    if not conflict_items:
        updated["protocol_version"] = version
        updated["last_upgrade"] = date.today().isoformat()
        updated["trust"] = "versioned"
    return updated


def baseline_project(args: argparse.Namespace) -> int:
    try:
        target = resolve_existing_target(args.target)
        if not (target / "vault").is_dir():
            raise AdoptionError(
                f"target has no vault/ directory; run 'adopt' for new adoptions: {target}"
            )
        if read_stamp(target) is not None:
            raise AdoptionError(f"adoption stamp already exists: {stamp_path(target)}")
        files: dict[str, dict] = {}
        for relative, role in sorted(FILE_ROLES.items()):
            if relative == "AGENTS.md":
                try:
                    agents_text = (target / relative).read_text(encoding="utf-8")
                except OSError:
                    continue
                region = marker_region(agents_text)
                if region is not None:
                    files[relative] = {
                        "role": "marker",
                        "baseline": sha256_hex(region.encode("utf-8")),
                        "observed": True,
                    }
                else:
                    files[relative] = {
                        "role": "merge",
                        "baseline": sha256_hex(agents_text.encode("utf-8")),
                        "observed": True,
                    }
                continue
            baseline = local_hash_for_role(target, relative, role)
            if baseline is None:
                continue
            files[relative] = {"role": role, "baseline": baseline, "observed": True}
        stamp = {
            "schema_version": 1,
            "protocol_version": None,
            "adopted_at": None,
            "last_upgrade": None,
            "trust": "unversioned",
            "files": files,
        }
        descriptor = open_upgrade_descriptor(target)
        try:
            write_stamp_file(target, stamp, descriptor)
        finally:
            if descriptor is not None:
                os.close(descriptor)
    except (AdoptionError, OSError) as exc:
        return fail(str(exc))

    print(f"baseline recorded: {len(stamp['files'])} tracked file(s) at {target}")
    print("trust: unversioned -- upstream changes only produce proposals until the first upgrade completes")
    return 0


def diff_project(args: argparse.Namespace) -> int:
    try:
        target = resolve_existing_target(args.target)
        stamp = read_stamp(target)
        if stamp is None:
            raise AdoptionError(
                f"no adoption stamp found at {stamp_path(target)}; "
                "run 'adopt' for new adoptions or 'baseline' for an existing vault"
            )
        plan = build_upgrade_plan(target, stamp)
        print_upgrade_header(target, stamp)
        print_plan(plan)
        print_playbook(migrations_after(stamp.get("protocol_version")))
    except (AdoptionError, OSError) as exc:
        return fail(str(exc))
    return plan_exit_code(plan)


def complete_upgrade(target: Path, stamp: dict) -> int:
    entries = stamp["files"]
    pending = sorted(relative for relative, entry in entries.items() if entry.get("pending"))
    if not pending:
        return fail("no pending proposals to complete; run 'diff' to check the current state")
    for relative in pending:
        role = entries[relative].get("role", "merge")
        baseline = local_hash_for_role(target, relative, role)
        if baseline is None:
            return fail(f"pending file is missing: {relative}")
        entries[relative]["baseline"] = baseline
        entries[relative]["observed"] = True
        entries[relative]["pending"] = False
    try:
        version = read_protocol_version()
    except AdoptionError as exc:
        return fail(str(exc))
    stamp["protocol_version"] = version
    stamp["last_upgrade"] = date.today().isoformat()
    stamp["trust"] = "versioned"
    stamp.pop("target_version", None)
    try:
        descriptor = open_upgrade_descriptor(target)
        try:
            write_stamp_file(target, stamp, descriptor)
        finally:
            if descriptor is not None:
                os.close(descriptor)
    except (AdoptionError, OSError) as exc:
        return fail(str(exc))

    print(f"completed upgrade to {version}: {len(pending)} proposal file(s) finalized")
    for relative in pending:
        print(f"  - {relative}")
    print_playbook([section for section in read_migration_sections() if section[0] == version])
    print("next: commit this upgrade as a standalone, revertable change")
    return 0


def upgrade_project(args: argparse.Namespace) -> int:
    try:
        target = resolve_existing_target(args.target)
        stamp = read_stamp(target)
        if stamp is None:
            raise AdoptionError(
                f"no adoption stamp found at {stamp_path(target)}; "
                "run 'adopt' for new adoptions or 'baseline' for an existing vault"
            )
        version = read_protocol_version()
        plan = build_upgrade_plan(target, stamp)
        selected = selection_filter(args)
    except (AdoptionError, OSError) as exc:
        return fail(str(exc))

    if args.complete:
        return complete_upgrade(target, stamp)

    print_upgrade_header(target, stamp)
    print_plan(plan)
    print_playbook(migrations_after(stamp.get("protocol_version")))

    if not args.apply:
        print("dry run only; rerun with --apply to execute apply/add/remove; conflicts always produce proposals")
        return plan_exit_code(plan)

    apply_items = [item for item in plan["apply"] if selected(item["path"])]
    add_items = [item for item in plan["add"] if selected(item["path"])]
    remove_items = [item for item in plan["remove"] if selected(item["path"])]
    conflict_items = [item for item in plan["conflict"] if selected(item["path"])]

    if not (apply_items or add_items or remove_items or conflict_items):
        # A tooling-only release changes no files; still move the stamp
        # forward so the version pointer does not stick behind forever.
        if args.apply and stamp.get("trust") == "versioned" and stamp.get("protocol_version") != version:
            stamp["protocol_version"] = version
            stamp["last_upgrade"] = date.today().isoformat()
            descriptor = open_upgrade_descriptor(target)
            try:
                write_stamp_file(target, stamp, descriptor)
            finally:
                if descriptor is not None:
                    os.close(descriptor)
            print(f"recorded protocol version {version} (no file changes)")
        print("nothing to apply")
        return plan_exit_code(plan)

    touch_paths = [item["path"] for item in (*apply_items, *add_items, *remove_items)]
    dirty = git_dirty_paths(target, [*touch_paths, STAMP_RELATIVE])
    if dirty and not args.allow_dirty:
        return fail(
            "target has uncommitted changes in files the upgrade would touch: "
            + ", ".join(sorted(dirty))
            + "; commit or stash them first, or pass --allow-dirty"
        )

    try:
        for item in (*apply_items, *add_items, *remove_items, *conflict_items):
            assert_upgrade_writable(target, item["path"])
        destinations = [target / item["path"] for item in (*apply_items, *add_items)]
        proposals = [
            (proposal_relative(version, item["path"]), render_proposal(target, version, item))
            for item in conflict_items
        ]
    except (AdoptionError, OSError) as exc:
        return fail(str(exc))

    target_descriptor: int | None = None
    outcomes: list[tuple[str, str, str]] = []
    try:
        if ANCHORED_WRITES_SUPPORTED:
            target_descriptor = open_target_directory(target, create=False)
        if destinations:
            validate_output_paths(target, destinations)
        if not (target / ".git").exists():
            backup_version = stamp.get("protocol_version") or "unknown"
            for item in (*apply_items, *remove_items):
                backup_upgraded_file(target, item["path"], backup_version, target_descriptor)

        for item in (*apply_items, *add_items):
            relative, role = item["path"], item["role"]
            action = apply_protocol_file(
                target,
                relative,
                role,
                force=item in apply_items,
                target_descriptor=target_descriptor,
            )
            outcomes.append((relative, role, action))

        for item in remove_items:
            remove_tracked_file(target, item["path"], target_descriptor)
            outcomes.append((item["path"], item["role"], "removed"))

        for relative, content in proposals:
            write_text_file(
                target / relative,
                content,
                target,
                force=True,
                dry_run=False,
                target_descriptor=target_descriptor,
            )

        applied = {
            relative: action for relative, role, action in outcomes if action != "skipped"
        }
        stamp = updated_stamp_after_apply(
            target, stamp, version, apply_items, add_items, remove_items, conflict_items, applied
        )
        write_stamp_file(target, stamp, target_descriptor)
    except (AdoptionError, OSError, UnicodeError) as exc:
        return fail(f"upgrade stopped during a safe write; the target may contain partial changes: {exc}")
    finally:
        if target_descriptor is not None:
            os.close(target_descriptor)

    for relative, role, action in outcomes:
        print(f"{action} {relative}")
    for relative, _content in proposals:
        print(f"proposal {relative}")
    print()
    if conflict_items:
        print(
            f"next: resolve proposals under {target / PROPOSAL_DIRECTORY / version}, "
            "then run 'upgrade <target> --complete'"
        )
    else:
        print("next: commit this upgrade as a standalone, revertable change")
    return EXIT_CONFLICT if conflict_items else 0


def adopt_project(args: argparse.Namespace) -> int:
    try:
        target = Path(args.target).expanduser().resolve()
        target_exists = target.exists()
    except (OSError, RuntimeError) as exc:
        return fail(f"could not resolve adoption target: {exc}")

    if target == Path(target.anchor):
        return fail(f"refusing to adopt into filesystem root: {target}")
    if not target_exists and not args.create:
        return fail(f"target does not exist: {target}")
    try:
        if target_exists and not target.is_dir():
            return fail(f"target is not a directory: {target}")
    except OSError as exc:
        return fail(f"could not inspect adoption target: {exc}")

    if not TEMPLATES_ROOT.is_dir():
        return fail(f"template directory does not exist: {TEMPLATES_ROOT}")

    destinations = [target / "AGENTS.md"]
    destinations.extend(target / relative for relative in TEMPLATE_FILES)
    destinations.extend(target / relative for relative in RENDERED_FILES)

    target_descriptor: int | None = None
    if target_exists and not args.dry_run and ANCHORED_WRITES_SUPPORTED:
        try:
            target_descriptor = open_target_directory(target, create=False)
        except (AdoptionError, OSError) as exc:
            return fail(f"could not securely open adoption target: {exc}")

    try:
        validate_template_sources(("AGENTS.md", *TEMPLATE_FILES))
        validate_output_paths(target, destinations)
    except (AdoptionError, OSError, RuntimeError) as exc:
        if target_descriptor is not None:
            os.close(target_descriptor)
        return fail(str(exc))

    if not target_exists:
        print_action(args.dry_run, f"create directory {target}")
        if not args.dry_run:
            if ANCHORED_WRITES_SUPPORTED:
                try:
                    target_descriptor = open_target_directory(target, create=True)
                except (AdoptionError, OSError) as exc:
                    return fail(f"could not securely create adoption target: {exc}")
            else:
                try:
                    target.mkdir(parents=True)
                except OSError as exc:
                    return fail(f"could not create adoption target: {exc}")

    rendered_files = {
        "vault/project.md": render_project(target, target_descriptor),
        "vault/runtime.md": render_runtime(target),
    }

    changed: list[str] = []
    skipped: list[str] = []
    actions: dict[str, str] = {}
    try:
        agent_result = append_agent_entry(target, args.dry_run, target_descriptor)
        (changed if agent_result in {"create", "updated"} else skipped).append("AGENTS.md")
        actions["AGENTS.md"] = agent_result

        for relative in TEMPLATE_FILES:
            result = copy_file(
                TEMPLATES_ROOT / relative,
                target / relative,
                target,
                force=args.force,
                dry_run=args.dry_run,
                target_descriptor=target_descriptor,
            )
            (changed if result != "skipped" else skipped).append(relative)
            actions[relative] = result

        for relative, content in rendered_files.items():
            result = write_text_file(
                target / relative,
                content,
                target,
                force=args.force,
                dry_run=args.dry_run,
                target_descriptor=target_descriptor,
            )
            (changed if result != "skipped" else skipped).append(relative)
            actions[relative] = result

        if not args.dry_run:
            write_adoption_stamp(target, actions, rendered_files, target_descriptor)
    except (AdoptionError, OSError, UnicodeError) as exc:
        return fail(f"adoption stopped during a safe write; the target may contain partial changes: {exc}")
    finally:
        if target_descriptor is not None:
            os.close(target_descriptor)

    print()
    print(f"adoption target: {target}")
    print(f"changed: {len(changed)}")
    for item in changed:
        print(f"  - {item}")
    if skipped:
        print(f"skipped existing files: {len(skipped)}")
        for item in skipped:
            print(f"  - {item}")
    print("next: ask your Agent to read AGENTS.md, vault/index.md (cheat sheet), and vault/runtime.md; read vault/governance.md in full for Level B/C work")
    print("later upgrades: python3 trellium.py diff <target>")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Adopt Trellium into a target project.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    content_options = argparse.ArgumentParser(add_help=False)
    content_options.add_argument(
        "--templates", metavar="DIR", help="override the template directory (VERSION stays with the running script)"
    )
    content_options.add_argument(
        "--fetch",
        action="store_true",
        help="fetch the latest tagged release from GitHub and run it instead of the bundled content",
    )

    adopt = subparsers.add_parser(
        "adopt", help="add Agent collaboration files to a project", parents=[content_options]
    )
    adopt.add_argument("target", nargs="?", default=".", help="target project directory")
    adopt.add_argument("--create", action="store_true", help="create target directory if missing")
    adopt.add_argument("--force", action="store_true", help="replace existing generated files")
    adopt.add_argument("--dry-run", action="store_true", help="print actions without writing")
    adopt.set_defaults(func=adopt_project)

    baseline = subparsers.add_parser(
        "baseline", help="record an adoption stamp for an existing vault adopted before versioning"
    )
    baseline.add_argument("target", nargs="?", default=".", help="target project directory")
    baseline.set_defaults(func=baseline_project)

    report = subparsers.add_parser(
        "diff", help="report drift between an adopted project and the current templates", parents=[content_options]
    )
    report.add_argument("target", nargs="?", default=".", help="target project directory")
    report.set_defaults(func=diff_project)

    upgrade = subparsers.add_parser(
        "upgrade",
        help="refresh protocol files in an adopted project while preserving project data",
        parents=[content_options],
    )
    upgrade.add_argument("target", nargs="?", default=".", help="target project directory")
    upgrade.add_argument(
        "--apply", action="store_true", help="execute the safe subset (apply/add/remove); conflicts produce proposals"
    )
    upgrade.add_argument(
        "--complete", action="store_true", help="finalize proposals resolved by the agent and the user"
    )
    upgrade.add_argument(
        "--skip", action="append", default=[], metavar="PATH", help="exclude a path from this upgrade round"
    )
    upgrade.add_argument(
        "--only", action="append", default=[], metavar="PATH", help="restrict this upgrade round to the given paths"
    )
    upgrade.add_argument(
        "--allow-dirty", action="store_true", help="proceed even when files to touch have uncommitted changes"
    )
    upgrade.set_defaults(func=upgrade_project)

    check = subparsers.add_parser(
        "check",
        help="read-only validation of task state blocks, policy, runtime projection, budgets, and TASK storage",
    )
    check.add_argument("target", nargs="?", default=".", help="target project directory")
    check.add_argument(
        "--format",
        default="text",
        help="output format: text or json (default: text)",
    )
    check.set_defaults(func=check_project)

    return parser


def main(argv: list[str] | None = None) -> int:
    global TEMPLATES_ROOT
    arguments = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()
    args = parser.parse_args(arguments)
    original_templates_root = TEMPLATES_ROOT
    if getattr(args, "templates", None):
        TEMPLATES_ROOT = Path(args.templates).expanduser().resolve()
    try:
        if getattr(args, "fetch", False):
            forwarded = [argument for argument in arguments if argument != "--fetch"]
            return fetch_and_run(args, forwarded)
        return args.func(args)
    finally:
        # Keep repeated in-process invocations (tests) from inheriting the override.
        TEMPLATES_ROOT = original_templates_root


if __name__ == "__main__":
    raise SystemExit(main())
