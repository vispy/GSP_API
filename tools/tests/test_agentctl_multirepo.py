from __future__ import annotations

import argparse
import contextlib
import importlib.machinery
import importlib.util
import io
import json
import pathlib
import subprocess
import tempfile
import unittest
from typing import Any
from unittest import mock


AGENTCTL_PATH = pathlib.Path(__file__).parents[1] / "agentctl"


def load_agentctl() -> Any:
    loader = importlib.machinery.SourceFileLoader(
        "agentctl_under_test", str(AGENTCTL_PATH)
    )
    spec = importlib.util.spec_from_loader(loader.name, loader)
    if spec is None:
        raise RuntimeError("Unable to load tools/agentctl")
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


agentctl = load_agentctl()


class MultiRepositoryLaunchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.base = pathlib.Path(self.temporary_directory.name)
        self.control = self.create_repository(
            "mission-control", "git@github.com:example/mission-control.git"
        )
        self.gsp = self.create_repository("gsp", "git@github.com:example/gsp.git")
        self.vispy2 = self.create_repository(
            "vispy2", "https://github.com/example/vispy2"
        )
        self.datoviz = self.create_repository(
            "datoviz", "git@github.com:example/datoviz.git"
        )
        self.write_control_files()
        self.commit(self.control, "mission control configuration")

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def git(self, repository: pathlib.Path, *args: str) -> str:
        return subprocess.check_output(
            ["git", "-C", str(repository), *args],
            stderr=subprocess.STDOUT,
            text=True,
        ).strip()

    def create_repository(self, name: str, remote: str) -> pathlib.Path:
        repository = self.base / name
        repository.mkdir()
        subprocess.check_call(
            ["git", "init", "-q", str(repository)],
            stdout=subprocess.DEVNULL,
        )
        self.git(repository, "config", "user.name", "Agentctl Tests")
        self.git(repository, "config", "user.email", "agentctl@example.invalid")
        self.git(repository, "remote", "add", "origin", remote)
        (repository / "AGENTS.md").write_text(
            f"# {name} instructions\n\nStay within the mission.\n",
            encoding="utf-8",
        )
        (repository / "seed.txt").write_text(f"{name}\n", encoding="utf-8")
        self.commit(repository, "initial")
        return repository

    def commit(self, repository: pathlib.Path, message: str) -> None:
        self.git(repository, "add", ".")
        self.git(repository, "commit", "-q", "-m", message)

    def repository_registry(self) -> dict[str, dict[str, Any]]:
        return {
            "mission-control": {
                "path": str(self.control),
                "expected_remote": "https://github.com/example/mission-control",
                "writable": True,
            },
            "gsp": {
                "path": str(self.gsp),
                "expected_remote": "https://github.com/example/gsp.git",
                "writable": True,
            },
            "vispy2": {
                "path": str(self.vispy2),
                "expected_remote": "git@github.com:example/vispy2.git",
                "writable": True,
            },
            "datoviz": {
                "path": str(self.datoviz),
                "expected_remote": "https://github.com/example/datoviz.git",
                "writable": False,
            },
        }

    def write_control_files(self) -> None:
        agent_directory = self.control / ".agent"
        (agent_directory / "missions").mkdir(parents=True)
        (agent_directory / "runs").mkdir()
        (self.control / "tools").mkdir()
        for name in ("PROJECT_CHARTER.md", "ARCHITECTURE.md", "SPEC_INDEX.md"):
            (self.control / name).write_text(f"# {name}\n", encoding="utf-8")
        (agent_directory / "S065_TECHNICAL_BASELINE.md").write_text(
            "# S065 baseline\n\nAccepted behavior.\n",
            encoding="utf-8",
        )
        (agent_directory / "project.json").write_text(
            json.dumps({"repositories": self.repository_registry()}, indent=2) + "\n",
            encoding="utf-8",
        )
        (agent_directory / "providers.json").write_text(
            json.dumps(
                {
                    "providers": {
                        "test-provider": {
                            "kind": "codex_exec",
                            "enabled": True,
                            "command_template": "exit 99 # {workspace} {worktree}",
                        },
                        "manual-provider": {
                            "kind": "manual_main_session",
                        },
                    }
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (agent_directory / "status.json").write_text(
            json.dumps({"missions": []}, indent=2) + "\n",
            encoding="utf-8",
        )

    def mission(
        self,
        repositories: list[str],
        path_locks: dict[str, list[str]],
    ) -> dict[str, Any]:
        return {
            "id": "M900",
            "state": "approved",
            "agent": "test-provider",
            "repositories": repositories,
            "path_locks": path_locks,
        }

    def test_prepares_one_writable_repository(self) -> None:
        mission = self.mission(["gsp"], {"gsp": ["src"]})
        targets, legacy = agentctl.validate_mission_targets(self.control, mission)

        workspace, provider_cwd = agentctl.add_isolated_worktrees(
            self.control, targets, "RTEST-ONE-M900", legacy
        )
        try:
            self.assertFalse(legacy)
            self.assertEqual(workspace, provider_cwd)
            self.assertEqual(targets[0]["worktree"], workspace / "gsp")
            self.assertEqual(
                self.git(targets[0]["worktree"], "rev-parse", "HEAD"),
                targets[0]["baseline_head"],
            )
            self.assertEqual(targets[0]["branch"], "agent/RTEST-ONE-M900")
        finally:
            agentctl.cleanup_worktrees(targets)

    def test_prepare_only_builds_two_repository_workspace_without_provider(
        self,
    ) -> None:
        mission = self.mission(
            ["gsp", "vispy2"],
            {"gsp": ["packages"], "vispy2": ["src", "tests"]},
        )
        status_path = self.control / ".agent" / "status.json"
        status_path.write_text(
            json.dumps({"missions": [mission]}, indent=2) + "\n",
            encoding="utf-8",
        )
        mission_path = self.control / ".agent" / "missions" / "M900-test.md"
        mission_path.write_text(
            "# M900\n\n## Stop conditions\n\nStop on unsafe state.\n",
            encoding="utf-8",
        )
        args = argparse.Namespace(
            approved=False,
            id="M900",
            provider=None,
            prepare_only=True,
        )

        with (
            mock.patch.object(agentctl, "repo_root", return_value=self.control),
            mock.patch.object(agentctl, "now_id", return_value="RTEST-TWO"),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(agentctl.cmd_launch(args), 0)

        run_path = self.control / ".agent" / "runs" / "RTEST-TWO-M900" / "run.json"
        metadata = json.loads(run_path.read_text(encoding="utf-8"))
        self.assertEqual(metadata["status"], "prepared")
        self.assertIsNone(metadata["pid"])
        self.assertEqual(len(metadata["repositories"]), 2)
        self.assertEqual(
            {
                pathlib.Path(item["worktree"]).parent
                for item in metadata["repositories"]
            },
            {pathlib.Path(metadata["workspace"])},
        )
        self.assertEqual(
            self.git(
                pathlib.Path(metadata["workspace"]),
                "rev-parse",
                "--is-inside-work-tree",
            ),
            "true",
        )
        self.assertTrue(
            all(
                pathlib.Path(item["worktree"]).is_dir()
                for item in metadata["repositories"]
            )
        )
        prompt = pathlib.Path(metadata["prompt_file"]).read_text(encoding="utf-8")
        self.assertIn("# File: AGENTS.md", prompt)
        self.assertIn("S065 implementation baseline", prompt)
        self.assertIn("Repository instructions: gsp", prompt)
        self.assertIn("Repository instructions: vispy2", prompt)
        self.assertIn(
            "modify only files at or below those roots",
            prompt,
        )
        self.assertIn("edits outside them are forbidden", prompt)
        prepared_targets = [
            {
                "source": pathlib.Path(item["source"]),
                "worktree": pathlib.Path(item["worktree"]),
                "branch": item["branch"],
            }
            for item in metadata["repositories"]
        ]
        agentctl.cleanup_worktrees(prepared_targets)

    def test_partial_worktree_failure_removes_created_resources(self) -> None:
        mission = self.mission(["gsp"], {"gsp": ["src"]})
        targets, legacy = agentctl.validate_mission_targets(self.control, mission)
        run_id = "RTEST-PARTIAL-M900"
        workspace = (
            self.control.parent / f"{self.control.name}-agent-workspaces" / run_id
        )
        original_check_call = subprocess.check_call

        def create_then_fail(command: list[str], **kwargs: Any) -> int:
            result = original_check_call(command, **kwargs)
            if "worktree" in command and "add" in command:
                raise subprocess.CalledProcessError(1, command)
            return result

        with mock.patch.object(
            agentctl.subprocess,
            "check_call",
            side_effect=create_then_fail,
        ):
            with self.assertRaises(subprocess.CalledProcessError):
                agentctl.add_isolated_worktrees(
                    self.control,
                    targets,
                    run_id,
                    legacy,
                )

        self.assertFalse(workspace.exists())
        self.assertEqual(
            self.git(self.gsp, "branch", "--list", f"agent/{run_id}"),
            "",
        )

    def test_rejects_dirty_writable_target(self) -> None:
        (self.gsp / "uncommitted.txt").write_text("dirty\n", encoding="utf-8")
        mission = self.mission(["gsp"], {"gsp": ["src"]})

        with self.assertRaisesRegex(agentctl.LaunchError, "is dirty"):
            agentctl.validate_mission_targets(self.control, mission)

    def test_rejects_remote_mismatch(self) -> None:
        self.git(
            self.gsp,
            "remote",
            "set-url",
            "origin",
            "git@github.com:someone-else/gsp.git",
        )
        mission = self.mission(["gsp"], {"gsp": ["src"]})

        with self.assertRaisesRegex(agentctl.LaunchError, "remote mismatch"):
            agentctl.validate_mission_targets(self.control, mission)

    def test_rejects_missing_repository_instructions(self) -> None:
        (self.gsp / "AGENTS.md").unlink()
        self.commit(self.gsp, "remove instructions")
        mission = self.mission(["gsp"], {"gsp": ["src"]})

        with self.assertRaisesRegex(agentctl.LaunchError, "missing AGENTS.md"):
            agentctl.validate_mission_targets(self.control, mission)

    def test_read_only_target_never_gets_worktree_or_branch(self) -> None:
        (self.datoviz / "local-evidence.txt").write_text("allowed\n", encoding="utf-8")
        mission = self.mission(["datoviz"], {})
        targets, legacy = agentctl.validate_mission_targets(self.control, mission)

        workspace, _ = agentctl.add_isolated_worktrees(
            self.control, targets, "RTEST-READONLY-M900", legacy
        )
        self.assertTrue(workspace.is_dir())
        self.assertIsNone(targets[0]["worktree"])
        self.assertIsNone(targets[0]["branch"])
        self.assertEqual(self.git(self.datoviz, "branch", "--list", "agent/*"), "")

        unsafe = self.mission(["datoviz"], {"datoviz": ["src"]})
        with self.assertRaisesRegex(agentctl.LaunchError, "cannot receive path locks"):
            agentctl.validate_mission_targets(self.control, unsafe)

    def test_rejects_exact_and_ancestor_lock_overlap(self) -> None:
        run_directory = self.control / ".agent" / "runs" / "R-ACTIVE"
        run_directory.mkdir()
        (run_directory / "run.json").write_text(
            json.dumps(
                {
                    "id": "R-ACTIVE",
                    "status": "running",
                    "path_locks": {"gsp": ["packages/gsp-core"]},
                }
            ),
            encoding="utf-8",
        )

        for lock in ("packages/gsp-core", "packages", "packages/gsp-core/src"):
            with self.subTest(lock=lock):
                mission = self.mission(["gsp"], {"gsp": [lock]})
                with self.assertRaisesRegex(agentctl.LaunchError, "Path lock conflict"):
                    agentctl.validate_mission_targets(self.control, mission)

    def test_allows_non_overlapping_locks(self) -> None:
        run_directory = self.control / ".agent" / "runs" / "R-ACTIVE"
        run_directory.mkdir()
        (run_directory / "run.json").write_text(
            json.dumps(
                {
                    "id": "R-ACTIVE",
                    "status": "running",
                    "path_locks": {"gsp": ["packages/gsp-core"]},
                }
            ),
            encoding="utf-8",
        )
        mission = self.mission(["gsp"], {"gsp": ["docs"]})

        targets, legacy = agentctl.validate_mission_targets(self.control, mission)

        self.assertFalse(legacy)
        self.assertEqual(targets[0]["locks"], ["docs"])

    def test_legacy_mission_uses_single_repository_layout(self) -> None:
        mission = {"id": "M001", "state": "approved"}
        mission_path = self.control / ".agent" / "missions" / "M001-legacy.md"
        mission_path.write_text(
            "# M001\n\n## Stop conditions\n\nStop on unsafe state.\n",
            encoding="utf-8",
        )
        self.commit(self.control, "legacy mission")
        targets, legacy = agentctl.validate_mission_targets(self.control, mission)

        workspace, provider_cwd = agentctl.add_isolated_worktrees(
            self.control, targets, "RTEST-LEGACY-M001", legacy
        )
        try:
            expected = (
                self.base / "mission-control-agent-worktrees" / "RTEST-LEGACY-M001"
            )
            self.assertTrue(legacy)
            self.assertEqual(workspace, expected)
            self.assertEqual(provider_cwd, expected)
            self.assertEqual(targets[0]["worktree"], expected)
            prompt = agentctl.mission_prompt(self.control, "M001", targets)
            self.assertIn(
                "A legacy writable repository with no recorded locks may be modified",
                prompt,
            )
        finally:
            agentctl.cleanup_worktrees(targets)

    def test_manual_provider_remains_prompt_only(self) -> None:
        mission = self.mission(["gsp"], {"gsp": ["src"]})
        mission["agent"] = "manual-provider"
        status_path = self.control / ".agent" / "status.json"
        status_path.write_text(
            json.dumps({"missions": [mission]}, indent=2) + "\n",
            encoding="utf-8",
        )
        mission_path = self.control / ".agent" / "missions" / "M900-manual.md"
        mission_path.write_text(
            "# M900\n\n## Stop conditions\n\nStop on unsafe state.\n",
            encoding="utf-8",
        )
        args = argparse.Namespace(
            approved=False,
            id="M900",
            provider=None,
            prepare_only=False,
        )

        with (
            mock.patch.object(agentctl, "repo_root", return_value=self.control),
            mock.patch.object(agentctl, "now_id", return_value="RTEST-MANUAL"),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(agentctl.cmd_launch(args), 0)

        run_path = self.control / ".agent" / "runs" / "RTEST-MANUAL-M900" / "run.json"
        metadata = json.loads(run_path.read_text(encoding="utf-8"))
        self.assertEqual(metadata["status"], "manual_required")
        self.assertIsNone(metadata["workspace"])
        self.assertIsNone(metadata["repositories"][0]["worktree"])
        self.assertIsNone(metadata["repositories"][0]["branch"])
        self.assertEqual(
            self.git(self.gsp, "branch", "--list", "agent/RTEST-MANUAL-M900"),
            "",
        )

    def test_rechecks_approval_inside_launch_lock(self) -> None:
        mission = self.mission(["gsp"], {"gsp": ["src"]})
        initial_status = {"missions": [mission]}
        changed_status = {
            "missions": [{**mission, "state": "running"}],
        }
        mission_path = self.control / ".agent" / "missions" / "M900-race.md"
        mission_path.write_text(
            "# M900\n\n## Stop conditions\n\nStop on unsafe state.\n",
            encoding="utf-8",
        )
        args = argparse.Namespace(
            approved=False,
            id="M900",
            provider=None,
            prepare_only=False,
        )

        with (
            mock.patch.object(agentctl, "repo_root", return_value=self.control),
            mock.patch.object(
                agentctl,
                "status",
                side_effect=[initial_status, changed_status],
            ),
            mock.patch.object(agentctl, "now_id", return_value="RTEST-RACE"),
            contextlib.redirect_stderr(io.StringIO()) as stderr,
        ):
            self.assertEqual(agentctl.cmd_launch(args), 2)

        self.assertIn("no longer approved", stderr.getvalue())
        self.assertFalse(
            (self.control / ".agent" / "runs" / "RTEST-RACE-M900").exists()
        )


if __name__ == "__main__":
    unittest.main()
