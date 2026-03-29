from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from larvaworld.portal.models_architecture.environment_builder_app import (
    _EnvironmentBuilderController,
)
from larvaworld.portal.workspace import (
    clear_active_workspace_path,
    initialize_workspace,
    set_active_workspace_path,
)


@pytest.fixture(autouse=True)
def workspace_config_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LARVAWORLD_PORTAL_CONFIG_DIR", str(tmp_path / "config"))
    clear_active_workspace_path()


def test_environment_builder_saves_preset_to_workspace(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    initialize_workspace(workspace_root)
    set_active_workspace_path(workspace_root)

    controller = _EnvironmentBuilderController()
    controller.preset_name.value = "Arena Alpha"
    controller._add_point_object(
        object_type="Food patch",
        x=0.01,
        y=-0.02,
        radius=0.008,
        color="#4caf50",
    )
    controller._add_border_object(
        x0=-0.03,
        y0=-0.03,
        x1=0.04,
        y1=0.04,
        width=0.001,
        color="#111111",
    )

    controller._on_save_preset(None)

    preset_path = workspace_root / "environments" / "Arena_Alpha.json"
    assert preset_path.is_file()
    payload = json.loads(preset_path.read_text(encoding="utf-8"))
    assert payload["arena"]["geometry"] == "rectangular"
    assert "food_001" in payload["food_params"]["source_units"]
    assert "border_002" in payload["border_list"]
    assert controller.preset_select.value == "Arena_Alpha.json"
    assert "Saved environment preset" in controller.status.object


def test_environment_builder_loads_preset_from_workspace(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    initialize_workspace(workspace_root)
    set_active_workspace_path(workspace_root)

    preset_path = workspace_root / "environments" / "demo_env.json"
    preset_path.write_text(
        json.dumps(
            {
                "arena": {"geometry": "circular", "dims": [0.3, 0.3]},
                "food_params": {
                    "source_units": {
                        "food_custom": {
                            "pos": [0.02, -0.01],
                            "radius": 0.012,
                            "color": "#88cc44",
                        }
                    },
                    "source_groups": {},
                    "food_grid": {},
                },
                "border_list": {
                    "border_custom": {
                        "vertices": [[-0.05, 0.01], [0.05, 0.01]],
                        "width": 0.002,
                        "color": "#222222",
                    }
                },
                "obstacles": {
                    "obstacle_custom": {
                        "pos": [-0.03, -0.04],
                        "radius": 0.01,
                        "color": "#445566",
                    }
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    controller = _EnvironmentBuilderController()
    controller.preset_select.value = "demo_env.json"

    controller._on_load_preset(None)

    assert controller.arena_shape.value == "circular"
    assert controller.arena_width.value == pytest.approx(0.3)
    assert controller.arena_height.value == pytest.approx(0.3)
    assert {obj.object_id for obj in controller._objects} == {
        "food_custom",
        "border_custom",
        "obstacle_custom",
    }
    assert controller.food_source.data["id"] == ["food_custom"]
    assert controller.border_source.data["id"] == ["border_custom"]
    assert controller.obstacle_source.data["id"] == ["obstacle_custom"]
    assert controller.preset_name.value == "demo_env"
    assert 'Loaded environment preset "demo_env"' in controller.status.object


def test_environment_builder_disables_workspace_presets_without_active_workspace() -> None:
    controller = _EnvironmentBuilderController()

    assert controller.save_preset_btn.disabled is True
    assert controller.load_preset_btn.disabled is True
    assert controller.refresh_presets_btn.disabled is True
    assert "Workspace environments directory unavailable" in controller.preset_meta.object


def test_environment_builder_applies_selected_food_edits_to_export(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    initialize_workspace(workspace_root)
    set_active_workspace_path(workspace_root)

    controller = _EnvironmentBuilderController()
    controller._add_point_object(
        object_type="Food patch",
        x=0.01,
        y=0.02,
        radius=0.008,
        color="#4caf50",
    )

    controller.selected_id.value = "food_custom"
    controller.selected_x.value = 0.03
    controller.selected_y.value = -0.01
    controller.selected_radius.value = 12.0
    controller.selected_color.value = "#123456"
    controller.selected_amount.value = 5.5
    controller.selected_odor_id.value = "banana"
    controller.selected_odor_intensity.value = 2.0
    controller.selected_odor_spread.value = 0.05
    controller.selected_substrate_type.value = "cornmeal"
    controller.selected_substrate_quality.value = 0.8

    controller._on_apply_selected_object(None)

    assert controller._objects[0].object_id == "food_custom"
    assert controller._objects[0].x == pytest.approx(0.03)
    assert controller._objects[0].y == pytest.approx(-0.01)
    assert controller._objects[0].radius == pytest.approx(0.012)
    payload = controller._build_export_config()
    food_entry = payload["food_params"]["source_units"]["food_custom"]
    assert food_entry["pos"] == [0.03, -0.01]
    assert food_entry["radius"] == pytest.approx(0.012)
    assert food_entry["amount"] == pytest.approx(5.5)
    assert food_entry["odor"] == {
        "id": "banana",
        "intensity": pytest.approx(2.0),
        "spread": pytest.approx(0.05),
    }
    assert food_entry["substrate"] == {
        "type": "cornmeal",
        "quality": pytest.approx(0.8),
    }
    assert controller.food_source.data["id"] == ["food_custom"]
    assert 'Updated object "food_custom"' in controller.status.object


def test_environment_builder_deletes_selected_object(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    initialize_workspace(workspace_root)
    set_active_workspace_path(workspace_root)

    controller = _EnvironmentBuilderController()
    controller._add_point_object(
        object_type="Food patch",
        x=0.01,
        y=0.02,
        radius=0.008,
        color="#4caf50",
    )

    controller._on_delete_selected_object(None)

    assert controller._objects == []
    assert controller.food_source.data["id"] == []
    assert controller.selected_object.disabled is True
    assert 'Deleted object "food_001"' in controller.status.object


def test_environment_builder_canvas_select_mode_syncs_inspector(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    initialize_workspace(workspace_root)
    set_active_workspace_path(workspace_root)

    controller = _EnvironmentBuilderController()
    controller._add_point_object(
        object_type="Food patch",
        x=0.01,
        y=0.02,
        radius=0.008,
        color="#4caf50",
    )
    controller.select_mode.value = True
    controller._on_select_mode_change()

    controller._on_tap(SimpleNamespace(x=0.01, y=0.02))

    assert controller.selected_object.value == "food_001"
    assert controller.selected_id.value == "food_001"
    assert controller.table.selection == [0]
    assert controller.food_highlight_source.data["x"] == [0.01]
    assert 'Selected "food_001" from canvas.' in controller.status.object


def test_environment_builder_table_selection_syncs_editor_and_highlight(
    tmp_path: Path,
) -> None:
    workspace_root = tmp_path / "workspace"
    initialize_workspace(workspace_root)
    set_active_workspace_path(workspace_root)

    controller = _EnvironmentBuilderController()
    controller._add_point_object(
        object_type="Food patch",
        x=0.01,
        y=0.02,
        radius=0.008,
        color="#4caf50",
    )
    controller._add_border_object(
        x0=-0.03,
        y0=-0.02,
        x1=0.04,
        y1=0.05,
        width=0.0015,
        color="#111111",
    )

    controller.table.selection = [1]
    controller._on_table_selection_change()

    assert controller.selected_object.value == "border_002"
    assert controller.selected_id.value == "border_002"
    assert controller.border_highlight_source.data["x0"] == [-0.03]
    assert controller.border_highlight_source.data["x1"] == [0.04]
