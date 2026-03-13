from __future__ import annotations

from larvaworld.gui_v2.registry_bridge import build_navigation_model


def test_build_navigation_model_contains_expected_structure() -> None:
    model = build_navigation_model()

    assert len(model.quick_start_modes) == 3
    assert len(model.lanes) == 3
    assert "wf.environment_builder" in model.entry_index

    environment_builder = model.entry_index["wf.environment_builder"]
    assert environment_builder.title == "Environment Builder"
    assert environment_builder.lane_key == "models"


def test_environment_builder_entry_is_present_in_models_lane() -> None:
    model = build_navigation_model()

    models_lane = next(lane for lane in model.lanes if lane.lane_id == "models")
    model_entry_ids = {entry.entry_id for entry in models_lane.entries}

    assert "wf.environment_builder" in model_entry_ids


def test_quick_start_modes_expose_expected_labels_and_colors() -> None:
    model = build_navigation_model()

    quick_start = {mode.mode_id: mode for mode in model.quick_start_modes}

    assert quick_start["user"].title == "User mode"
    assert quick_start["modeler"].title == "Modeler mode"
    assert quick_start["experimentalist"].title == "Experimentalist mode"

    assert quick_start["user"].color == "#7c575"
    assert quick_start["modeler"].color == "#eca548"
    assert quick_start["experimentalist"].color == "#6cbf6f"
