from __future__ import annotations

from pathlib import Path

import pytest

from larvaworld.portal import workspace_ui
from larvaworld.portal.workspace import get_active_workspace_path, initialize_workspace


@pytest.fixture(autouse=True)
def workspace_config_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LARVAWORLD_PORTAL_CONFIG_DIR", str(tmp_path / "config"))


def test_pick_workspace_directory_uses_macos_picker(
    monkeypatch,
    tmp_path: Path,
) -> None:
    selected = tmp_path / "workspace"

    monkeypatch.delenv("WSL_DISTRO_NAME", raising=False)
    monkeypatch.setattr(workspace_ui.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(
        workspace_ui.shutil,
        "which",
        lambda command: "/usr/bin/osascript" if command == "osascript" else None,
    )
    monkeypatch.setattr(
        workspace_ui,
        "_pick_directory_via_osascript",
        lambda initial_dir=None: selected,
    )

    path, error = workspace_ui._pick_workspace_directory(tmp_path)

    assert path == selected
    assert error is None


def test_pick_workspace_directory_macos_cancel_is_silent(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv("WSL_DISTRO_NAME", raising=False)
    monkeypatch.setattr(workspace_ui.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(
        workspace_ui.shutil,
        "which",
        lambda command: "/usr/bin/osascript" if command == "osascript" else None,
    )
    monkeypatch.setattr(
        workspace_ui,
        "_pick_directory_via_osascript",
        lambda initial_dir=None: None,
    )

    path, error = workspace_ui._pick_workspace_directory(tmp_path)

    assert path is None
    assert error is None


def test_pick_workspace_directory_reports_missing_picker(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv("WSL_DISTRO_NAME", raising=False)
    monkeypatch.setattr(workspace_ui.platform, "system", lambda: "Linux")
    monkeypatch.setattr(workspace_ui.shutil, "which", lambda _command: None)
    monkeypatch.setattr(
        workspace_ui,
        "_pick_directory_via_tk",
        lambda initial_dir=None: None,
    )

    path, error = workspace_ui._pick_workspace_directory(tmp_path)

    assert path is None
    assert error == "No folder picker is available in this environment."


def test_browse_activates_initialized_workspace(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    workspace_root = tmp_path / "workspace"
    initialize_workspace(workspace_root, name="Workspace")
    controller = workspace_ui.WorkspaceUiController()

    monkeypatch.setattr(
        workspace_ui,
        "_pick_workspace_directory",
        lambda initial_dir=None: (workspace_root, None),
    )

    controller._on_browse(None)

    assert controller.path_input.value == str(workspace_root)
    assert get_active_workspace_path() == workspace_root.resolve()
    assert "Active workspace updated." in controller.status_pane.object


def test_browse_keeps_uninitialized_workspace_pending(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    workspace_root = tmp_path / "workspace"
    controller = workspace_ui.WorkspaceUiController()

    monkeypatch.setattr(
        workspace_ui,
        "_pick_workspace_directory",
        lambda initial_dir=None: (workspace_root, None),
    )

    controller._on_browse(None)

    assert controller.path_input.value == str(workspace_root)
    assert get_active_workspace_path() is None
    assert "Folder is not initialized yet." in controller.status_pane.object
