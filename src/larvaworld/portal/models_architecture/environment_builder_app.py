from __future__ import annotations

import io
import json
from dataclasses import dataclass

import pandas as pd
import panel as pn
from bokeh.events import Tap
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure

from larvaworld.portal.landing_registry import DOCS_ARENAS_SUBSTRATES
from larvaworld.portal.panel_components import PORTAL_RAW_CSS, build_app_header


LANE_MODELS_COLOR = "#c1b0c2"
LANE_MODELS_COLOR_DARK = "#5a4760"

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


class _EnvironmentBuilderController:
    # English comments inside code.
    def __init__(self) -> None:
        self._objects: list[_ObjectRow] = []
        self._border_start: tuple[float, float] | None = None
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
        self.clear_last_btn = pn.widgets.Button(name="Undo last", button_type="default")
        self.clear_all_btn = pn.widgets.Button(name="Clear all", button_type="warning")
        self.export_btn = pn.widgets.FileDownload(
            name="",
            label="Download JSON",
            button_type="primary",
            callback=self._export_json,
            filename="environment_builder_config.json",
        )
        self.clear_last_btn.width = 100
        self.clear_all_btn.width = 90
        self.export_btn.width = 220
        self.status = pn.pane.Markdown("Click on the canvas to place an object.")
        self.table = pn.pane.DataFrame(
            pd.DataFrame(
                columns=["id", "type", "x", "y", "x2", "y2", "radius", "width", "color"]
            ),
            index=False,
            height=620,
            sizing_mode="stretch_width",
        )

        self.food_source = ColumnDataSource(
            {"x": [], "y": [], "r": [], "color": [], "id": []}
        )
        self.obstacle_source = ColumnDataSource(
            {"x": [], "y": [], "r": [], "color": [], "id": []}
        )
        self.border_source = ColumnDataSource(
            {"x0": [], "y0": [], "x1": [], "y1": [], "w": [], "color": [], "id": []}
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
            source=self.obstacle_source,
            line_color="color",
            fill_color=None,
            line_width=2,
            legend_label="Obstacles",
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
        self.clear_last_btn.on_click(self._on_clear_last)
        self.clear_all_btn.on_click(self._on_clear_all)

        self._update_insert_hint()

    def view(self) -> pn.viewable.Viewable:
        # English comments inside code.
        intro = pn.pane.Markdown(
            (
                "### Environment Builder\n"
                "Design arena geometry, place food patches, draw borders, and export a JSON config. "
                f"Reference: [Arenas and Substrates]({DOCS_ARENAS_SUBSTRATES})."
            ),
            css_classes=["lw-env-builder-intro"],
            margin=0,
        )
        divider = pn.pane.HTML('<div class="lw-env-builder-divider"></div>', margin=0)
        primary_actions = pn.Row(
            self.clear_last_btn,
            self.clear_all_btn,
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
            self.object_type,
            self.object_radius,
            self.border_width,
            self.object_color,
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
        side = pn.Column(controls, width=360, sizing_mode="fixed")

        canvas = pn.pane.Bokeh(self.fig, sizing_mode="stretch_both")
        right = pn.Column(table_card, width=360, sizing_mode="fixed")
        main = pn.Row(side, canvas, right, sizing_mode="stretch_width")

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

    def _on_tap(self, event: Tap) -> None:
        # English comments inside code.
        x = round(float(event.x), 4)
        y = round(float(event.y), 4)
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
            )
        )
        self.status.object = f"Added {object_type.lower()} at ({x:.3f}, {y:.3f})."
        self._refresh_table()

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
            }
            for obj in self._objects
        ]
        self.table.object = pd.DataFrame(rows)

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
                    "amount": 3.0,
                    "odor": {
                        "id": f"{obj.object_id}_odor",
                        "intensity": 1.0,
                        "spread": 0.02,
                    },
                    "substrate": {"type": "standard", "quality": 1.0},
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
    pn.extension(raw_css=[PORTAL_RAW_CSS, ENV_BUILDER_RAW_CSS])
    controller = _EnvironmentBuilderController()

    template = pn.template.MaterialTemplate(
        title="",
        header_background=LANE_MODELS_COLOR,
        header_color="#1f1f1f",
    )
    template.header.append(build_app_header(title="Environment Builder"))
    template.main.append(controller.view())
    return template
