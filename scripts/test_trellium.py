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


if __name__ == "__main__":
    unittest.main()
