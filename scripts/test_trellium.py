from __future__ import annotations

from contextlib import contextmanager, redirect_stderr, redirect_stdout
import importlib.util
from io import StringIO
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from typing import Iterator
from unittest.mock import patch


SCRIPT_PATH = Path(__file__).with_name("trellium.py")
SPEC = importlib.util.spec_from_file_location("agent_init", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {SCRIPT_PATH}")
agent_init = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(agent_init)


def state_block(payload: dict | None = None, *, text: str | None = None) -> str:
    body = text if text is not None else json.dumps(payload, indent=2)
    return f"<!-- trellium-task-state\n{body}\n-->"


def policy_block(payload: dict | None = None, *, text: str | None = None) -> str:
    body = text if text is not None else json.dumps(payload, indent=2)
    return f"<!-- trellium-policy\n{body}\n-->"


def tracked_policy() -> str:
    return policy_block({"schema_version": 1, "task_storage": "tracked"})


def local_policy() -> str:
    return policy_block({"schema_version": 1, "task_storage": "local"})


def valid_state(task_id: str = "TASK-0001", lifecycle: str = "draft", **overrides) -> dict:
    payload = {
        "schema_version": 1,
        "task_id": task_id,
        "level": "B",
        "authority_level": 2,
        "lifecycle": lifecycle,
    }
    payload.update(overrides)
    for key, value in list(payload.items()):
        if value is None:
            del payload[key]
    return payload


def build_runtime(
    rows: tuple[tuple[str, str, str], ...] = (),
    focus: str = "ADOPTION",
    recent: tuple[str, ...] = ("did a thing",),
) -> str:
    lines = [
        "# Runtime Context",
        "",
        "## Focus",
        "",
        f"- {focus}",
        "",
        "## Active Tasks",
        "",
        "| Task | Objective | Status | Next Action |",
        "| --- | --- | --- | --- |",
    ]
    for task_id, status, _objective in rows:
        lines.append(f"| {task_id} | one-line objective | {status} | next action |")
    lines += ["", "## Recent Changes", ""]
    lines += [f"- {item}" for item in recent]
    return "\n".join(lines) + "\n"


class TargetTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def run_agent_init(self, *arguments: str) -> tuple[int, str, str]:
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = agent_init.main(list(arguments))
        return code, out.getvalue(), err.getvalue()

    @staticmethod
    def snapshot(root: Path) -> dict[str, bytes]:
        return {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted(root.rglob("*"))
            if path.is_file()
        }

    def adopt(self, target: Path, *extra: str) -> tuple[int, str, str]:
        return self.run_agent_init("adopt", str(target), *extra)

    def read_stamp(self, target: Path) -> dict:
        return json.loads(
            (target / agent_init.STAMP_RELATIVE).read_text(encoding="utf-8")
        )

    @contextmanager
    def patched_templates(self) -> Iterator[Path]:
        templates = self.root / "templates"
        shutil.copytree(agent_init.TEMPLATES_ROOT, templates, dirs_exist_ok=True)
        with patch.object(agent_init, "TEMPLATES_ROOT", templates):
            yield templates


class AgentInitTest(TargetTestCase):
    def test_adopt_creates_expected_files_and_is_idempotent(self) -> None:
        target = self.root / "project"
        target.mkdir()
        (target / "README.md").write_text("# Demo\n\nA demo project.\n", encoding="utf-8")

        code, _, err = self.adopt(target)

        self.assertEqual(code, 0, err)
        expected = {
            "AGENTS.md",
            "README.md",
            "skills/agent-task/SKILL.md",
            "vault/.agent-init.json",
            "vault/collaboration.md",
            "vault/decisions.md",
            "vault/governance.md",
            "vault/handoff.md",
            "vault/index.md",
            "vault/parked.md",
            "vault/project.md",
            "vault/runtime.md",
            "vault/tasks/README.md",
        }
        first_snapshot = self.snapshot(target)
        self.assertEqual(set(first_snapshot), expected)
        self.assertIn("vault/index.md", first_snapshot["AGENTS.md"].decode("utf-8"))

        code, out, err = self.run_agent_init("adopt", str(target))

        self.assertEqual(code, 0, err)
        self.assertEqual(self.snapshot(target), first_snapshot)
        self.assertIn("changed: 0", out)

    def test_dry_run_with_create_does_not_write_anything(self) -> None:
        target = self.root / "new-project"

        code, _, err = self.run_agent_init("adopt", str(target), "--create", "--dry-run")

        self.assertEqual(code, 0, err)
        self.assertFalse(target.exists())

    def test_create_builds_missing_target_safely(self) -> None:
        target = self.root / "nested/new-project"

        code, _, err = self.run_agent_init("adopt", str(target), "--create")

        self.assertEqual(code, 0, err)
        self.assertTrue((target / "AGENTS.md").is_file())
        self.assertTrue((target / "vault/runtime.md").is_file())

    def test_rejects_filesystem_root_target(self) -> None:
        filesystem_root = Path(self.root.anchor)

        code, _, err = self.run_agent_init("adopt", str(filesystem_root), "--dry-run")

        self.assertEqual(code, 1)
        self.assertIn("filesystem root", err)

    def test_adopt_uses_portable_fallback_without_dir_fd_support(self) -> None:
        target = self.root / "project"
        target.mkdir()

        with patch.object(agent_init, "ANCHORED_WRITES_SUPPORTED", False):
            code, _, err = self.run_agent_init("adopt", str(target))

        self.assertEqual(code, 0, err)
        self.assertTrue((target / "AGENTS.md").is_file())
        self.assertTrue((target / "vault/runtime.md").is_file())

    @unittest.skipUnless(
        agent_init.ANCHORED_WRITES_SUPPORTED,
        "requires anchored write support",
    )
    def test_write_error_returns_partial_state_warning(self) -> None:
        target = self.root / "project"
        target.mkdir()

        with patch.object(agent_init, "atomic_copy_file_at", side_effect=OSError("disk full")):
            code, _, err = self.run_agent_init("adopt", str(target))

        self.assertEqual(code, 1)
        self.assertIn("partial changes", err)
        self.assertIn("disk full", err)

    def test_adopt_appends_existing_agents_entry_once(self) -> None:
        target = self.root / "project"
        target.mkdir()
        agents_path = target / "AGENTS.md"
        agents_path.write_text("# Existing Rules\n\nKeep this section.\n", encoding="utf-8")

        code, _, err = self.run_agent_init("adopt", str(target))

        self.assertEqual(code, 0, err)
        first_content = agents_path.read_text(encoding="utf-8")
        self.assertIn("Keep this section.", first_content)
        self.assertEqual(first_content.count(agent_init.AGENTS_MARKER_START), 1)

        code, _, err = self.run_agent_init("adopt", str(target))

        self.assertEqual(code, 0, err)
        self.assertEqual(agents_path.read_text(encoding="utf-8"), first_content)

    def test_force_replaces_existing_generated_files(self) -> None:
        target = self.root / "project"
        target.mkdir()
        code, _, err = self.run_agent_init("adopt", str(target))
        self.assertEqual(code, 0, err)

        governance = target / "vault/governance.md"
        runtime = target / "vault/runtime.md"
        governance.write_text("custom governance\n", encoding="utf-8")
        runtime.write_text("custom runtime\n", encoding="utf-8")

        code, _, err = self.run_agent_init("adopt", str(target), "--force")

        self.assertEqual(code, 0, err)
        self.assertEqual(
            governance.read_bytes(),
            (agent_init.TEMPLATES_ROOT / "vault/governance.md").read_bytes(),
        )
        self.assertNotEqual(runtime.read_text(encoding="utf-8"), "custom runtime\n")

    def test_force_rejects_symlinked_vault_before_any_write(self) -> None:
        target = self.root / "project"
        outside = self.root / "outside"
        target.mkdir()
        outside.mkdir()
        sentinel = outside / "governance.md"
        sentinel.write_text("do not replace\n", encoding="utf-8")
        (target / "vault").symlink_to(outside, target_is_directory=True)

        code, _, _ = self.run_agent_init("adopt", str(target), "--force")

        self.assertEqual(code, 1)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "do not replace\n")
        self.assertFalse((target / "AGENTS.md").exists())
        self.assertFalse((target / "skills").exists())
        self.assertEqual(self.snapshot(outside), {"governance.md": b"do not replace\n"})

    def test_rejects_symlinked_agents_file_before_any_write(self) -> None:
        target = self.root / "project"
        outside = self.root / "outside"
        target.mkdir()
        outside.mkdir()
        sentinel = outside / "AGENTS.md"
        sentinel.write_text("external rules\n", encoding="utf-8")
        (target / "AGENTS.md").symlink_to(sentinel)

        code, _, _ = self.run_agent_init("adopt", str(target))

        self.assertEqual(code, 1)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "external rules\n")
        self.assertFalse((target / "vault").exists())
        self.assertFalse((target / "skills").exists())

    def test_rejects_hard_linked_agents_file_before_any_write(self) -> None:
        target = self.root / "project"
        outside = self.root / "outside"
        target.mkdir()
        outside.mkdir()
        sentinel = outside / "AGENTS.md"
        sentinel.write_text("external rules\n", encoding="utf-8")
        agents_path = target / "AGENTS.md"
        os.link(sentinel, agents_path)
        self.assertEqual(sentinel.stat().st_ino, agents_path.stat().st_ino)

        code, _, err = self.run_agent_init("adopt", str(target))

        self.assertEqual(code, 1)
        self.assertRegex(err.lower(), r"hard link|multiple links|link count")
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "external rules\n")
        self.assertFalse((target / "vault").exists())
        self.assertFalse((target / "skills").exists())

    def test_rejects_symlinked_skills_directory_before_any_write(self) -> None:
        target = self.root / "project"
        outside = self.root / "outside"
        target.mkdir()
        outside.mkdir()
        (target / "skills").symlink_to(outside, target_is_directory=True)

        code, _, _ = self.run_agent_init("adopt", str(target))

        self.assertEqual(code, 1)
        self.assertFalse((target / "AGENTS.md").exists())
        self.assertFalse((target / "vault").exists())
        self.assertEqual(self.snapshot(outside), {})

    @unittest.skipUnless(
        agent_init.ANCHORED_WRITES_SUPPORTED,
        "requires dir_fd and O_NOFOLLOW support",
    )
    def test_rejects_parent_symlink_added_after_preflight(self) -> None:
        target = self.root / "project"
        outside = self.root / "outside"
        target.mkdir()
        outside.mkdir()
        original_append = agent_init.append_agent_entry

        def append_then_swap(*args: object, **kwargs: object) -> str:
            result = original_append(*args, **kwargs)
            (target / "vault").symlink_to(outside, target_is_directory=True)
            return result

        with patch.object(agent_init, "append_agent_entry", side_effect=append_then_swap):
            code, _, err = self.run_agent_init("adopt", str(target))

        self.assertEqual(code, 1)
        self.assertIn("safe write", err)
        self.assertEqual(self.snapshot(outside), {})

    @unittest.skipUnless(
        agent_init.ANCHORED_WRITES_SUPPORTED,
        "requires dir_fd and O_NOFOLLOW support",
    )
    def test_keeps_original_target_when_ancestor_is_swapped_after_open(self) -> None:
        container = self.root / "container"
        target = container / "project"
        redirected = self.root / "redirected"
        redirected_target = redirected / "project"
        moved_container = self.root / "original-container"
        target.mkdir(parents=True)
        redirected_target.mkdir(parents=True)
        original_validate = agent_init.validate_output_paths

        def validate_then_redirect(*args: object, **kwargs: object) -> None:
            original_validate(*args, **kwargs)
            container.rename(moved_container)
            container.symlink_to(redirected, target_is_directory=True)

        with patch.object(
            agent_init,
            "validate_output_paths",
            side_effect=validate_then_redirect,
        ):
            code, _, err = self.run_agent_init("adopt", str(target))

        self.assertEqual(code, 0, err)
        self.assertTrue((moved_container / "project/AGENTS.md").is_file())
        self.assertFalse((redirected_target / "AGENTS.md").exists())

    def test_does_not_copy_content_from_symlinked_readme(self) -> None:
        target = self.root / "project"
        outside = self.root / "outside.env"
        target.mkdir()
        outside.write_text("TOKEN=outside-secret\n", encoding="utf-8")
        (target / "README.md").symlink_to(outside)

        code, _, err = self.run_agent_init("adopt", str(target))

        self.assertEqual(code, 0, err)
        project = (target / "vault/project.md").read_text(encoding="utf-8")
        self.assertNotIn("outside-secret", project)
        self.assertIn("project project.", project)

    def test_does_not_copy_content_from_hard_linked_readme(self) -> None:
        target = self.root / "project"
        outside = self.root / "outside.env"
        target.mkdir()
        outside.write_text("TOKEN=outside-secret\n", encoding="utf-8")
        os.link(outside, target / "README.md")

        code, _, err = self.run_agent_init("adopt", str(target))

        self.assertEqual(code, 0, err)
        project = (target / "vault/project.md").read_text(encoding="utf-8")
        self.assertNotIn("outside-secret", project)
        self.assertIn("project project.", project)


