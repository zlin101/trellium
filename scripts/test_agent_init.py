from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import importlib.util
from io import StringIO
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


SCRIPT_PATH = Path(__file__).with_name("agent-init.py")
SPEC = importlib.util.spec_from_file_location("agent_init", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {SCRIPT_PATH}")
agent_init = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(agent_init)


class AgentInitTest(unittest.TestCase):
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

    def test_adopt_creates_expected_files_and_is_idempotent(self) -> None:
        target = self.root / "project"
        target.mkdir()
        (target / "README.md").write_text("# Demo\n\nA demo project.\n", encoding="utf-8")

        code, _, err = self.run_agent_init("adopt", str(target))

        self.assertEqual(code, 0, err)
        expected = {
            "AGENTS.md",
            "README.md",
            "skills/agent-task/SKILL.md",
            "vault/collaboration.md",
            "vault/decisions.md",
            "vault/governance.md",
            "vault/handoff.md",
            "vault/index.md",
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


class RenderedContentTest(unittest.TestCase):
    def test_agent_entry_section_levels_governance_reading(self) -> None:
        section = agent_init.agent_entry_section()
        self.assertIn("cheat sheet", section)
        self.assertIn("Level B or Level C", section)
        self.assertNotIn("3. `vault/governance.md`", section)


if __name__ == "__main__":
    unittest.main()
