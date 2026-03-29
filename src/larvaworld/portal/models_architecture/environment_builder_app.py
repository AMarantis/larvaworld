from __future__ import annotations

import io
import json
from dataclasses import dataclass
import math
from pathlib import Path
import re

import pandas as pd
import panel as pn
from bokeh.events import Tap
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure

from larvaworld.lib.param.composition import substrate_dict
from larvaworld.portal.landing_registry import DOCS_ARENAS_SUBSTRATES
from larvaworld.portal.panel_components import PORTAL_RAW_CSS, build_app_header
from larvaworld.portal.workspace import WorkspaceError, get_workspace_dir


LANE_MODELS_COLOR = "#c1b0c2"
LANE_MODELS_COLOR_DARK = "#5a4760"
SUBSTRATE_TYPE_OPTIONS = ["standard"] + [
    key for key in substrate_dict.keys() if key != "standard"
]

ENV_BUILDER_RAW_CSS = """
.lw-env-builder-root {
  padding: 14px 12px 20px 12px;
}

.lw-env-builder-divider {
  width: 100%;
  height: 1px;
  background: rgba(17, 17, 17, 0.38);
  margin: 6px 0 8px 0;
}

.lw-env-builder-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  width: 100%;
}

.lw-env-builder-actions-primary {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.lw-env-builder-actions-download {
  display: flex;
  width: 100%;
}

.lw-env-builder-actions-download .bk-btn {
  width: 100% !important;
  min-width: 0 !important;
}

.lw-env-builder-intro {
  border-left: 4px solid #c1b0c2;
  background: rgba(193, 176, 194, 0.18);
  border-radius: 10px;
  padding: 10px 12px;
  margin: 0 0 10px 0;
}

.lw-env-builder-intro a {
  color: #4f2f5f;
}

.lw-env-builder-preset-meta {
  font-size: 12px;
  line-height: 1.45;
  color: rgba(17, 17, 17, 0.72);
  padding: 0 6px;
  overflow-wrap: anywhere;
}

.lw-env-builder-preset-actions {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  width: 100%;
  align-items: stretch;
}

.lw-env-builder-preset-actions > * {
  width: 100% !important;
  min-width: 0 !important;
}

.lw-env-builder-edit-actions {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  width: 100%;
}

.lw-env-builder-edit-actions > * {
  width: 100% !important;
  min-width: 0 !important;
}

.lw-env-builder-mode-actions {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  width: 100%;
}

.lw-env-builder-mode-actions > * {
  width: 100% !important;
  min-width: 0 !important;
}

.lw-env-builder-danger-action {
  display: flex;
  width: 100%;
}

.lw-env-builder-danger-action > * {
  width: 100% !important;
  min-width: 0 !important;
  flex: 1 1 auto;
}

.lw-env-builder-danger-action .bk-btn {
  width: 100% !important;
}

.lw-env-builder-select-mode .bk-btn {
  font-weight: 700;
}

.lw-env-builder-objects-table .tabulator {
  font-size: 12px;
}

.lw-env-builder-objects-table .tabulator .tabulator-col,
.lw-env-builder-objects-table .tabulator .tabulator-cell {
  font-size: 12px;
}

""".strip()


@dataclass(frozen=True)
class _ObjectRow:
    # English comments inside code.
    object_id: str
    object_type: str
    x: float | None
    y: float | None
    x2: float | None = None
    y2: float | None = None
    radius: float | None = None
    width: float | None = None
    color: str | None = None
    amount: float | None = None
    odor_id: str | None = None
    odor_intensity: float | None = None
    odor_spread: float | None = None
    substrate_type: str | None = None
    substrate_quality: float | None = None