class UpgradeMechanismTest(TargetTestCase):
    def make_adopted_target(self) -> Path:
        target = self.root / "project"
        target.mkdir()
        code, _, err = self.adopt(target)
        self.assertEqual(code, 0, err)
        return target

    def test_file_roles_cover_every_adopted_file(self) -> None:
        self.assertEqual(
            set(agent_init.FILE_ROLES),
            set(agent_init.TEMPLATE_FILES) | set(agent_init.RENDERED_FILES) | {"AGENTS.md"},
        )
        self.assertEqual(agent_init.WRITABLE_ROLES, {"marker", "merge", "template"})
        for relative, role in agent_init.FILE_ROLES.items():
            self.assertIn(role, agent_init.WRITABLE_ROLES | {"data"}, relative)

    def test_adopt_writes_stamp_with_roles_and_hashes(self) -> None:
        target = self.make_adopted_target()

        stamp = self.read_stamp(target)

        self.assertEqual(stamp["protocol_version"], agent_init.read_protocol_version())
        self.assertEqual(stamp["trust"], "versioned")
        self.assertEqual(stamp["schema_version"], 1)
        self.assertEqual(set(stamp["files"]), set(agent_init.FILE_ROLES))
        for relative, entry in stamp["files"].items():
            expected_role = "merge" if relative == "AGENTS.md" else agent_init.FILE_ROLES[relative]
            self.assertEqual(entry["role"], expected_role)
        for relative in agent_init.TEMPLATE_FILES:
            expected = agent_init.sha256_hex((target / relative).read_bytes())
            self.assertEqual(stamp["files"][relative]["baseline"], expected)

    def test_diff_reports_in_sync_after_adopt(self) -> None:
        target = self.make_adopted_target()

        code, out, err = self.run_agent_init("diff", str(target))

        self.assertEqual(code, 0, err)
        self.assertIn("in_sync", out)
        self.assertIn("protected", out)

    def test_upgrade_preserves_local_edits_and_data_files(self) -> None:
        target = self.make_adopted_target()
        (target / "vault/runtime.md").write_text("# Evolved runtime\n", encoding="utf-8")
        (target / "vault/decisions.md").write_text("D-0001 keep this decision\n", encoding="utf-8")
        governance = (target / "vault/governance.md").read_text(encoding="utf-8")
        (target / "vault/governance.md").write_text(
            governance + "\n## Project Rules\n\n- Keep this local rule.\n", encoding="utf-8"
        )

        with self.patched_templates() as templates:
            (templates / "vault/index.md").write_text("new index template\n", encoding="utf-8")
            (templates / "vault/governance.md").write_text("new governance template\n", encoding="utf-8")
            code, out, err = self.run_agent_init("upgrade", str(target), "--apply")

        self.assertEqual(code, agent_init.EXIT_CONFLICT, err)
        self.assertEqual((target / "vault/index.md").read_text(encoding="utf-8"), "new index template\n")
        self.assertIn("Keep this local rule.", (target / "vault/governance.md").read_text(encoding="utf-8"))
        self.assertEqual((target / "vault/runtime.md").read_text(encoding="utf-8"), "# Evolved runtime\n")
        self.assertIn(
            "D-0001 keep this decision", (target / "vault/decisions.md").read_text(encoding="utf-8")
        )

        version = agent_init.read_protocol_version()
        proposals = list((target / "vault/.upgrade" / version).glob("*.proposal.md"))
        self.assertEqual([path.name for path in proposals], ["vault__governance.md.proposal.md"])
        proposal_text = proposals[0].read_text(encoding="utf-8")
        self.assertIn("new governance template", proposal_text)
        self.assertIn("Keep this local rule.", proposal_text)

        stamp = self.read_stamp(target)
        self.assertEqual(
            stamp["files"]["vault/index.md"]["baseline"],
            agent_init.sha256_hex(b"new index template\n"),
        )
        self.assertTrue(stamp["files"]["vault/governance.md"]["pending"])

    def test_upgrade_complete_marks_merged_files_observed(self) -> None:
        target = self.make_adopted_target()
        (target / "vault/governance.md").write_text("locally modified governance\n", encoding="utf-8")
        with self.patched_templates() as templates:
            (templates / "vault/governance.md").write_text("new governance template\n", encoding="utf-8")
            code, _, err = self.run_agent_init("upgrade", str(target), "--apply")
        self.assertEqual(code, agent_init.EXIT_CONFLICT, err)

        merged = "new governance template\nmerged with local edits\n"
        (target / "vault/governance.md").write_text(merged, encoding="utf-8")

        code, out, err = self.run_agent_init("upgrade", str(target), "--complete")

        self.assertEqual(code, 0, err)
        version = agent_init.read_protocol_version()
        stamp = self.read_stamp(target)
        entry = stamp["files"]["vault/governance.md"]
        self.assertFalse(entry["pending"])
        self.assertTrue(entry["observed"])
        self.assertEqual(entry["baseline"], agent_init.sha256_hex(merged.encode("utf-8")))
        self.assertEqual(stamp["protocol_version"], version)
        self.assertEqual(stamp["trust"], "versioned")

        # A merged file is user-owned: the next upstream change must propose,
        # never auto-replace.
        with self.patched_templates() as templates:
            (templates / "vault/governance.md").write_text("newer governance template\n", encoding="utf-8")
            code, out, err = self.run_agent_init("diff", str(target))
        self.assertEqual(code, agent_init.EXIT_CONFLICT, err)
        self.assertIn("conflict", out)
        self.assertEqual(
            (target / "vault/governance.md").read_text(encoding="utf-8"), merged
        )

        # The same upstream revision the merge already absorbed stays quiet.
        with self.patched_templates() as templates:
            (templates / "vault/governance.md").write_text("new governance template\n", encoding="utf-8")
            code, out, err = self.run_agent_init("diff", str(target))
        self.assertEqual(code, 0, err)
        self.assertIn("already absorbed", out)

    def test_upgrade_replaces_marker_region_and_keeps_user_content(self) -> None:
        # The marker flavor appears when adopt appends a section to an
        # existing user-owned AGENTS.md.
        target = self.root / "project"
        target.mkdir()
        agents_path = target / "AGENTS.md"
        agents_path.write_text("# Project Rules\n\nOwned by the project.\n", encoding="utf-8")
        code, _, err = self.adopt(target)
        self.assertEqual(code, 0, err)
        self.assertEqual(agents_path.read_text(encoding="utf-8").count(agent_init.AGENTS_MARKER_START), 1)

        def refreshed_section() -> str:
            return (
                f"{agent_init.AGENTS_MARKER_START}\n## Trellium\n\n"
                f"Refreshed entry text.\n{agent_init.AGENTS_MARKER_END}\n"
            )

        with patch.object(agent_init, "agent_entry_section", refreshed_section):
            code, _, err = self.run_agent_init("upgrade", str(target), "--apply")

        self.assertEqual(code, 0, err)
        text = agents_path.read_text(encoding="utf-8")
        self.assertIn("Owned by the project.", text)
        self.assertIn("Refreshed entry text.", text)
        self.assertEqual(text.count(agent_init.AGENTS_MARKER_START), 1)

        # A locally modified marker region is a conflict, not an auto-replace.
        text = agents_path.read_text(encoding="utf-8")
        marker_end = text.find(agent_init.AGENTS_MARKER_END)
        agents_path.write_text(
            text[:marker_end] + "- local note inside the region\n" + text[marker_end:], encoding="utf-8"
        )

        def newer_section() -> str:
            return (
                f"{agent_init.AGENTS_MARKER_START}\n## Trellium\n\n"
                f"Newer entry text.\n{agent_init.AGENTS_MARKER_END}\n"
            )

        with patch.object(agent_init, "agent_entry_section", newer_section):
            code, _, err = self.run_agent_init("upgrade", str(target), "--apply")

        self.assertEqual(code, agent_init.EXIT_CONFLICT, err)
        text = agents_path.read_text(encoding="utf-8")
        self.assertIn("- local note inside the region", text)
        self.assertNotIn("Newer entry text.", text)

    def test_upgrade_refuses_dirty_git_state(self) -> None:
        if shutil.which("git") is None:
            self.skipTest("requires git")
        target = self.make_adopted_target()
        subprocess.run(["git", "init", "-q"], cwd=target, check=True)

        with self.patched_templates() as templates:
            (templates / "vault/index.md").write_text("new index template\n", encoding="utf-8")
            code, _, err = self.run_agent_init("upgrade", str(target), "--apply")
            self.assertEqual(code, 1)
            self.assertIn("uncommitted changes", err)
            self.assertNotEqual(
                (target / "vault/index.md").read_text(encoding="utf-8"), "new index template\n"
            )

            subprocess.run(["git", "add", "-A"], cwd=target, check=True)
            subprocess.run(
                ["git", "-c", "user.name=test", "-c", "user.email=test@example.com", "commit", "-qm", "adopt"],
                cwd=target,
                check=True,
            )
            code, _, err = self.run_agent_init("upgrade", str(target), "--apply")

        self.assertEqual(code, 0, err)
        self.assertEqual((target / "vault/index.md").read_text(encoding="utf-8"), "new index template\n")

    def test_baseline_unversioned_upgrades_conflict_only(self) -> None:
        target = self.make_adopted_target()
        (target / agent_init.STAMP_RELATIVE).unlink()
        (target / "vault/index.md").write_text("legacy local index\n", encoding="utf-8")

        code, _, err = self.run_agent_init("diff", str(target))
        self.assertEqual(code, 1)
        self.assertIn("baseline", err)

        code, _, err = self.run_agent_init("baseline", str(target))
        self.assertEqual(code, 0, err)
        stamp = self.read_stamp(target)
        self.assertEqual(stamp["trust"], "unversioned")
        self.assertIsNone(stamp["protocol_version"])
        self.assertTrue(stamp["files"]["vault/index.md"]["observed"])

        code, _, err = self.run_agent_init("baseline", str(target))
        self.assertEqual(code, 1)
        self.assertIn("already exists", err)

        with self.patched_templates() as templates:
            (templates / "vault/index.md").write_text("new upstream index\n", encoding="utf-8")
            code, _, err = self.run_agent_init("upgrade", str(target), "--apply")

        self.assertEqual(code, agent_init.EXIT_CONFLICT, err)
        self.assertEqual((target / "vault/index.md").read_text(encoding="utf-8"), "legacy local index\n")
        self.assertTrue(list((target / "vault/.upgrade").rglob("*.proposal.md")))

    def test_write_scope_guard_rejects_project_data(self) -> None:
        target = self.root / "project"
        (target / "vault").mkdir(parents=True)
        (target / "vault/runtime.md").write_text("# Runtime\n", encoding="utf-8")

        for relative in (
            "vault/runtime.md",  # existing project data
            "vault/tasks/TASK-0001.md",
            "vault/decisions/D-0001-x.md",
            "src/app.py",
        ):
            with self.assertRaises(agent_init.AdoptionError):
                agent_init.assert_upgrade_writable(target, relative)

        for relative in (
            "AGENTS.md",
            "vault/index.md",
            "vault/governance.md",
            "vault/tasks/README.md",
            "skills/agent-task/SKILL.md",
        ):
            agent_init.assert_upgrade_writable(target, relative)

        # Creating an absent data-role starter is allowed.
        with patch.dict(agent_init.FILE_ROLES, {"vault/parked.md": "data"}):
            agent_init.assert_upgrade_writable(target, "vault/parked.md")

        agent_init.assert_upgrade_writable(target, agent_init.STAMP_RELATIVE)
        agent_init.assert_upgrade_writable(target, "vault/.upgrade/2026.08.0/vault__index.md.proposal.md")
        agent_init.assert_upgrade_writable(target, ".agent-init-backup/2026.08.0/vault/index.md")

    def test_upgrade_skip_leaves_file_untouched(self) -> None:
        target = self.make_adopted_target()

        with self.patched_templates() as templates:
            (templates / "vault/index.md").write_text("new index template\n", encoding="utf-8")
            code, _, err = self.run_agent_init(
                "upgrade", str(target), "--apply", "--skip", "vault/index.md"
            )

        self.assertEqual(code, agent_init.EXIT_ACTIONABLE, err)
        self.assertNotEqual(
            (target / "vault/index.md").read_text(encoding="utf-8"), "new index template\n"
        )
        stamp = self.read_stamp(target)
        self.assertEqual(
            stamp["files"]["vault/index.md"]["baseline"],
            agent_init.sha256_hex((agent_init.TEMPLATES_ROOT / "vault/index.md").read_bytes()),
        )

    def test_diff_lists_pending_migration_playbook(self) -> None:
        target = self.make_adopted_target()
        stamp = self.read_stamp(target)
        stamp["protocol_version"] = "2025.01.0"
        (target / agent_init.STAMP_RELATIVE).write_text(
            json.dumps(stamp, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

        code, out, err = self.run_agent_init("diff", str(target))

        self.assertEqual(code, 0, err)
        self.assertIn("migration playbook", out)
        self.assertIn(agent_init.read_protocol_version(), out)

    def test_adopt_fails_without_version_file(self) -> None:
        target = self.root / "project"
        target.mkdir()

        with patch.object(agent_init, "VERSION_FILE", self.root / "missing-VERSION"):
            code, _, err = self.adopt(target)

        self.assertEqual(code, 1)
        self.assertIn("version file", err)

    def test_upgrade_backfills_new_data_file_for_older_adoption(self) -> None:
        # A project adopted at 2026.08.0 has no parked.md and no stamp entry
        # for it; the 2026.09.0 template set backfills it as a data-role add.
        target = self.make_adopted_target()
        (target / "vault/parked.md").unlink()
        stamp = self.read_stamp(target)
        stamp["files"].pop("vault/parked.md", None)
        (target / agent_init.STAMP_RELATIVE).write_text(
            json.dumps(stamp, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

        code, out, err = self.run_agent_init("diff", str(target))
        self.assertEqual(code, agent_init.EXIT_ACTIONABLE, err)
        self.assertIn("+ vault/parked.md", out)

        code, _, err = self.run_agent_init("upgrade", str(target), "--apply")
        self.assertEqual(code, 0, err)

        self.assertTrue((target / "vault/parked.md").is_file())
        entry = self.read_stamp(target)["files"]["vault/parked.md"]
        self.assertEqual(entry["role"], "data")
        code, out, err = self.run_agent_init("diff", str(target))
        self.assertEqual(code, 0, err)
        self.assertIn("x vault/parked.md", out)


class EmbeddedSkillLayoutTest(TargetTestCase):
    @staticmethod
    def load_module(script_path: Path, name: str):
        spec = importlib.util.spec_from_file_location(name, script_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"cannot load {script_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_repo_layout_detection(self) -> None:
        self.assertFalse(agent_init.SKILL_LAYOUT)
        self.assertEqual(
            agent_init.TEMPLATES_ROOT,
            agent_init.SCRIPT_DIRECTORY.parent / "skills" / "trellium-zh" / "assets" / "templates",
        )

    def test_embedded_packages_install_their_own_locale(self) -> None:
        repo_zh_package = agent_init.TEMPLATES_ROOT.parents[1]
        repo_en_package = repo_zh_package.parent / "trellium"
        for package, locale_marker in ((repo_zh_package, "替换为"), (repo_en_package, "replace with")):
            with self.subTest(package=package.name):
                copied = self.root / package.name
                shutil.copytree(package, copied)
                embedded = self.load_module(copied / "assets" / "trellium.py", f"embedded_{package.name}")

                self.assertTrue(embedded.SKILL_LAYOUT)
                self.assertEqual(embedded.TEMPLATES_ROOT, (copied / "assets" / "templates").resolve())
                self.assertTrue(embedded.VERSION_FILE.is_file())
                self.assertTrue(embedded.MIGRATIONS_FILE.is_file())

                target = self.root / f"target-{package.name}"
                target.mkdir()
                code, _, err = self.run_agent_init_module(embedded, "adopt", str(target))
                self.assertEqual(code, 0, err)
                handoff = (target / "vault/handoff.md").read_text(encoding="utf-8")
                self.assertIn(locale_marker, handoff)
                runtime = (target / "vault/runtime.md").read_text(encoding="utf-8")
                self.assertIn("## Active Tasks", runtime)
                self.assertIn("Trellium adoption recorded", runtime)

                stamp = json.loads(
                    (target / embedded.STAMP_RELATIVE).read_text(encoding="utf-8")
                )
                self.assertEqual(stamp["protocol_version"], embedded.read_protocol_version())

    def test_embedded_check_passes_on_fresh_adoption(self) -> None:
        # The shipped templates must be check-clean: a fresh adoption in both
        # skill packages validates policy/state/template consistency.
        repo_zh_package = agent_init.TEMPLATES_ROOT.parents[1]
        for package_name in (repo_zh_package.name, "trellium"):
            package_root = repo_zh_package.parent / package_name
            with self.subTest(package=package_name):
                copied = self.root / f"check-{package_name}"
                shutil.copytree(package_root, copied)
                embedded = self.load_module(copied / "assets" / "trellium.py", f"embedded_check_{package_name}")

                target = self.root / f"check-target-{package_name}"
                target.mkdir()
                code, _, err = self.run_agent_init_module(embedded, "adopt", str(target))
                self.assertEqual(code, 0, err)

                out, err2 = StringIO(), StringIO()
                with redirect_stdout(out), redirect_stderr(err2):
                    check_code = embedded.main(["check", str(target), "--format", "json"])
                self.assertEqual(check_code, 0, out.getvalue())
                payload = json.loads(out.getvalue())
                self.assertEqual(payload["summary"]["errors"], 0, payload["findings"])
                self.assertIsNotNone(payload["measurements"].get("runtime"))

    @staticmethod
    def run_agent_init_module(module, *arguments: str) -> tuple[int, str, str]:
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = module.main(list(arguments))
        return code, out.getvalue(), err.getvalue()

    def test_embedded_upgrade_uses_package_version(self) -> None:
        repo_zh_package = agent_init.TEMPLATES_ROOT.parents[1]
        copied = self.root / "trellium-zh"
        shutil.copytree(repo_zh_package, copied)
        embedded = self.load_module(copied / "assets" / "trellium.py", "embedded_upgrade")

        target = self.root / "project"
        target.mkdir()
        code, _, err = self.run_agent_init_module(embedded, "adopt", str(target))
        self.assertEqual(code, 0, err)

        # Upstream drift inside the package's own templates must be detected
        # by the embedded script without any repo paths.
        with patch.object(embedded, "TEMPLATES_ROOT", copied / "assets" / "templates") as patcher:
            (copied / "assets" / "templates" / "vault" / "index.md").write_text(
                "package-updated index\n", encoding="utf-8"
            )
            code, out, err = self.run_agent_init_module(embedded, "diff", str(target))
            self.assertEqual(code, embedded.EXIT_ACTIONABLE, err)
            self.assertIn("~ vault/index.md", out)
            code, _, err = self.run_agent_init_module(embedded, "upgrade", str(target), "--apply")
            self.assertEqual(code, 0, err)
        self.assertEqual(
            (target / "vault/index.md").read_text(encoding="utf-8"), "package-updated index\n"
        )


class FetchTest(TargetTestCase):
    def build_release_tree(self, version: str, index_text: str | None = None) -> Path:
        release = self.root / "releases" / version
        (release / "scripts").mkdir(parents=True)
        shutil.copy(SCRIPT_PATH, release / "scripts" / "trellium.py")
        (release / "init").mkdir()
        (release / "init" / "VERSION").write_text(f"{version}\n", encoding="utf-8")
        (release / "init" / "MIGRATIONS.md").write_text(
            f"# Migrations\n\n## {version} — test\n\n- test entry\n", encoding="utf-8"
        )
        templates = release / "skills" / "trellium-zh" / "assets" / "templates"
        shutil.copytree(agent_init.TEMPLATES_ROOT, templates)
        if index_text is not None:
            (templates / "vault" / "index.md").write_text(index_text, encoding="utf-8")
        return release

    def test_fetch_runs_fetched_release_end_to_end(self) -> None:
        target = self.root / "project"
        target.mkdir()
        code, _, err = self.adopt(target)
        self.assertEqual(code, 0, err)
        release = self.build_release_tree("9999.0.0", index_text="fetched index template\n")

        with patch.object(agent_init, "latest_release_tag", return_value="9999.0.0"), patch.object(
            agent_init, "fetch_release_tree", return_value=release
        ):
            code, out, err = self.run_agent_init("diff", str(target), "--fetch")

        self.assertEqual(code, agent_init.EXIT_ACTIONABLE, err)
        self.assertIn("fetch: using zlin101/trellium tag 9999.0.0", out)
        self.assertIn("available: 9999.0.0", out)
        self.assertIn("~ vault/index.md", out)

        with patch.object(agent_init, "latest_release_tag", return_value="9999.0.0"), patch.object(
            agent_init, "fetch_release_tree", return_value=release
        ):
            code, out, err = self.run_agent_init("upgrade", str(target), "--fetch", "--apply")

        self.assertEqual(code, 0, err)
        self.assertEqual((target / "vault/index.md").read_text(encoding="utf-8"), "fetched index template\n")
        stamp = self.read_stamp(target)
        self.assertEqual(stamp["protocol_version"], "9999.0.0")

    def test_upgrade_applies_version_pointer_on_tooling_release(self) -> None:
        # A release with no file changes must still advance the stamp so the
        # version pointer does not stick behind the latest release.
        target = self.root / "project"
        target.mkdir()
        code, _, err = self.adopt(target)
        self.assertEqual(code, 0, err)
        stamp = self.read_stamp(target)
        stamp["protocol_version"] = "2026.09.0"
        (target / agent_init.STAMP_RELATIVE).write_text(
            json.dumps(stamp, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        self.assertNotEqual(agent_init.read_protocol_version(), "2026.09.0")

        code, out, err = self.run_agent_init("upgrade", str(target), "--apply")

        self.assertEqual(code, 0, err)
        self.assertIn("recorded protocol version", out)
        updated = self.read_stamp(target)
        self.assertEqual(updated["protocol_version"], agent_init.read_protocol_version())

    def test_fetch_refuses_downgrade(self) -> None:
        target = self.root / "project"
        target.mkdir()
        code, _, err = self.adopt(target)
        self.assertEqual(code, 0, err)
        release = self.build_release_tree("2025.01.0")

        with patch.object(agent_init, "latest_release_tag", return_value="2025.01.0"), patch.object(
            agent_init, "fetch_release_tree", return_value=release
        ):
            code, _, err = self.run_agent_init("diff", str(target), "--fetch")

        self.assertEqual(code, 1)
        self.assertIn("older than", err)

    def test_templates_flag_overrides_without_fetch(self) -> None:
        target = self.root / "project"
        target.mkdir()
        code, _, err = self.adopt(target)
        self.assertEqual(code, 0, err)
        release = self.build_release_tree("9999.0.0", index_text="overridden index template\n")

        code, out, err = self.run_agent_init(
            "diff", str(target), "--templates", str(release / "skills" / "trellium-zh" / "assets" / "templates")
        )

        self.assertEqual(code, agent_init.EXIT_ACTIONABLE, err)
        self.assertIn("~ vault/index.md", out)

    def test_safe_extract_rejects_traversal_and_links(self) -> None:
        import io
        import tarfile

        def write_tar(path: Path, member_name: str, symlink: bool = False) -> None:
            with tarfile.open(path, "w:gz") as archive:
                if symlink:
                    info = tarfile.TarInfo(member_name)
                    info.type = tarfile.SYMTYPE
                    info.linkname = "/etc/passwd"
                    archive.addfile(info)
                else:
                    payload = b"evil"
                    info = tarfile.TarInfo(member_name)
                    info.size = len(payload)
                    archive.addfile(info, io.BytesIO(payload))

        tarball = self.root / "evil-traversal.tar.gz"
        write_tar(tarball, "../evil.txt")
        with self.assertRaises(agent_init.AdoptionError):
            agent_init.safe_extract_tarball(tarball, self.root / "extract-a")

        tarball = self.root / "evil-symlink.tar.gz"
        write_tar(tarball, "link", symlink=True)
        with self.assertRaises(agent_init.AdoptionError):
            agent_init.safe_extract_tarball(tarball, self.root / "extract-b")


class RenderedContentTest(unittest.TestCase):
    def test_agent_entry_section_levels_governance_reading(self) -> None:
        section = agent_init.agent_entry_section()
        self.assertIn("cheat sheet", section)
        self.assertIn("Level B or Level C", section)
        self.assertNotIn("3. `vault/governance.md`", section)


class VaultCheckTest(TargetTestCase):
    def make_project(
        self,
        *,
        index: str | None = None,
        runtime: str | None = None,
        handoff: str | None = None,
        decisions: str | None = None,
        parked: str | None = None,
        files: dict[str, str] | None = None,
        policy: str | None = None,
    ) -> Path:
        count = getattr(self, "_project_count", 0) + 1
        self._project_count = count
        name = "project" if count == 1 else f"project-{count}"
        target = self.root / name
        (target / "vault" / "tasks").mkdir(parents=True, exist_ok=True)
        if index is None:
            index = "# Vault Index\n\n" + (policy if policy is not None else tracked_policy()) + "\n\nRouting text.\n"
        (target / "vault/index.md").write_text(index, encoding="utf-8")
        (target / "vault/runtime.md").write_text(
            runtime if runtime is not None else build_runtime(), encoding="utf-8"
        )
        (target / "vault/handoff.md").write_text(
            handoff if handoff is not None else "# Handoff\n\n## TASK-0001 - 2026-01-01\n\n- Objective: x\n", encoding="utf-8"
        )
        (target / "vault/decisions.md").write_text(
            decisions if decisions is not None else "# Decisions\n\n- D-0001 · title · Active · essence · 2026-01-01\n", encoding="utf-8"
        )
        (target / "vault/parked.md").write_text(
            parked if parked is not None else "# Parked\n\n## Entries\n\n- P-0001 · task · title · context · trigger · 2026-01-01\n", encoding="utf-8"
        )
        for relative, content in (files or {}).items():
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content, encoding="utf-8")
        return target

    def check(self, target: Path, *extra: str) -> tuple[int, str, str]:
        return self.run_agent_init("check", str(target), *extra)

    def check_json(self, target: Path, *extra: str) -> dict:
        code, out, err = self.check(target, "--format", "json", *extra)
        self.assertIn(code, (0, agent_init.CHECK_ERROR_EXIT), err)
        return json.loads(out)

    def codes(self, payload: dict) -> list[str]:
        return [finding["code"] for finding in payload["findings"]]

    def test_valid_project_passes_with_zero_findings(self) -> None:
        target = self.make_project(
            files={"vault/tasks/TASK-0001-short-title.md": (
                "# TASK-0001 - Short Title\n\n" + state_block(valid_state()) + "\n\n## Objective\n\nWork.\n"
            )},
            runtime=build_runtime(rows=(("TASK-0001", "draft", "obj"),), focus="TASK-0001"),
        )

        code, out, err = self.check(target)
        self.assertEqual(code, 0, err)
        self.assertIn("passed with warnings", out)
        self.assertIn("GIT_CHECK_SKIPPED", out)

        payload = self.check_json(target)
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["summary"], {"errors": 0, "warnings": 1})
        self.assertEqual(self.codes(payload), ["GIT_CHECK_SKIPPED"])
        self.assertIn("runtime", payload["measurements"])
        self.assertIn("tasks", payload["measurements"])
        self.assertEqual(payload["measurements"]["tasks"]["current_task_files"], 1)

    def test_field_order_and_whitespace_do_not_matter(self) -> None:
        block = state_block(text='{ "lifecycle":"draft" ,\n"authority_level":2,\n "schema_version":1, "task_id":"TASK-0001", "level":"B" }')
        target = self.make_project(
            files={"vault/tasks/TASK-0001-a.md": f"# TASK-0001 - A\n\n{block}\n"},
        )

        payload = self.check_json(target)

        self.assertEqual(payload["summary"]["errors"], 0)

    def test_missing_policy_is_legacy_warning_without_hidden_defaults(self) -> None:
        target = self.make_project(
            policy="",
            runtime=build_runtime(recent=tuple(f"item {i}" for i in range(30))),
        )

        code, out, err = self.check(target)

        self.assertEqual(code, 0, err)
        self.assertIn("POLICY_MISSING", out)
        self.assertIn("passed with warnings", out)
        self.assertNotIn("BUDGET_EXCEEDED", out)

        payload = self.check_json(target)
        self.assertEqual(payload["summary"], {"errors": 0, "warnings": 1})
        self.assertEqual(self.codes(payload), ["POLICY_MISSING"])

    def test_policy_schema_violations_are_errors(self) -> None:
        cases = {
            "unknown-field": policy_block({"schema_version": 1, "task_storage": "tracked", "extra": True}),
            "bad-storage": policy_block({"schema_version": 1, "task_storage": "hybrid"}),
            "bad-schema-version": policy_block({"schema_version": 2, "task_storage": "tracked"}),
            "bool-schema-version": policy_block(text='{"schema_version": true, "task_storage": "tracked"}'),
            "trailing-comma": policy_block(text='{"schema_version": 1, "task_storage": "tracked",}'),
            "negative-budget": policy_block({
                "schema_version": 1,
                "task_storage": "tracked",
                "budgets": {"runtime": {"max_lines": -5}},
            }),
            "unknown-budget-key": policy_block({
                "schema_version": 1,
                "task_storage": "tracked",
                "budgets": {"runtime": {"max_bytes": 100}},
            }),
            "unknown-budget-file": policy_block({
                "schema_version": 1,
                "task_storage": "tracked",
                "budgets": {"misc": {"max_lines": 100}},
            }),
        }
        for name, index in cases.items():
            with self.subTest(case=name):
                target = self.make_project(index="# Vault Index\n\n" + index + "\n")
                code, out, err = self.check(target)
                self.assertEqual(code, 2, out)
                self.assertIn("POLICY_INVALID", out)

    def test_duplicate_policy_blocks_are_invalid(self) -> None:
        index = "# Vault Index\n\n" + tracked_policy() + "\n" + tracked_policy() + "\n"
        target = self.make_project(index=index)

        code, out, err = self.check(target)

        self.assertEqual(code, 2)
        self.assertIn("POLICY_INVALID", out)

    def test_legacy_task_without_state_block_is_unresolved_warning(self) -> None:
        target = self.make_project(
            files={"vault/tasks/TASK-0002-legacy.md": "# TASK-0002 - Legacy\n\n## Status\n\nActive\n"},
            runtime=build_runtime(rows=(("TASK-0002", "active", "obj"),)),
        )

        code, out, err = self.check(target)

        self.assertEqual(code, 0, err)
        self.assertIn("TASK_STATE_MISSING", out)
        self.assertIn("TASK_RUNTIME_UNRESOLVED", out)
        self.assertNotIn("TASK_RUNTIME_DRIFT", out)

        payload = self.check_json(target)
        self.assertEqual(
            sorted(self.codes(payload)),
            ["GIT_CHECK_SKIPPED", "TASK_RUNTIME_UNRESOLVED", "TASK_STATE_MISSING"],
        )
        self.assertEqual(payload["measurements"]["tasks"]["legacy_tasks"], 1)

    def test_state_block_violations_are_errors(self) -> None:
        base = {"schema_version": 1, "task_id": "TASK-0001", "level": "B", "authority_level": 2, "lifecycle": "draft"}
        cases = {
            "unknown-field": dict(base, surprise=1),
            "bad-lifecycle": dict(base, lifecycle="waiting-review"),
            "bad-level": dict(base, level="A"),
            "authority-out-of-range": dict(base, authority_level=5),
            "authority-bool": None,  # handled with raw text below
            "string-schema-version": None,
            "bad-task-id": dict(base, task_id="TASK-1"),
            "not-an-object": None,
        }
        raw_cases = {
            "authority-bool": '{ "schema_version": 1, "task_id": "TASK-0001", "level": "B", "authority_level": true, "lifecycle": "draft" }',
            "string-schema-version": '{ "schema_version": "1", "task_id": "TASK-0001", "level": "B", "authority_level": 2, "lifecycle": "draft" }',
            "not-an-object": '["TASK-0001"]',
        }
        for name, payload in cases.items():
            if payload is None:
                continue
            with self.subTest(case=name):
                target = self.make_project(
                    files={"vault/tasks/TASK-0001-x.md": "# TASK-0001 - X\n\n" + state_block(payload) + "\n"}
                )
                code, out, err = self.check(target)
                self.assertEqual(code, 2, out)
                self.assertIn("TASK_STATE_INVALID", out)
        for name, text in raw_cases.items():
            with self.subTest(case=name):
                target = self.make_project(
                    files={"vault/tasks/TASK-0001-x.md": "# TASK-0001 - X\n\n" + state_block(text=text) + "\n"}
                )
                code, out, err = self.check(target)
                self.assertEqual(code, 2, out)
                self.assertIn("TASK_STATE_INVALID", out)

    def test_duplicate_state_blocks_are_invalid(self) -> None:
        target = self.make_project(
            files={"vault/tasks/TASK-0001-x.md": (
                "# TASK-0001 - X\n\n" + state_block(valid_state()) + "\n" + state_block(valid_state()) + "\n"
            )}
        )

        code, out, err = self.check(target)

        self.assertEqual(code, 2)
        self.assertIn("TASK_STATE_DUPLICATE", out)

    def test_unterminated_state_block_is_invalid(self) -> None:
        target = self.make_project(
            files={"vault/tasks/TASK-0001-x.md": "# TASK-0001 - X\n\n<!-- trellium-task-state\n{ \"broken\": true }\n"},
        )

        code, out, err = self.check(target)

        self.assertEqual(code, 2)
        self.assertIn("TASK_STATE_INVALID", out)

    def test_task_id_must_match_file_name(self) -> None:
        target = self.make_project(
            files={"vault/tasks/TASK-0001-a.md": "# TASK-0001 - A\n\n" + state_block(valid_state(task_id="TASK-0002")) + "\n"}
        )

        code, out, err = self.check(target)

        self.assertEqual(code, 2)
        self.assertIn("TASK_ID_MISMATCH", out)

    def test_optional_state_fields_are_validated(self) -> None:
        good = valid_state(current_slice="A4", gates={"design": "passed", "live": "not_authorized"})
        target = self.make_project(
            files={"vault/tasks/TASK-0001-x.md": "# TASK-0001 - X\n\n" + state_block(good) + "\n"}
        )
        payload = self.check_json(target)
        self.assertEqual(payload["summary"], {"errors": 0, "warnings": 1})
        self.assertEqual(self.codes(payload), ["GIT_CHECK_SKIPPED"])

        bad_gate = valid_state(gates={"design": "approved"})
        target = self.make_project(
            files={"vault/tasks/TASK-0001-x.md": "# TASK-0001 - X\n\n" + state_block(bad_gate) + "\n"}
        )
        code, out, err = self.check(target)
        self.assertEqual(code, 2)
        self.assertIn("TASK_STATE_INVALID", out)

    def test_runtime_projection_drift_and_dangling_pointers(self) -> None:
        target = self.make_project(
            files={"vault/tasks/TASK-0001-a.md": "# TASK-0001 - A\n\n" + state_block(valid_state(lifecycle="draft")) + "\n"},
            runtime=build_runtime(
                rows=(
                    ("TASK-0001", "active", "drifted status"),
                    ("TASK-0042", "draft", "missing file"),
                    ("TASK-BAD", "draft", "malformed id"),
                ),
                focus="TASK-0099",
            ),
        )

        code, out, err = self.check(target)

        self.assertEqual(code, 2)
        self.assertIn("TASK_RUNTIME_DRIFT", out)
        self.assertIn("TASK_RUNTIME_MISSING", out)
        self.assertIn("TASK_RUNTIME_INVALID", out)
        payload = self.check_json(target)
        self.assertIn("TASK_RUNTIME_MISSING", self.codes(payload))

    def test_level_a_inline_rows_are_not_flagged(self) -> None:
        target = self.make_project(
            runtime=build_runtime(rows=(("ADOPTION", "active", "inline level A row"),)),
        )

        payload = self.check_json(target)

        self.assertEqual(payload["summary"], {"errors": 0, "warnings": 0})
    def test_budget_thresholds_require_explicit_policy(self) -> None:
        long_runtime = build_runtime(recent=tuple(f"item {i}" for i in range(30)))
        target = self.make_project(runtime=long_runtime)
        payload = self.check_json(target)
        self.assertEqual(payload["summary"]["errors"], 0)
        self.assertGreaterEqual(payload["measurements"]["runtime"]["lines"], 30)

        strict = policy_block({
            "schema_version": 1,
            "task_storage": "tracked",
            "budgets": {"runtime": {"max_lines": 5, "max_recent_entries": 2}},
        })
        target = self.make_project(index="# Vault Index\n\n" + strict + "\n", runtime=long_runtime)
        code, out, err = self.check(target)
        self.assertEqual(code, 2)
        self.assertIn("BUDGET_EXCEEDED", out)

    def test_max_active_tasks_with_legacy_files_is_unresolved(self) -> None:
        policy = policy_block({
            "schema_version": 1,
            "task_storage": "tracked",
            "budgets": {"tasks": {"max_active_tasks": 1}},
        })
        target = self.make_project(
            index="# Vault Index\n\n" + policy + "\n",
            files={
                "vault/tasks/TASK-0001-a.md": "# TASK-0001 - A\n\n" + state_block(valid_state(lifecycle="active")) + "\n",
                "vault/tasks/TASK-0002-legacy.md": "# TASK-0002 - Legacy\n",
            },
        )

        code, out, err = self.check(target)

        self.assertEqual(code, 0, err)
        self.assertIn("TASK_COUNT_UNRESOLVED", out)

    def test_max_active_tasks_is_enforced_when_resolvable(self) -> None:
        policy = policy_block({
            "schema_version": 1,
            "task_storage": "tracked",
            "budgets": {"tasks": {"max_active_tasks": 1}},
        })
        target = self.make_project(
            index="# Vault Index\n\n" + policy + "\n",
            files={
                "vault/tasks/TASK-0001-a.md": "# TASK-0001 - A\n\n" + state_block(valid_state(lifecycle="active")) + "\n",
                "vault/tasks/TASK-0002-b.md": "# TASK-0002 - B\n\n" + state_block(valid_state(task_id="TASK-0002", lifecycle="accepted")) + "\n",
                "vault/tasks/TASK-0003-c.md": "# TASK-0003 - C\n\n" + state_block(valid_state(task_id="TASK-0003", lifecycle="active")) + "\n",
            },
        )

        code, out, err = self.check(target)

        self.assertEqual(code, 2)
        self.assertIn("BUDGET_EXCEEDED", out)

    def test_review_ledgers_and_archive_are_cold_history(self) -> None:
        target = self.make_project(
            files={
                "vault/tasks/TASK-0001-review.md": "# TASK-0001 - Review Ledger\n\n## Findings\n",
                "vault/tasks/archive/TASK-0002-old.md": "# TASK-0002 - Old\n",
            },
        )

        code, out, err = self.check(target)
        self.assertEqual(code, 0, err)
        self.assertNotIn("TASK_STATE_MISSING", out)

        payload = self.check_json(target)
        self.assertEqual(payload["measurements"]["tasks"]["review_ledgers"], 1)
        self.assertEqual(payload["measurements"]["tasks"]["archive_files"], 1)
        self.assertEqual(payload["measurements"]["tasks"]["current_task_files"], 0)

    def init_git_repo(self, target: Path) -> None:
        subprocess.run(["git", "init", "-q"], cwd=target, check=True)
        subprocess.run(["git", "config", "user.name", "test"], cwd=target, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=target, check=True)

    def git(self, target: Path, *arguments: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", *arguments], cwd=target, check=False, capture_output=True)

    def test_storage_tracked_mode(self) -> None:
        files = {
            "vault/tasks/TASK-0001-active.md": "# TASK-0001 - Active\n\n" + state_block(valid_state(lifecycle="active")) + "\n",
            "vault/tasks/TASK-0002-done.md": "# TASK-0002 - Done\n\n" + state_block(valid_state(task_id="TASK-0002", lifecycle="accepted")) + "\n",
            "vault/tasks/archive/TASK-0003-old.md": "# TASK-0003 - Old\n",
        }
        target = self.make_project(files=files)
        self.init_git_repo(target)
        self.git(target, "add", "-A")
        self.git(target, "commit", "-qm", "base")

        code, out, err = self.check(target)
        self.assertEqual(code, 0, err)
        self.assertNotIn("TASK_STORAGE_MISMATCH", out)

        # An uncommitted new active task is a normal window: warning only.
        new_task = target / "vault/tasks/TASK-0004-new.md"
        new_task.write_text("# TASK-0004 - New\n\n" + state_block(valid_state(task_id="TASK-0004")) + "\n", encoding="utf-8")
        code, out, err = self.check(target)
        self.assertEqual(code, 0, err)
        self.assertNotIn("TASK_STORAGE_MISMATCH", out)

        # A closed (accepted) task that is not tracked is an error.
        done_path = target / "vault/tasks/TASK-0005-done.md"
        done_path.write_text("# TASK-0005 - Done\n\n" + state_block(valid_state(task_id="TASK-0005", lifecycle="accepted")) + "\n", encoding="utf-8")
        code, out, err = self.check(target)
        self.assertEqual(code, 2)
        self.assertIn("TASK_STORAGE_MISMATCH", out)
        done_path.unlink()

        # An untracked task file matched by .gitignore is an error: it would
        # silently stay local while the project policy says tracked. (Tracked
        # files are never reported by check-ignore; the index wins.)
        ignored_task = target / "vault/tasks/TASK-0006-ignored.md"
        ignored_task.write_text("# TASK-0006 - Ignored\n\n" + state_block(valid_state(task_id="TASK-0006")) + "\n", encoding="utf-8")
        (target / ".gitignore").write_text("vault/tasks/TASK-0006-ignored.md\n", encoding="utf-8")
        code, out, err = self.check(target)
        self.assertEqual(code, 2)
        self.assertIn("TASK_STORAGE_MISMATCH", out)
        self.assertIn("TASK-0006-ignored.md", out)

    def test_storage_local_mode_rejects_tracked_tasks(self) -> None:
        target = self.make_project(
            policy=local_policy(),
            files={"vault/tasks/TASK-0001-quiet.md": "# TASK-0001 - Quiet\n\n" + state_block(valid_state()) + "\n"},
        )
        self.init_git_repo(target)

        # Not tracked yet: no storage finding.
        code, out, err = self.check(target)
        self.assertEqual(code, 0, err)

        self.git(target, "add", "-A")
        code, out, err = self.check(target)
        self.assertEqual(code, 2)
        self.assertIn("TASK_STORAGE_MISMATCH", out)

    def test_storage_handles_unicode_and_space_file_names(self) -> None:
        name = "TASK-0007-我的 任务.md"
        target = self.make_project(
            policy=local_policy(),
            files={f"vault/tasks/{name}": f"# TASK-0007 - Unicode\n\n{state_block(valid_state(task_id='TASK-0007'))}\n"},
        )
        self.init_git_repo(target)
        self.git(target, "add", "-A")

        code, out, err = self.check(target)
        self.assertEqual(code, 2)
        self.assertIn("TASK_STORAGE_MISMATCH", out)
        self.assertIn(name, out)

    def test_storage_check_skipped_without_git(self) -> None:
        # A task file exists, so storage could not be verified: skipped warning.
        target = self.make_project(
            files={"vault/tasks/TASK-0001-a.md": "# TASK-0001 - A\n\n" + state_block(valid_state()) + "\n"},
        )

        code, out, err = self.check(target)

        self.assertEqual(code, 0, err)
        self.assertIn("GIT_CHECK_SKIPPED", out)
        self.assertNotIn("storage ok", out)

    def test_symlinked_task_input_is_not_followed(self) -> None:
        outside = self.root / "outside"
        outside.mkdir()
        secret = outside / "TASK-0001-real.md"
        secret.write_text("# TASK-0001 - Real\n\nOUTSIDE-SECRET-CONTENT\n", encoding="utf-8")
        target = self.make_project()
        (target / "vault/tasks/TASK-0001-link.md").symlink_to(secret)

        code, out, err = self.check(target)

        self.assertEqual(code, 2)
        self.assertIn("SYMLINK_INPUT", out)
        self.assertNotIn("OUTSIDE-SECRET-CONTENT", out)

    def test_symlinked_vault_is_not_followed(self) -> None:
        outside = self.root / "outside-vault"
        outside.mkdir()
        (outside / "index.md").write_text("OUTSIDE-INDEX-CONTENT\n", encoding="utf-8")
        target = self.root / "project"
        target.mkdir()
        (target / "vault").symlink_to(outside, target_is_directory=True)

        code, out, err = self.check(target)

        self.assertEqual(code, 2)
        self.assertIn("SYMLINK_INPUT", out)
        self.assertNotIn("OUTSIDE-INDEX-CONTENT", out)

    def test_symlinked_tasks_directory_is_not_followed(self) -> None:
        outside = self.root / "outside-tasks"
        outside.mkdir()
        block = state_block(text='{ "schema_version": 1, "task_id": "TASK-0500", "level": "B", "authority_level": 2, "lifecycle": "draft", "zzz_external_marker_field": 1 }')
        (outside / "TASK-0500-secret.md").write_text(f"# TASK-0500 - Secret\n\n{block}\nOUTSIDE-SECRET-CONTENT\n", encoding="utf-8")
        target = self.make_project()
        (target / "vault/tasks").rmdir()
        (target / "vault/tasks").symlink_to(outside, target_is_directory=True)

        code, out, err = self.check(target)
        self.assertEqual(code, 2)
        self.assertIn("SYMLINK_INPUT", out)
        self.assertNotIn("OUTSIDE-SECRET-CONTENT", out)
        self.assertNotIn("zzz_external_marker_field", out)
        self.assertNotIn("TASK-0500-secret.md", out.replace("vault/tasks is a symbolic link", ""))

        payload = self.check_json(target)
        self.assertEqual(payload["measurements"]["tasks"]["current_task_files"], 0)

    def test_symlinked_ledger_and_archive_are_errors(self) -> None:
        outside = self.root / "outside-archive"
        outside.mkdir()
        (outside / "TASK-0600-old.md").write_text("# TASK-0600 - Old\n", encoding="utf-8")
        target = self.make_project(
            files={"vault/tasks/TASK-0001-review.md": "# TASK-0001 - Review Ledger\n"},
        )
        (target / "vault/tasks/TASK-0001-review.md").unlink()
        (target / "vault/tasks/TASK-0001-review.md").symlink_to(outside / "TASK-0600-old.md")
        (target / "vault/tasks/archive").symlink_to(outside, target_is_directory=True)

        code, out, err = self.check(target)

        self.assertEqual(code, 2)
        self.assertIn("SYMLINK_INPUT", out)

    def test_prefix_marker_lookalike_is_not_a_block(self) -> None:
        index = "# Vault Index\n\n" + tracked_policy() + "\n\n<!-- trellium-policy-history\nsome archived notes\n-->\n"
        target = self.make_project(index=index)

        payload = self.check_json(target)

        self.assertEqual(payload["summary"]["errors"], 0)

    def test_duplicate_json_keys_are_rejected(self) -> None:
        target = self.make_project(
            files={"vault/tasks/TASK-0001-x.md": "# TASK-0001 - X\n\n" + state_block(
                text='{ "schema_version": 1, "task_id": "TASK-0001", "level": "B", "authority_level": 2, "lifecycle": "draft", "lifecycle": "accepted" }'
            ) + "\n"}
        )

        code, out, err = self.check(target)

        self.assertEqual(code, 2)
        self.assertIn("TASK_STATE_INVALID", out)

    def test_check_is_read_only_and_deterministic(self) -> None:
        target = self.make_project(
            files={"vault/tasks/TASK-0001-a.md": "# TASK-0001 - A\n\n" + state_block(valid_state()) + "\n"},
            runtime=build_runtime(rows=(("TASK-0001", "active", "drift"),)),
        )
        self.init_git_repo(target)
        self.git(target, "add", "-A")
        before_snapshot = self.snapshot(target)
        before_status = self.git(target, "status", "--porcelain").stdout

        results = []
        for _ in range(3):
            code, out, _err = self.check(target, "--format", "json")
            self.assertEqual(code, 2)
            payload = json.loads(out)
            payload.pop("target")
            results.append(payload)

        self.assertEqual(results[0], results[1])
        self.assertEqual(results[1], results[2])
        self.assertEqual(before_snapshot, self.snapshot(target))
        self.assertEqual(before_status, self.git(target, "status", "--porcelain").stdout)

    def test_json_output_shape_is_stable(self) -> None:
        target = self.make_project(
            files={"vault/tasks/TASK-0001-a.md": "# TASK-0001 - A\n\n" + state_block(valid_state()) + "\n"},
            runtime=build_runtime(rows=(("TASK-0001", "active", "drift"),)),
        )

        _, out, _ = self.check(target, "--format", "json")
        payload = json.loads(out)

        self.assertEqual(
            set(payload),
            {"schema_version", "target", "summary", "findings", "measurements"},
        )
        for finding in payload["findings"]:
            self.assertLessEqual(
                {"code", "severity", "path", "message"} - set(finding),
                set(),
            )
            self.assertLessEqual(
                set(finding) - {"code", "severity", "path", "message", "task_id"},
                set(),
            )
        self.assertEqual(
            [(f["code"], f["severity"]) for f in payload["findings"]],
            [("TASK_RUNTIME_DRIFT", "error"), ("GIT_CHECK_SKIPPED", "warning")],
        )

    def test_check_requires_existing_target_with_vault(self) -> None:
        code, _, err = self.check(self.root / "missing")
        self.assertEqual(code, 1)
        self.assertIn("existing directory", err)

        empty = self.root / "empty"
        empty.mkdir()
        code, _, err = self.check(empty)
        self.assertEqual(code, 1)
        self.assertIn("vault", err)

    def test_check_rejects_unknown_format(self) -> None:
        target = self.make_project()

        code, _, err = self.check(target, "--format", "yaml")

        self.assertEqual(code, 1)
        self.assertIn("format", err)

    def test_missing_required_files_are_reported(self) -> None:
        target = self.make_project()
        (target / "vault/parked.md").unlink()

        code, out, err = self.check(target)

        self.assertEqual(code, 0, err)
        self.assertIn("REQUIRED_FILE_MISSING", out)


if __name__ == "__main__":
    unittest.main()
