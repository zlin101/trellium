#!/usr/bin/env python3
"""Adopt Agent Native Init assets into a target project."""

from __future__ import annotations

import argparse
import os
import secrets
import shutil
import stat
import sys
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Iterator


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / "skills"
TEMPLATES_ROOT = SKILLS_ROOT / "agent-native-init-zh" / "assets" / "templates"

TEMPLATE_FILES = (
    "vault/index.md",
    "vault/governance.md",
    "vault/decisions.md",
    "vault/handoff.md",
    "vault/collaboration.md",
    "vault/tasks/README.md",
    "skills/agent-task/SKILL.md",
)
RENDERED_FILES = ("vault/project.md", "vault/runtime.md")

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
                print_action(False, f"keep existing Agent Native Init entry in {agents_path}")
                return "skipped"

            section = agent_entry_section()
            print_action(False, f"append Agent Native Init entry to {agents_path}")
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
        print_action(dry_run, f"keep existing Agent Native Init entry in {agents_path}")
        return "skipped"

    section = agent_entry_section()

    print_action(dry_run, f"append Agent Native Init entry to {agents_path}")
    if not dry_run:
        atomic_write_text(agents_path, current.rstrip() + section + "\n")
    return "updated"


def agent_entry_section() -> str:
    return f"""

{AGENTS_MARKER_START}
## Agent Native Init

For non-trivial work, read these files before editing:

1. `vault/index.md`
2. `vault/runtime.md`
3. `vault/governance.md`

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
    try:
        agent_result = append_agent_entry(target, args.dry_run, target_descriptor)
        (changed if agent_result in {"create", "updated"} else skipped).append("AGENTS.md")

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
