from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import importlib.util
from io import StringIO
from pathlib import Path
import tempfile
import unittest


SCRIPT_PATH = Path(__file__).with_name("sync-skills.py")
SPEC = importlib.util.spec_from_file_location("sync_skills", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {SCRIPT_PATH}")
sync_skills = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync_skills)


class SyncSkillsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.source = self.root / "init"
        self.source.mkdir()
        (self.source / "INIT.md").write_text("# Init\n", encoding="utf-8")
        protocol = self.source / "protocol"
        protocol.mkdir()
        (protocol / "flow.md").write_text("# Flow\n", encoding="utf-8")
        self.targets = [self.root / "skill-zh", self.root / "skill-en"]

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def run_sync(self, check: bool) -> int:
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            return sync_skills.sync(self.source, self.targets, check)

    def test_sync_creates_identical_snapshots(self) -> None:
        self.assertEqual(self.run_sync(check=False), 0)
        self.assertEqual(self.run_sync(check=True), 0)

        for target in self.targets:
            self.assertEqual((target / "init/INIT.md").read_text(encoding="utf-8"), "# Init\n")
            manifest = (target / sync_skills.MANIFEST_NAME).read_text(encoding="utf-8")
            self.assertIn('"source_file_count": 2', manifest)

    def test_check_detects_source_drift(self) -> None:
        self.assertEqual(self.run_sync(check=False), 0)
        (self.source / "INIT.md").write_text("# Updated Init\n", encoding="utf-8")

        self.assertEqual(self.run_sync(check=True), 1)

    def test_resync_removes_unexpected_generated_files(self) -> None:
        self.assertEqual(self.run_sync(check=False), 0)
        stale = self.targets[0] / "stale.md"
        stale.write_text("stale\n", encoding="utf-8")
        self.assertEqual(self.run_sync(check=True), 1)

        self.assertEqual(self.run_sync(check=False), 0)
        self.assertFalse(stale.exists())
        self.assertEqual(self.run_sync(check=True), 0)

    def test_rejects_target_inside_source(self) -> None:
        with self.assertRaises(sync_skills.SyncError):
            sync_skills.sync(self.source, [self.source / "generated"], check=False)

    def test_check_drift_output_names_the_fix(self) -> None:
        self.assertEqual(self.run_sync(check=False), 0)
        (self.source / "INIT.md").write_text("# Updated Init\n", encoding="utf-8")

        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = sync_skills.sync(self.source, self.targets, check=True)

        self.assertEqual(code, 1)
        self.assertIn("python3 scripts/sync-skills.py", err.getvalue())


if __name__ == "__main__":
    unittest.main()
