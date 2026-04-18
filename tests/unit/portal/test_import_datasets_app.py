from __future__ import annotations

from pathlib import Path

import pytest

from larvaworld.portal.datasets import import_datasets_app
from larvaworld.portal.datasets.discovery import RawDatasetCandidate
from larvaworld.portal.datasets.models import WorkspaceDatasetRecord
from larvaworld.portal.workspace import (
    clear_active_workspace_path,
    initialize_workspace,
    set_active_workspace_path,
)


@pytest.fixture(autouse=True)
def workspace_config_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LARVAWORLD_PORTAL_CONFIG_DIR", str(tmp_path / "config"))
    clear_active_workspace_path()


def _record(path: Path) -> WorkspaceDatasetRecord:
    return WorkspaceDatasetRecord(
        dataset_id=path.name,
        dataset_dir=path,
        data_dir=path / "data",
        conf_path=path / "data" / "conf.txt",
        h5_path=path / "data" / "data.h5",
        lab_id="Schleyer",
        group_id="exploration",
        ref_id=None,
        n_agents=12,
    )


def test_import_datasets_controller_requires_active_workspace() -> None:
    controller = import_datasets_app._ImportDatasetsController()

    assert controller.discover_button.disabled is True
    assert controller.import_button.disabled is True
    assert "Configure an active workspace" in controller.status.object