class _EnvironmentBuilderController:
    # English comments inside code.
    def __init__(self) -> None:
        self._objects: list[_ObjectRow] = []
        self._border_start: tuple[float, float] | None = None
        self._selected_object_id: str | None = None
        self._syncing_selection = False
        self._counter = 1

        self.arena_shape = pn.widgets.Select(
            name="Arena shape",
            value="rectangular",
            options=["rectangular", "circular"],
        )
        self.arena_width = pn.widgets.FloatSlider(
            name="Arena width (m)",
            start=0.05,
            end=0.50,
            step=0.01,
            value=0.20,
        )
        self.arena_height = pn.widgets.FloatSlider(
            name="Arena height (m)",
            start=0.05,
            end=0.50,
            step=0.01,
            value=0.20,
        )
        self.object_type = pn.widgets.Select(
            name="Insert object",
            value="Food patch",
            options=["Food patch", "Obstacle", "Border segment"],
        )
        self.object_radius = pn.widgets.FloatSlider(
            name="Object radius (mm)",
            start=1.0,
            end=30.0,
            step=1.0,
            value=8.0,
            format="0.0",
        )
        self.border_width = pn.widgets.FloatSlider(
            name="Border width (mm)",
            start=0.5,
            end=10.0,
            step=0.5,
            value=1.0,
            format="0.0",
        )
        self.object_color = pn.widgets.ColorPicker(name="Object color", value="#4caf50")
        self.select_mode = pn.widgets.Toggle(
            name="Select on canvas",
            value=False,
            button_type="primary",
            css_classes=["lw-env-builder-select-mode"],
        )
        self.selected_object = pn.widgets.Select(
            name="Inspect object",
            options={},
            value=None,
        )
        self.selected_id = pn.widgets.TextInput(name="Object ID", value="")
        self.selected_x = pn.widgets.FloatInput(name="X (m)", value=0.0, step=0.001)
        self.selected_y = pn.widgets.FloatInput(name="Y (m)", value=0.0, step=0.001)
        self.selected_x2 = pn.widgets.FloatInput(name="X2 (m)", value=0.0, step=0.001)
        self.selected_y2 = pn.widgets.FloatInput(name="Y2 (m)", value=0.0, step=0.001)
        self.selected_radius = pn.widgets.FloatInput(
            name="Radius (mm)", value=8.0, step=0.5
        )
        self.selected_width = pn.widgets.FloatInput(
            name="Border width (mm)", value=1.0, step=0.5
        )
        self.selected_color = pn.widgets.ColorPicker(name="Color", value="#4caf50")
        self.selected_amount = pn.widgets.FloatInput(name="Food amount", value=3.0, step=0.5)
        self.selected_odor_id = pn.widgets.TextInput(name="Odor ID", value="")
        self.selected_odor_intensity = pn.widgets.FloatInput(
            name="Odor intensity",
            value=1.0,
            step=0.1,
        )
        self.selected_odor_spread = pn.widgets.FloatInput(
            name="Odor spread",
            value=0.02,
            step=0.005,
        )
        self.selected_substrate_type = pn.widgets.Select(
            name="Substrate type",
            value="standard",
            options=SUBSTRATE_TYPE_OPTIONS,
        )
        self.selected_substrate_quality = pn.widgets.FloatInput(
            name="Substrate quality",
            value=1.0,
            step=0.1,
        )
        self.apply_selected_btn = pn.widgets.Button(
            name="Apply changes",
            button_type="primary",
        )
        self.delete_selected_btn = pn.widgets.Button(
            name="Delete selected",
            button_type="warning",
        )
        self.preset_name = pn.widgets.TextInput(
            name="Preset name",
            value="environment_builder_config",
            placeholder="environment_builder_config",
        )
        self.preset_select = pn.widgets.Select(
            name="Saved presets",
            options={},
            value=None,
        )
        self.save_preset_btn = pn.widgets.Button(
            name="Save preset",
            button_type="primary",
        )
        self.load_preset_btn = pn.widgets.Button(
            name="Load preset",
            button_type="default",
        )
        self.refresh_presets_btn = pn.widgets.Button(
            name="Refresh list",
            button_type="default",
        )
        self.clear_last_btn = pn.widgets.Button(name="Undo last", button_type="default")
        self.clear_all_btn = pn.widgets.Button(name="Clear canvas", button_type="danger")
        self.export_btn = pn.widgets.FileDownload(
            name="",
            label="Download JSON",
            button_type="primary",
            callback=self._export_json,
            filename="environment_builder_config.json",
        )
        self.preset_meta = pn.pane.HTML("", sizing_mode="stretch_width", margin=(0, 0, 4, 0))
        self.clear_last_btn.width = 100
        self.clear_all_btn.width = None
        self.clear_all_btn.sizing_mode = "stretch_width"
        self.export_btn.width = 220
        self.refresh_presets_btn.width = 120
        self.status = pn.pane.Markdown("Click on the canvas to place an object.")
        self._table_columns = [
            "id",
            "type",
            "x",
            "y",
            "x2",
            "y2",
            "radius",
            "width",
            "color",
            "amount",
            "odor_id",
        ]
        self.table = pn.widgets.Tabulator(
            pd.DataFrame(columns=self._table_columns),
            show_index=False,
            selectable=1,
            editors={column: None for column in self._table_columns},
            height=620,
            sizing_mode="stretch_width",
            css_classes=["lw-env-builder-objects-table"],
        )

        self.food_source = ColumnDataSource(
            {"x": [], "y": [], "r": [], "color": [], "id": []}
        )
        self.food_highlight_source = ColumnDataSource(
            {"x": [], "y": [], "r": [], "color": []}
        )
        self.obstacle_source = ColumnDataSource(
            {"x": [], "y": [], "r": [], "color": [], "id": []}
        )
        self.obstacle_highlight_source = ColumnDataSource(
            {"x": [], "y": [], "r": [], "color": []}
        )
        self.border_source = ColumnDataSource(
            {"x0": [], "y0": [], "x1": [], "y1": [], "w": [], "color": [], "id": []}
        )
        self.border_highlight_source = ColumnDataSource(
            {"x0": [], "y0": [], "x1": [], "y1": [], "w": [], "color": []}
        )
        self.border_preview_source = ColumnDataSource({"x": [], "y": [], "color": []})
        self._arena_source = ColumnDataSource(
            {
                "x": [0.0],
                "y": [0.0],
                "w": [self.arena_width.value],
                "h": [self.arena_height.value],
            }
        )

        self.fig = figure(
            title="Environment canvas",
            x_range=(-0.30, 0.30),
            y_range=(-0.30, 0.30),
            match_aspect=True,
            width=760,
            height=620,
            tools="pan,wheel_zoom,reset,save",
            active_scroll="wheel_zoom",
            toolbar_location="right",
        )
        self.fig.background_fill_color = "#ffffff"
        self.fig.border_fill_color = "#fafafa"
        self.fig.xaxis.axis_label = "X (m)"
        self.fig.yaxis.axis_label = "Y (m)"

        self._arena_rect_renderer = self.fig.rect(
            x="x",
            y="y",
            width="w",
            height="h",
            source=self._arena_source,
            line_color=LANE_MODELS_COLOR_DARK,
            line_width=3,
            fill_alpha=0.0,
            visible=True,
        )
        self._arena_circle_renderer = self.fig.ellipse(
            x="x",
            y="y",
            width="w",
            height="h",
            source=self._arena_source,
            line_color=LANE_MODELS_COLOR_DARK,
            line_width=3,
            fill_alpha=0.0,
            visible=False,
        )
        self.fig.circle(
            x="x",
            y="y",
            radius="r",
            source=self.food_source,
            line_color="color",
            fill_color="color",
            fill_alpha=0.35,
            line_width=2,
            legend_label="Food patches",
        )
        self.fig.circle(
            x="x",
            y="y",
            radius="r",
            source=self.food_highlight_source,
            line_color="#f97316",
            fill_color=None,
            line_width=4,
        )
        self.fig.circle(
            x="x",
            y="y",
            radius="r",
            source=self.obstacle_source,
            line_color="color",
            fill_color=None,
            line_width=2,
            legend_label="Obstacles",
        )
        self.fig.circle(
            x="x",
            y="y",
            radius="r",
            source=self.obstacle_highlight_source,
            line_color="#f97316",
            fill_color=None,
            line_width=4,
        )
        self.fig.segment(
            x0="x0",
            y0="y0",
            x1="x1",
            y1="y1",
            source=self.border_source,
            line_color="color",
            line_width="w",
            legend_label="Borders",
        )
        self.fig.segment(
            x0="x0",
            y0="y0",
            x1="x1",
            y1="y1",
            source=self.border_highlight_source,
            line_color="#f97316",
            line_width="w",
        )
        self.fig.scatter(
            x="x",
            y="y",
            source=self.border_preview_source,
            marker="cross",
            size=16,
            line_width=3,
            line_color="color",
        )
        self.fig.legend.location = "top_left"
        self.fig.legend.background_fill_alpha = 0.85

        self.fig.on_event(Tap, self._on_tap)
        self.arena_shape.param.watch(self._update_arena, "value")
        self.arena_width.param.watch(self._update_arena, "value")
        self.arena_height.param.watch(self._update_arena, "value")
        self.object_type.param.watch(self._update_insert_hint, "value")
        self.select_mode.param.watch(self._on_select_mode_change, "value")
        self.selected_object.param.watch(self._on_selected_object_change, "value")
        self.table.param.watch(self._on_table_selection_change, "selection")
        self.apply_selected_btn.on_click(self._on_apply_selected_object)
        self.delete_selected_btn.on_click(self._on_delete_selected_object)
        self.save_preset_btn.on_click(self._on_save_preset)
        self.load_preset_btn.on_click(self._on_load_preset)
        self.refresh_presets_btn.on_click(self._on_refresh_presets)
        self.clear_last_btn.on_click(self._on_clear_last)
        self.clear_all_btn.on_click(self._on_clear_all)

        self._update_insert_hint()
        self._refresh_preset_controls()
        self._refresh_object_controls()

    def view(self) -> pn.viewable.Viewable:
        # English comments inside code.
        intro = pn.pane.Markdown(
            (
                "### Environment Builder\n"
                "Build and revise environment configurations for Larvaworld experiments: define arena "
                "geometry, place food patches, obstacles, and border segments on the canvas, inspect "
                "and edit placed objects, and save reusable workspace presets or export the result as "
                "an environment JSON. "
                f"Reference: [Arenas and Substrates]({DOCS_ARENAS_SUBSTRATES})."
            ),
            css_classes=["lw-env-builder-intro"],
            margin=0,
        )
        divider = pn.pane.HTML('<div class="lw-env-builder-divider"></div>', margin=0)
        primary_actions = pn.Row(
            self.refresh_presets_btn,
            css_classes=["lw-env-builder-actions-primary"],
            sizing_mode="stretch_width",
            margin=0,
        )
        download_action = pn.Row(
            self.export_btn,
            css_classes=["lw-env-builder-actions-download"],
            sizing_mode="stretch_width",
            margin=0,
        )
        actions = pn.Column(
            primary_actions,
            download_action,
            css_classes=["lw-env-builder-actions"],
            sizing_mode="stretch_width",
            margin=0,
        )

        controls = pn.Card(
            self.arena_shape,
            self.arena_width,
            self.arena_height,
            divider,
            pn.Row(
                self.select_mode,
                self.clear_last_btn,
                css_classes=["lw-env-builder-mode-actions"],
                sizing_mode="stretch_width",
                margin=0,
            ),
            self.object_type,
            self.object_radius,
            self.border_width,
            self.object_color,
            pn.layout.Divider(margin=(4, 0, 0, 0)),
            self.preset_name,
            self.preset_select,
            self.preset_meta,
            pn.Row(
                self.save_preset_btn,
                self.load_preset_btn,
                css_classes=["lw-env-builder-preset-actions"],
                sizing_mode="stretch_width",
                margin=0,
            ),
            actions,
            self.status,
            title="Controls",
            collapsed=False,
            sizing_mode="stretch_width",
        )
        table_card = pn.Card(
            self.table,
            title="Placed objects",
            collapsed=False,
            sizing_mode="stretch_width",
        )
        editor_card = pn.Card(
            self.selected_object,
            self.selected_id,
            self.selected_x,
            self.selected_y,
            self.selected_x2,
            self.selected_y2,
            self.selected_radius,
            self.selected_width,
            self.selected_color,
            self.selected_amount,
            self.selected_odor_id,
            self.selected_odor_intensity,
            self.selected_odor_spread,
            self.selected_substrate_type,
            self.selected_substrate_quality,
            pn.Row(
                self.apply_selected_btn,
                self.delete_selected_btn,
                css_classes=["lw-env-builder-edit-actions"],
                sizing_mode="stretch_width",
                margin=0,
            ),
            pn.Row(
                self.clear_all_btn,
                css_classes=["lw-env-builder-danger-action"],
                sizing_mode="stretch_width",
                margin=(4, 0, 0, 0),
            ),
            title="Inspect / Edit",
            collapsed=False,
            sizing_mode="stretch_width",
        )
        side = pn.Column(controls, width=360, sizing_mode="fixed")

        canvas = pn.pane.Bokeh(self.fig, sizing_mode="stretch_both")
        center = pn.Column(
            canvas,
            table_card,
            width=760,
            sizing_mode="fixed",
        )
        right = pn.Column(editor_card, width=360, sizing_mode="fixed")
        main = pn.Row(side, center, right, sizing_mode="stretch_width")

        return pn.Column(
            intro, main, css_classes=["lw-env-builder-root"], sizing_mode="stretch_both"
        )

    def _update_insert_hint(self, *_: object) -> None:
        # English comments inside code.
        is_border_segment = self.object_type.value == "Border segment"
        self.border_width.visible = is_border_segment
        self.object_radius.visible = not is_border_segment
        if self.object_type.value == "Obstacle":
            self.object_radius.name = "Obstacle radius (mm)"
        else:
            self.object_radius.name = "Food patch radius (mm)"
        if self.object_type.value == "Border segment":
            if self._border_start is None:
                self.status.object = "Click first point for border segment."
            else:
                x0, y0 = self._border_start
                self.status.object = (
                    f"First point captured at ({x0:.3f}, {y0:.3f}). Click second point."
                )
            return
        self._border_start = None
        self._clear_border_preview()
        self.status.object = f"Click canvas to add a {self.object_type.value.lower()}."

    def _preset_dir(self) -> Path:
        # English comments inside code.
        return get_workspace_dir("environments")

    def _preset_filename(self, name: str) -> str:
        # English comments inside code.
        cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "_", name.strip()).strip("._-")
        if not cleaned:
            cleaned = "environment_builder_config"
        if not cleaned.endswith(".json"):
            cleaned += ".json"
        return cleaned

    def _preset_label_from_filename(self, filename: str) -> str:
        # English comments inside code.
        return Path(filename).stem

    def _next_counter_seed(self) -> int:
        # English comments inside code.
        highest = 0
        for obj in self._objects:
            match = re.search(r"_(\d+)$", obj.object_id)
            if match:
                highest = max(highest, int(match.group(1)))
        return highest + 1 if highest else len(self._objects) + 1

    def _refresh_preset_controls(self, *, selected_filename: str | None = None) -> None:
        # English comments inside code.
        try:
            preset_dir = self._preset_dir()
            preset_dir.mkdir(parents=True, exist_ok=True)
        except WorkspaceError as exc:
            self.preset_meta.object = (
                '<div class="lw-env-builder-preset-meta">'
                f"Workspace environments directory unavailable: {exc}"
                "</div>"
            )
            self.preset_select.options = {}
            self.preset_select.value = None
            self.preset_select.disabled = True
            self.load_preset_btn.disabled = True
            self.save_preset_btn.disabled = True
            self.refresh_presets_btn.disabled = True
            return

        preset_files = sorted(preset_dir.glob("*.json"))
        options = {
            self._preset_label_from_filename(path.name): path.name for path in preset_files
        }
        self.preset_select.options = options
        self.preset_select.disabled = False
        self.save_preset_btn.disabled = False
        self.refresh_presets_btn.disabled = False

        if not options:
            self.preset_select.value = None
            self.load_preset_btn.disabled = True
        else:
            self.load_preset_btn.disabled = False
            if selected_filename in options.values():
                self.preset_select.value = selected_filename
            elif self.preset_select.value not in options.values():
                self.preset_select.value = next(iter(options.values()))

        self.preset_meta.object = (
            '<div class="lw-env-builder-preset-meta">'
            f"Workspace preset directory: <code>{preset_dir}</code>"
            "</div>"
        )

    def _selected_row(self) -> _ObjectRow | None:
        # English comments inside code.
        selected_id = self._selected_object_id or self.selected_object.value
        if not selected_id:
            return None
        for obj in self._objects:
            if obj.object_id == selected_id:
                return obj
        return None

    def _selected_row_index(self) -> int | None:
        # English comments inside code.
        selected = self._selected_row()
        if selected is None:
            return None
        for index, obj in enumerate(self._objects):
            if obj.object_id == selected.object_id:
                return index
        return None

    def _object_options(self) -> dict[str, str]:
        # English comments inside code.
        return {
            f"{obj.object_id} ({obj.object_type})": obj.object_id for obj in self._objects
        }

    def _set_editor_disabled(self, disabled: bool) -> None:
        # English comments inside code.
        widgets = [
            self.selected_object,
            self.selected_id,
            self.selected_x,
            self.selected_y,
            self.selected_x2,
            self.selected_y2,
            self.selected_radius,
            self.selected_width,
            self.selected_color,
            self.selected_amount,
            self.selected_odor_id,
            self.selected_odor_intensity,
            self.selected_odor_spread,
            self.selected_substrate_type,
            self.selected_substrate_quality,
            self.apply_selected_btn,
            self.delete_selected_btn,
        ]
        for widget in widgets:
            widget.disabled = disabled

    def _clear_canvas_highlight(self) -> None:
        # English comments inside code.
        self.food_highlight_source.data = {"x": [], "y": [], "r": [], "color": []}
        self.obstacle_highlight_source.data = {"x": [], "y": [], "r": [], "color": []}
        self.border_highlight_source.data = {
            "x0": [],
            "y0": [],
            "x1": [],
            "y1": [],
            "w": [],
            "color": [],
        }

    def _update_canvas_highlight(self, obj: _ObjectRow | None) -> None:
        # English comments inside code.
        self._clear_canvas_highlight()
        if obj is None:
            return
        if obj.object_type == "Food patch":
            self.food_highlight_source.data = {
                "x": [obj.x],
                "y": [obj.y],
                "r": [max(float(obj.radius or 0.008) * 1.35, 0.004)],
                "color": ["#f97316"],
            }
        elif obj.object_type == "Obstacle":
            self.obstacle_highlight_source.data = {
                "x": [obj.x],
                "y": [obj.y],
                "r": [max(float(obj.radius or 0.008) * 1.35, 0.004)],
                "color": ["#f97316"],
            }
        else:
            self.border_highlight_source.data = {
                "x0": [obj.x],
                "y0": [obj.y],
                "x1": [obj.x2],
                "y1": [obj.y2],
                "w": [max(4, int((obj.width or 0.001) * 3000))],
                "color": ["#f97316"],
            }

    def _set_selected_object(self, object_id: str | None) -> None:
        # English comments inside code.
        self._syncing_selection = True
        try:
            self._selected_object_id = object_id
            options = self._object_options()
            if object_id is None or object_id not in options.values():
                self.selected_object.value = None
                self.table.selection = []
                self._populate_editor(None)
                self.selected_object.disabled = not bool(options)
                self._update_canvas_highlight(None)
                return
            self.selected_object.value = object_id
            row_index = self._selected_row_index()
            self.table.selection = [] if row_index is None else [row_index]
            obj = self._selected_row()
            self._populate_editor(obj)
            self._update_canvas_highlight(obj)
        finally:
            self._syncing_selection = False

    def _sync_editor_visibility(self, obj: _ObjectRow | None) -> None:
        # English comments inside code.
        object_type = obj.object_type if obj is not None else None
        is_border = object_type == "Border segment"
        is_food = object_type == "Food patch"
        self.selected_x2.visible = is_border
        self.selected_y2.visible = is_border
        self.selected_width.visible = is_border
        self.selected_radius.visible = object_type in {"Food patch", "Obstacle"}
        self.selected_amount.visible = is_food
        self.selected_odor_id.visible = is_food
        self.selected_odor_intensity.visible = is_food
        self.selected_odor_spread.visible = is_food
        self.selected_substrate_type.visible = is_food
        self.selected_substrate_quality.visible = is_food

    def _set_substrate_type_options(self, substrate_type: str | None = None) -> None:
        # English comments inside code.
        options = list(SUBSTRATE_TYPE_OPTIONS)
        if substrate_type:
            substrate_value = str(substrate_type)
            if substrate_value not in options:
                options.append(substrate_value)
        self.selected_substrate_type.options = options

    def _populate_editor(self, obj: _ObjectRow | None) -> None:
        # English comments inside code.
        self._sync_editor_visibility(obj)
        if obj is None:
            self._set_editor_disabled(True)
            self._set_substrate_type_options("standard")
            return

        self._set_editor_disabled(False)
        self.selected_id.value = obj.object_id
        self.selected_x.value = float(obj.x or 0.0)
        self.selected_y.value = float(obj.y or 0.0)
        self.selected_x2.value = float(obj.x2 or 0.0)
        self.selected_y2.value = float(obj.y2 or 0.0)
        self.selected_radius.value = round(float(obj.radius or 0.008) * 1000.0, 4)
        self.selected_width.value = round(float(obj.width or 0.001) * 1000.0, 4)
        self.selected_color.value = str(obj.color or "#4caf50")
        self.selected_amount.value = float(obj.amount or 3.0)
        self.selected_odor_id.value = str(obj.odor_id or f"{obj.object_id}_odor")
        self.selected_odor_intensity.value = float(obj.odor_intensity or 1.0)
        self.selected_odor_spread.value = float(obj.odor_spread or 0.02)
        self._set_substrate_type_options(obj.substrate_type or "standard")
        self.selected_substrate_type.value = str(obj.substrate_type or "standard")
        self.selected_substrate_quality.value = float(obj.substrate_quality or 1.0)

    def _refresh_object_controls(self, *, selected_object_id: str | None = None) -> None:
        # English comments inside code.
        options = self._object_options()
        self.selected_object.options = options
        if not options:
            self._set_selected_object(None)
            return

        self.selected_object.disabled = False
        target_id = selected_object_id
        if target_id not in options.values():
            target_id = (
                self._selected_object_id
                if self._selected_object_id in options.values()
                else next(iter(options.values()))
            )
        self._set_selected_object(target_id)

    def _on_selected_object_change(self, *_: object) -> None:
        # English comments inside code.
        if self._syncing_selection:
            return
        self._set_selected_object(self.selected_object.value)

    def _on_table_selection_change(self, *_: object) -> None:
        # English comments inside code.
        if self._syncing_selection:
            return
        selection = list(self.table.selection or [])
        if not selection:
            self._set_selected_object(None)
            return
        row_index = selection[0]
        if row_index < 0 or row_index >= len(self._objects):
            self._set_selected_object(None)
            return
        self._set_selected_object(self._objects[row_index].object_id)

    def _on_select_mode_change(self, *_: object) -> None:
        # English comments inside code.
        if self.select_mode.value:
            self.select_mode.button_type = "success"
            self.status.object = (
                "Select mode enabled. Click an object on the canvas to inspect it."
            )
        else:
            self.select_mode.button_type = "primary"
            self.status.object = f"Click canvas to add a {self.object_type.value.lower()}."

    def _iter_loaded_objects(self, config: dict[str, object]) -> list[_ObjectRow]:
        # English comments inside code.
        loaded: list[_ObjectRow] = []
        food_params = config.get("food_params")
        if isinstance(food_params, dict):
            source_units = food_params.get("source_units", {})
            if isinstance(source_units, dict):
                for object_id, entry in source_units.items():
                    if not isinstance(entry, dict):
                        continue
                    pos = entry.get("pos")
                    if not isinstance(pos, (list, tuple)) or len(pos) < 2:
                        continue
                    loaded.append(
                        _ObjectRow(
                            object_id=str(object_id),
                            object_type="Food patch",
                            x=float(pos[0]),
                            y=float(pos[1]),
                            radius=float(entry.get("radius", 0.008)),
                            color=str(entry.get("color", "#4caf50")),
                            amount=float(entry.get("amount", 3.0)),
                            odor_id=str(
                                entry.get("odor", {}).get("id", f"{object_id}_odor")
                            ),
                            odor_intensity=float(
                                entry.get("odor", {}).get("intensity", 1.0)
                            ),
                            odor_spread=float(entry.get("odor", {}).get("spread", 0.02)),
                            substrate_type=str(
                                entry.get("substrate", {}).get("type", "standard")
                            ),
                            substrate_quality=float(
                                entry.get("substrate", {}).get("quality", 1.0)
                            ),
                        )
                    )

        obstacles = config.get("obstacles", {})
        if isinstance(obstacles, dict):
            for object_id, entry in obstacles.items():
                if not isinstance(entry, dict):
                    continue
                pos = entry.get("pos")
                if not isinstance(pos, (list, tuple)) or len(pos) < 2:
                    continue
                loaded.append(
                    _ObjectRow(
                        object_id=str(object_id),
                        object_type="Obstacle",
                        x=float(pos[0]),
                        y=float(pos[1]),
                        radius=float(entry.get("radius", 0.008)),
                        color=str(entry.get("color", "#2f2f2f")),
                    )
                )

        border_list = config.get("border_list", {})
        if isinstance(border_list, dict):
            for object_id, entry in border_list.items():
                if not isinstance(entry, dict):
                    continue
                vertices = entry.get("vertices", entry.get("points"))
                if not isinstance(vertices, (list, tuple)) or len(vertices) < 2:
                    continue
                p0, p1 = vertices[0], vertices[1]
                if (
                    not isinstance(p0, (list, tuple))
                    or not isinstance(p1, (list, tuple))
                    or len(p0) < 2
                    or len(p1) < 2
                ):
                    continue
                loaded.append(
                    _ObjectRow(
                        object_id=str(object_id),
                        object_type="Border segment",
                        x=float(p0[0]),
                        y=float(p0[1]),
                        x2=float(p1[0]),
                        y2=float(p1[1]),
                        width=float(entry.get("width", 0.001)),
                        color=str(entry.get("color", "#111111")),
                    )
                )

        return loaded

    def _apply_config(self, config: dict[str, object]) -> None:
        # English comments inside code.
        arena = config.get("arena", {})
        if isinstance(arena, dict):
            geometry = str(arena.get("geometry", arena.get("shape", "rectangular")))
            geometry = {
                "rect": "rectangular",
                "rectangle": "rectangular",
                "circle": "circular",
            }.get(geometry, geometry)
            if geometry in {"rectangular", "circular"}:
                self.arena_shape.value = geometry
            dims = arena.get("dims")
            if isinstance(dims, (list, tuple)) and len(dims) >= 2:
                self.arena_width.value = float(dims[0])
                self.arena_height.value = float(dims[1])

        self._objects = self._iter_loaded_objects(config)
        self._border_start = None
        self._counter = self._next_counter_seed()
        self._rebuild_sources()
        self._refresh_table()
        self._refresh_object_controls()
        self._update_insert_hint()

    def _on_save_preset(self, _: object) -> None:
        # English comments inside code.
        try:
            preset_dir = self._preset_dir()
            preset_dir.mkdir(parents=True, exist_ok=True)
        except WorkspaceError as exc:
            self.status.object = f"Cannot save preset without an active workspace: {exc}"
            return

        raw_name = self.preset_name.value.strip() or "environment_builder_config"
        filename = self._preset_filename(raw_name)
        target = preset_dir / filename
        payload = self._build_export_config()
        target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        self._refresh_preset_controls(selected_filename=filename)
        self.preset_name.value = self._preset_label_from_filename(filename)
        self.status.object = f'Saved environment preset "{self.preset_name.value}".'

    def _on_load_preset(self, _: object) -> None:
        # English comments inside code.
        selected = self.preset_select.value
        if not selected:
            self.status.object = "Select a saved preset first."
            return

        try:
            path = self._preset_dir() / str(selected)
        except WorkspaceError as exc:
            self.status.object = f"Cannot load preset without an active workspace: {exc}"
            return

        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            self._refresh_preset_controls()
            self.status.object = "Selected preset file no longer exists."
            return
        except (OSError, json.JSONDecodeError) as exc:
            self.status.object = f"Failed to read preset: {exc}"
            return

        if not isinstance(payload, dict):
            self.status.object = "Preset file is not a valid environment configuration."
            return

        self._apply_config(payload)
        self.preset_name.value = path.stem
        self.status.object = f'Loaded environment preset "{path.stem}".'

    def _on_refresh_presets(self, _: object) -> None:
        # English comments inside code.
        self._refresh_preset_controls(selected_filename=str(self.preset_select.value or ""))
        self.status.object = "Refreshed environment preset list."

    def _on_apply_selected_object(self, _: object) -> None:
        # English comments inside code.
        current = self._selected_row()
        if current is None:
            self.status.object = "Select an object to edit first."
            return

        new_id = self.selected_id.value.strip()
        if not new_id:
            self.status.object = "Object ID cannot be empty."
            return
        if any(obj.object_id == new_id and obj is not current for obj in self._objects):
            self.status.object = f'Object ID "{new_id}" is already in use.'
            return

        x = float(self.selected_x.value)
        y = float(self.selected_y.value)
        if not self._inside_arena(x, y):
            self.status.object = "Primary object coordinates must stay inside the arena."
            return

        updated = _ObjectRow(
            object_id=new_id,
            object_type=current.object_type,
            x=x,
            y=y,
            color=self.selected_color.value,
        )

        if current.object_type == "Border segment":
            x2 = float(self.selected_x2.value)
            y2 = float(self.selected_y2.value)
            if not self._inside_arena(x2, y2):
                self.status.object = "Border end coordinates must stay inside the arena."
                return
            updated = _ObjectRow(
                object_id=new_id,
                object_type=current.object_type,
                x=x,
                y=y,
                x2=x2,
                y2=y2,
                width=round(float(self.selected_width.value) / 1000.0, 4),
                color=self.selected_color.value,
            )
        elif current.object_type == "Obstacle":
            updated = _ObjectRow(
                object_id=new_id,
                object_type=current.object_type,
                x=x,
                y=y,
                radius=round(float(self.selected_radius.value) / 1000.0, 4),
                color=self.selected_color.value,
            )
        else:
            updated = _ObjectRow(
                object_id=new_id,
                object_type=current.object_type,
                x=x,
                y=y,
                radius=round(float(self.selected_radius.value) / 1000.0, 4),
                color=self.selected_color.value,
                amount=float(self.selected_amount.value),
                odor_id=self.selected_odor_id.value.strip() or f"{new_id}_odor",
                odor_intensity=float(self.selected_odor_intensity.value),
                odor_spread=float(self.selected_odor_spread.value),
                substrate_type=self.selected_substrate_type.value.strip() or "standard",
                substrate_quality=float(self.selected_substrate_quality.value),
            )

        self._objects = [
            updated if obj.object_id == current.object_id else obj for obj in self._objects
        ]
        self._counter = self._next_counter_seed()
        self._rebuild_sources()
        self._refresh_table()
        self._refresh_object_controls(selected_object_id=updated.object_id)
        self.status.object = f'Updated object "{updated.object_id}".'

    def _on_delete_selected_object(self, _: object) -> None:
        # English comments inside code.
        current = self._selected_row()
        if current is None:
            self.status.object = "Select an object to delete first."
            return
        self._objects = [
            obj for obj in self._objects if obj.object_id != current.object_id
        ]
        self._counter = self._next_counter_seed()
        self._rebuild_sources()
        self._refresh_table()
        self._refresh_object_controls()
        self.status.object = f'Deleted object "{current.object_id}".'

    def _update_arena(self, *_: object) -> None:
        # English comments inside code.
        width = float(self.arena_width.value)
        height = float(self.arena_height.value)
        self._arena_source.data = {"x": [0.0], "y": [0.0], "w": [width], "h": [height]}
        is_rect = self.arena_shape.value == "rectangular"
        self._arena_rect_renderer.visible = is_rect
        self._arena_circle_renderer.visible = not is_rect

    def _inside_arena(self, x: float, y: float) -> bool:
        # English comments inside code.
        width = float(self.arena_width.value)
        height = float(self.arena_height.value)
        if self.arena_shape.value == "rectangular":
            return abs(x) <= width / 2 and abs(y) <= height / 2
        if width <= 0 or height <= 0:
            return False
        nx = x / (width / 2)
        ny = y / (height / 2)
        return (nx * nx + ny * ny) <= 1.0

    def _pick_object_at(self, x: float, y: float) -> _ObjectRow | None:
        # English comments inside code.
        nearest: tuple[float, _ObjectRow] | None = None
        for obj in self._objects:
            if obj.object_type == "Border segment":
                x0 = float(obj.x or 0.0)
                y0 = float(obj.y or 0.0)
                x1 = float(obj.x2 or 0.0)
                y1 = float(obj.y2 or 0.0)
                dx = x1 - x0
                dy = y1 - y0
                segment_len_sq = dx * dx + dy * dy
                if segment_len_sq <= 0:
                    continue
                t = max(0.0, min(1.0, ((x - x0) * dx + (y - y0) * dy) / segment_len_sq))
                px = x0 + t * dx
                py = y0 + t * dy
                distance = math.hypot(x - px, y - py)
                tolerance = max(float(obj.width or 0.001) * 3.0, 0.008)
                if distance <= tolerance and (
                    nearest is None or distance < nearest[0]
                ):
                    nearest = (distance, obj)
                continue

            ox = float(obj.x or 0.0)
            oy = float(obj.y or 0.0)
            radius = max(float(obj.radius or 0.008), 0.004)
            distance = math.hypot(x - ox, y - oy)
            if distance <= radius and (nearest is None or distance < nearest[0]):
                nearest = (distance, obj)

        return None if nearest is None else nearest[1]

    def _on_tap(self, event: Tap) -> None:
        # English comments inside code.
        x = round(float(event.x), 4)
        y = round(float(event.y), 4)
        if self.select_mode.value:
            selected = self._pick_object_at(x, y)
            if selected is None:
                self.status.object = "No object found at that location."
                return
            self._set_selected_object(selected.object_id)
            self.status.object = f'Selected "{selected.object_id}" from canvas.'
            return
        if not self._inside_arena(x, y):
            self.status.object = "Click inside arena bounds."
            return

        object_type = self.object_type.value
        if object_type == "Border segment":
            self._tap_border(x, y)
            return
        self._add_point_object(
            object_type=object_type,
            x=x,
            y=y,
            radius=round(float(self.object_radius.value) / 1000.0, 4),
            color=self.object_color.value,
        )

    def _tap_border(self, x: float, y: float) -> None:
        # English comments inside code.
        if self._border_start is None:
            self._border_start = (x, y)
            self._show_border_preview(x=x, y=y, color=self.object_color.value)
            self._update_insert_hint()
            return
        x0, y0 = self._border_start
        self._border_start = None
        self._clear_border_preview()
        self._add_border_object(
            x0=x0,
            y0=y0,
            x1=x,
            y1=y,
            width=round(float(self.border_width.value) / 1000.0, 4),
            color=self.object_color.value,
        )
        self._update_insert_hint()

    def _next_id(self, prefix: str) -> str:
        # English comments inside code.
        object_id = f"{prefix}_{self._counter:03d}"
        self._counter += 1
        return object_id

    def _add_point_object(
        self, *, object_type: str, x: float, y: float, radius: float, color: str
    ) -> None:
        # English comments inside code.
        if object_type == "Food patch":
            object_id = self._next_id("food")
            self._append_source_row(
                self.food_source,
                {"x": x, "y": y, "r": radius, "color": color, "id": object_id},
            )
        else:
            object_id = self._next_id("obstacle")
            self._append_source_row(
                self.obstacle_source,
                {"x": x, "y": y, "r": radius, "color": color, "id": object_id},
            )

        self._objects.append(
            _ObjectRow(
                object_id=object_id,
                object_type=object_type,
                x=x,
                y=y,
                radius=radius,
                color=color,
                amount=3.0 if object_type == "Food patch" else None,
                odor_id=f"{object_id}_odor" if object_type == "Food patch" else None,
                odor_intensity=1.0 if object_type == "Food patch" else None,
                odor_spread=0.02 if object_type == "Food patch" else None,
                substrate_type="standard" if object_type == "Food patch" else None,
                substrate_quality=1.0 if object_type == "Food patch" else None,
            )
        )
        self.status.object = f"Added {object_type.lower()} at ({x:.3f}, {y:.3f})."
        self._refresh_table()
        self._refresh_object_controls(selected_object_id=object_id)

    def _add_border_object(
        self, *, x0: float, y0: float, x1: float, y1: float, width: float, color: str
    ) -> None:
        # English comments inside code.
        object_id = self._next_id("border")
        self._append_source_row(
            self.border_source,
            {
                "x0": x0,
                "y0": y0,
                "x1": x1,
                "y1": y1,
                "w": max(1, int(width * 1500)),
                "color": color,
                "id": object_id,
            },
        )
        self._objects.append(
            _ObjectRow(
                object_id=object_id,
                object_type="Border segment",
                x=x0,
                y=y0,
                x2=x1,
                y2=y1,
                width=width,
                color=color,
            )
        )
        self.status.object = (
            f"Added border segment from ({x0:.3f}, {y0:.3f}) to ({x1:.3f}, {y1:.3f})."
        )
        self._refresh_table()
        self._refresh_object_controls(selected_object_id=object_id)

    def _show_border_preview(self, *, x: float, y: float, color: str) -> None:
        # English comments inside code.
        self.border_preview_source.data = {"x": [x], "y": [y], "color": [color]}

    def _clear_border_preview(self) -> None:
        # English comments inside code.
        self.border_preview_source.data = {"x": [], "y": [], "color": []}

    def _append_source_row(
        self, source: ColumnDataSource, row: dict[str, object]
    ) -> None:
        # English comments inside code.
        data = {key: list(value) for key, value in source.data.items()}
        for key, value in row.items():
            data[key].append(value)
        source.data = data

    def _on_clear_last(self, _: object) -> None:
        # English comments inside code.
        if self._border_start is not None:
            self._border_start = None
            self._clear_border_preview()
            self._update_insert_hint()
            self.status.object = "Cancelled pending border segment."
            return
        if not self._objects:
            self.status.object = "Nothing to undo."
            return
        self._objects.pop()
        self._rebuild_sources()
        self._refresh_table()
        self._refresh_object_controls()
        self.status.object = "Removed last object."

    def _on_clear_all(self, _: object) -> None:
        # English comments inside code.
        self._objects.clear()
        self._border_start = None
        self._counter = 1
        self._clear_border_preview()
        self.food_source.data = {"x": [], "y": [], "r": [], "color": [], "id": []}
        self.obstacle_source.data = {"x": [], "y": [], "r": [], "color": [], "id": []}
        self.border_source.data = {
            "x0": [],
            "y0": [],
            "x1": [],
            "y1": [],
            "w": [],
            "color": [],
            "id": [],
        }
        self._refresh_table()
        self._refresh_object_controls()
        self._update_insert_hint()
        self.status.object = "Cleared all placed objects."

    def _rebuild_sources(self) -> None:
        # English comments inside code.
        self._clear_border_preview()
        self.food_source.data = {"x": [], "y": [], "r": [], "color": [], "id": []}
        self.obstacle_source.data = {"x": [], "y": [], "r": [], "color": [], "id": []}
        self.border_source.data = {
            "x0": [],
            "y0": [],
            "x1": [],
            "y1": [],
            "w": [],
            "color": [],
            "id": [],
        }
        for obj in self._objects:
            if obj.object_type == "Food patch":
                self._append_source_row(
                    self.food_source,
                    {
                        "x": obj.x,
                        "y": obj.y,
                        "r": obj.radius,
                        "color": obj.color,
                        "id": obj.object_id,
                    },
                )
            elif obj.object_type == "Obstacle":
                self._append_source_row(
                    self.obstacle_source,
                    {
                        "x": obj.x,
                        "y": obj.y,
                        "r": obj.radius,
                        "color": obj.color,
                        "id": obj.object_id,
                    },
                )
            else:
                self._append_source_row(
                    self.border_source,
                    {
                        "x0": obj.x,
                        "y0": obj.y,
                        "x1": obj.x2,
                        "y1": obj.y2,
                        "w": max(1, int((obj.width or 0.001) * 1500)),
                        "color": obj.color,
                        "id": obj.object_id,
                    },
                )

    def _refresh_table(self) -> None:
        # English comments inside code.
        rows = [
            {
                "id": obj.object_id,
                "type": obj.object_type,
                "x": obj.x,
                "y": obj.y,
                "x2": obj.x2,
                "y2": obj.y2,
                "radius": obj.radius,
                "width": obj.width,
                "color": obj.color,
                "amount": obj.amount,
                "odor_id": obj.odor_id,
            }
            for obj in self._objects
        ]
        self.table.value = pd.DataFrame(rows)

    def _build_export_config(self) -> dict[str, object]:
        # English comments inside code.
        source_units: dict[str, dict[str, object]] = {}
        border_list: dict[str, dict[str, object]] = {}
        obstacles: dict[str, dict[str, object]] = {}

        for obj in self._objects:
            if obj.object_type == "Food patch":
                source_units[obj.object_id] = {
                    "pos": [obj.x, obj.y],
                    "radius": obj.radius,
                    "amount": obj.amount if obj.amount is not None else 3.0,
                    "odor": {
                        "id": obj.odor_id or f"{obj.object_id}_odor",
                        "intensity": obj.odor_intensity if obj.odor_intensity is not None else 1.0,
                        "spread": obj.odor_spread if obj.odor_spread is not None else 0.02,
                    },
                    "substrate": {
                        "type": obj.substrate_type or "standard",
                        "quality": obj.substrate_quality
                        if obj.substrate_quality is not None
                        else 1.0,
                    },
                    "color": obj.color,
                }
            elif obj.object_type == "Obstacle":
                obstacles[obj.object_id] = {
                    "pos": [obj.x, obj.y],
                    "radius": obj.radius,
                    "color": obj.color,
                }
            elif obj.object_type == "Border segment":
                border_list[obj.object_id] = {
                    "vertices": [[obj.x, obj.y], [obj.x2, obj.y2]],
                    "width": obj.width,
                    "color": obj.color,
                }

        return {
            "arena": {
                "geometry": self.arena_shape.value,
                "dims": [self.arena_width.value, self.arena_height.value],
            },
            "food_params": {
                "source_units": source_units,
                "source_groups": {},
                "food_grid": {},
            },
            "border_list": border_list,
            "obstacles": obstacles,
        }

    def _export_json(self) -> io.StringIO:
        # English comments inside code.
        payload = self._build_export_config()
        return io.StringIO(json.dumps(payload, indent=2))


def environment_builder_app() -> pn.viewable.Viewable:
    # English comments inside code.
    pn.extension("tabulator", raw_css=[PORTAL_RAW_CSS, ENV_BUILDER_RAW_CSS])
    controller = _EnvironmentBuilderController()

    template = pn.template.MaterialTemplate(
        title="",
        header_background=LANE_MODELS_COLOR,
        header_color="#1f1f1f",
    )
    template.header.append(build_app_header(title="Environment Builder"))
    template.main.append(controller.view())
    return template