def test_import_datasets_controller_discovers_candidates_and_enables_import(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = initialize_workspace(tmp_path / "workspace")
    set_active_workspace_path(workspace.root)
    raw_root = tmp_path / "raw"
    candidate = RawDatasetCandidate(
        candidate_id="dish01",
        parent_dir="exploration/dish01",
        display_name="exploration/dish01",
        source_path=raw_root / "exploration" / "dish01",
        warnings=[],
    )
    monkeypatch.setattr(
        import_datasets_app,
        "discover_raw_datasets",
        lambda _lab_id, _raw_root: [candidate],
    )

    controller = import_datasets_app._ImportDatasetsController()

    assert controller.discover_button.disabled is True
    controller.raw_root_input.value = str(raw_root)
    assert controller.discover_button.disabled is False

    controller._handle_discover()

    assert "Discovered 1 candidate" in controller.status.object
    assert controller.candidate_select.disabled is False
    option_values = [value for value in controller.candidate_select.options.values()]
    candidate_key = next(value for value in option_values if value)
    controller.candidate_select.value = candidate_key

    assert controller.import_button.disabled is False
    assert controller.dataset_id_input.value == "dish01"
    assert "exploration/dish01" in controller.candidate_summary.object


def test_import_datasets_browse_raw_root_clears_existing_candidates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = initialize_workspace(tmp_path / "workspace")
    set_active_workspace_path(workspace.root)
    original_root = tmp_path / "raw"
    new_root = tmp_path / "raw-next"
    candidate = RawDatasetCandidate(
        candidate_id="dish01",
        parent_dir="exploration/dish01",
        display_name="exploration/dish01",
        source_path=original_root / "exploration" / "dish01",
        warnings=[],
    )
    monkeypatch.setattr(
        import_datasets_app,
        "discover_raw_datasets",
        lambda _lab_id, _raw_root: [candidate],
    )
    monkeypatch.setattr(
        import_datasets_app,
        "pick_directory",
        lambda *args, **kwargs: (new_root, None),
    )

    controller = import_datasets_app._ImportDatasetsController()
    controller.raw_root_input.value = str(original_root)
    controller._handle_discover()
    candidate_key = next(
        value for value in controller.candidate_select.options.values() if value
    )
    controller.candidate_select.value = candidate_key

    assert controller.import_button.disabled is False

    controller._handle_browse_raw_root()

    assert controller.raw_root_input.value == str(new_root)
    assert controller.candidate_select.disabled is True
    assert controller.candidate_select.value == ""
    assert controller.dataset_id_input.value == ""
    assert "Source changed." in controller.status.object


def test_import_datasets_browse_raw_root_cancel_is_silent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = initialize_workspace(tmp_path / "workspace")
    set_active_workspace_path(workspace.root)
    raw_root = tmp_path / "raw"
    monkeypatch.setattr(
        import_datasets_app,
        "pick_directory",
        lambda *args, **kwargs: (None, None),
    )

    controller = import_datasets_app._ImportDatasetsController()
    controller.raw_root_input.value = str(raw_root)
    initial_status = controller.status.object

    controller._handle_browse_raw_root()

    assert controller.raw_root_input.value == str(raw_root)
    assert controller.status.object == initial_status


def test_import_datasets_browse_raw_root_surfaces_picker_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = initialize_workspace(tmp_path / "workspace")
    set_active_workspace_path(workspace.root)
    monkeypatch.setattr(
        import_datasets_app,
        "pick_directory",
        lambda *args, **kwargs: (
            None,
            "No folder picker is available in this environment.",
        ),
    )

    controller = import_datasets_app._ImportDatasetsController()

    controller._handle_browse_raw_root()

    assert (
        "No folder picker is available in this environment." in controller.status.object
    )


def test_import_datasets_controller_builds_request_and_reports_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = initialize_workspace(tmp_path / "workspace")
    set_active_workspace_path(workspace.root)
    raw_root = tmp_path / "raw"
    candidate = RawDatasetCandidate(
        candidate_id="dish01",
        parent_dir="exploration/dish01",
        display_name="exploration/dish01",
        source_path=raw_root / "exploration" / "dish01",
        warnings=[],
    )
    seen_requests = []
    record = _record(
        workspace.datasets_dir / "imported" / "Schleyer" / "exploration" / "dish01"
    )
    monkeypatch.setattr(
        import_datasets_app,
        "discover_raw_datasets",
        lambda _lab_id, _raw_root: [candidate],
    )
    monkeypatch.setattr(
        import_datasets_app,
        "_candidate_import_overrides",
        lambda _lab_id, _raw_root, _candidate: {},
    )
    monkeypatch.setattr(
        import_datasets_app,
        "import_into_workspace",
        lambda request, workspace=None: seen_requests.append((request, workspace))
        or record,
    )

    controller = import_datasets_app._ImportDatasetsController()
    controller.lab_select.value = "Schleyer"
    controller.raw_root_input.value = str(raw_root)
    controller._handle_discover()
    candidate_key = next(
        value for value in controller.candidate_select.options.values() if value
    )
    controller.candidate_select.value = candidate_key
    controller.group_id_input.value = "exploration"
    controller.color_input.value = "blue"

    controller._handle_import()

    request, resolved_workspace = seen_requests[0]
    assert resolved_workspace == workspace
    assert request.lab_id == "Schleyer"
    assert request.parent_dir == "exploration/dish01"
    assert request.raw_folder == raw_root
    assert request.dataset_id == "dish01"
    assert request.group_id == "exploration"
    assert request.color == "blue"
    assert request.extra_kwargs == {}
    assert "imported into the active workspace" in controller.status.object
    assert str(record.dataset_dir) in controller.status.object


def test_import_datasets_controller_surfaces_adapter_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = initialize_workspace(tmp_path / "workspace")
    set_active_workspace_path(workspace.root)
    raw_root = tmp_path / "raw"
    candidate = RawDatasetCandidate(
        candidate_id="dish01",
        parent_dir="exploration/dish01",
        display_name="exploration/dish01",
        source_path=raw_root / "exploration" / "dish01",
        warnings=[],
    )
    monkeypatch.setattr(
        import_datasets_app,
        "discover_raw_datasets",
        lambda _lab_id, _raw_root: [candidate],
    )
    monkeypatch.setattr(
        import_datasets_app,
        "_candidate_import_overrides",
        lambda _lab_id, _raw_root, _candidate: {},
    )
    monkeypatch.setattr(
        import_datasets_app,
        "import_into_workspace",
        lambda _request, workspace=None: (_ for _ in ()).throw(
            RuntimeError("Import failed: backend returned no dataset")
        ),
    )

    controller = import_datasets_app._ImportDatasetsController()
    controller.raw_root_input.value = str(raw_root)
    controller._handle_discover()
    candidate_key = next(
        value for value in controller.candidate_select.options.values() if value
    )
    controller.candidate_select.value = candidate_key

    controller._handle_import()

    assert "Import failed: backend returned no dataset" in controller.status.object
