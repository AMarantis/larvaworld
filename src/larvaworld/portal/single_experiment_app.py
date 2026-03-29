from __future__ import annotations

import json
import re
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Any

import holoviews as hv
import panel as pn

from larvaworld.lib import reg, screen, sim, util
from larvaworld.portal.landing_registry import (
    DOCS_EXPERIMENT_TYPES,
    DOCS_SINGLE_EXPERIMENTS,
)
from larvaworld.portal.panel_components import PORTAL_RAW_CSS, build_app_header
from larvaworld.portal.workspace import WorkspaceError, get_workspace_dir


__all__ = [
    "_SingleExperimentController",
    "_default_run_name",
    "_editor_group_title",
    "_safe_slug",
    "single_experiment_app",
]


SINGLE_EXPERIMENT_RAW_CSS = """
.lw-single-exp-root {
  padding: 14px 12px 20px 12px;
}

.lw-single-exp-intro {
  border-left: 4px solid #7aa6c2;
  background: rgba(122, 166, 194, 0.16);
  border-radius: 10px;
  padding: 10px 12px;
  margin: 0 0 10px 0;
}

.lw-single-exp-intro a {
  color: #284b63;
}

.lw-single-exp-actions {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  width: 100%;
}

.lw-single-exp-actions > * {
  width: 100% !important;
  min-width: 0 !important;
}

.lw-single-exp-preview-placeholder {
  padding: 22px 20px;
  border: 1px dashed rgba(17, 17, 17, 0.18);
  border-radius: 12px;
  background: rgba(248, 250, 252, 0.9);
  color: rgba(17, 17, 17, 0.72);
  line-height: 1.55;
}

.lw-single-exp-preview-meta {
  font-size: 12px;
  line-height: 1.55;
  color: rgba(17, 17, 17, 0.78);
  background: rgba(193, 176, 194, 0.12);
  border-left: 3px solid #c1b0c2;
  border-radius: 8px;
  padding: 8px 10px;
  margin: 0 0 8px 0;
}

.lw-single-exp-summary {
  font-size: 12px;
  line-height: 1.55;
  color: rgba(17, 17, 17, 0.76);
  padding: 0 6px;
}

.lw-single-exp-status {
  font-size: 12px;
  line-height: 1.55;
}

.lw-single-exp-params {
  font-size: 12px;
  line-height: 1.45;
}

.lw-single-exp-params-group .bk-input,
.lw-single-exp-params-group textarea,
.lw-single-exp-params-group .bk-input-group {
  font-size: 12px;
}

.lw-single-exp-param-sequence {
  margin-bottom: 8px;
}

.lw-single-exp-param-sequence-label {
  font-size: 12px;
  font-weight: 600;
  color: rgba(17, 17, 17, 0.78);
  margin: 0 0 4px 0;
}
""".strip()

_EDITOR_EXCLUDED_PATHS = {"experiment"}
_ARENA_GEOMETRY_OPTIONS = ["circular", "rectangular"]
_SPATIAL_DISTRO_MODE_OPTIONS = ["uniform", "normal", "periphery", "grid"]
_SPATIAL_DISTRO_SHAPE_OPTIONS = ["circle", "rect", "oval", "rectangular"]
_ENRICHMENT_MODE_OPTIONS = ["minimal", "full"]
_ENRICHMENT_PROC_KEY_OPTIONS = ["angular", "spatial", "source", "PI", "wind"]
_ENRICHMENT_ANOT_KEY_OPTIONS = [
    "bout_detection",
    "bout_distribution",
    "interference",
    "source_attraction",
    "patch_residency",
]
_ODORSCAPE_OPTIONS = ["Analytical", "Gaussian", "Diffusion"]


def _safe_slug(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "_", value.strip()).strip("._-")
    return cleaned or "single_experiment"


def _default_run_name(experiment_id: str) -> str:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{_safe_slug(experiment_id)}_{stamp}"


def _editor_group_title(key: str) -> str:
    return key.replace("_", " ").title()


def _editor_field_title(path: str) -> str:
    return path.replace("_", " ").replace(".", " / ").title()


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if hasattr(value, "item") and callable(getattr(value, "item")):
        try:
            return value.item()
        except Exception:
            return str(value)
    return value


def _normalize_scalar(value: Any) -> Any:
    if isinstance(value, tuple):
        return tuple(_normalize_scalar(item) for item in value)
    if isinstance(value, list):
        return [_normalize_scalar(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _normalize_scalar(item) for key, item in value.items()}
    if isinstance(value, Path):
        return str(value)
    if hasattr(value, "item") and callable(getattr(value, "item")):
        try:
            return value.item()
        except Exception:
            return str(value)
    return value


class _ExperimentPreview:
    def __init__(
        self,
        launcher: sim.ExpRun,
        *,
        size: int = 620,
        preview_step_cap: int = 300,
    ) -> None:
        self.launcher = launcher
        self.size = size
        self.draw_ops = screen.AgentDrawOps(draw_centroid=True, draw_segs=False)
        preview_steps = max(2, min(int(self.launcher.p.steps), preview_step_cap))
        self.launcher.sim_setup(steps=preview_steps)
        self.Nfade = max(1, int(self.draw_ops.trail_dt / self.launcher.dt))
        self.env = self.launcher.p.env_params
        xdim, ydim = self.env.arena.dims
        self.image_kws = {
            "title": "Arena preview",
            "xlim": (-xdim / 2, xdim / 2),
            "ylim": (-ydim / 2, ydim / 2),
            "width": self.size,
            "height": int(self.size * ydim / xdim) if xdim else self.size,
            "xlabel": "X (m)",
            "ylabel": "Y (m)",
        }
        self.progress_bar = pn.widgets.Progress(
            name="Simulation timestep",
            bar_color="primary",
            width=int(self.size / 2),
            max=self.launcher.Nsteps - 1,
            value=self.launcher.t,
        )
        self.time_slider = pn.widgets.Player(
            name="Tick",
            width=int(self.size / 2),
            start=0,
            end=preview_steps - 1,
            interval=max(int(1000 * self.launcher.dt), 1),
            value=0,
        )
        self.tank_plot = self._get_tank_plot()

    def _get_tank_plot(self) -> hv.element.Overlay:
        arena = self.env.arena
        if arena.geometry == "circular":
            return hv.Ellipse(0, 0, arena.dims[0]).opts(
                line_width=5,
                bgcolor="lightgrey",
            )
        if arena.geometry == "rectangular":
            return hv.Box(0, 0, spec=arena.dims).opts(
                line_width=5,
                bgcolor="lightgrey",
            )
        raise ValueError(f"Unsupported arena geometry: {arena.geometry}")

    def _draw_overlay(self) -> hv.Overlay:
        agents = self.launcher.agents
        sources = self.launcher.sources
        draw_layers = util.AttrDict(
            {
                "draw_segs": hv.Overlay(
                    [
                        hv.Polygons([seg.vertices for seg in agent.segs]).opts(
                            color=agent.color
                        )
                        for agent in agents
                    ]
                ),
                "draw_centroid": hv.Points(agents.get_position()).opts(
                    size=5,
                    color="black",
                ),
                "draw_head": hv.Points(agents.head.front_end).opts(
                    size=5,
                    color="red",
                ),
                "draw_midline": hv.Overlay(
                    [
                        hv.Path(agent.midline_xy).opts(color="blue", line_width=2)
                        for agent in agents
                    ]
                ),
                "visible_trails": hv.Contours(
                    [agent.trajectory[-self.Nfade :] for agent in agents]
                ).opts(color="black"),
            }
        )
        source_layers = [
            hv.Ellipse(source.pos[0], source.pos[1], source.radius * 2).opts(
                line_width=5,
                color=source.color,
                bgcolor=source.color,
            )
            for source in sources
        ]
        agent_layers = [
            layer for key, layer in draw_layers.items() if getattr(self.draw_ops, key)
        ]
        return hv.Overlay([self.tank_plot] + source_layers + agent_layers).opts(
            responsive=False,
            **self.image_kws,
        )

    def view(self) -> pn.viewable.Viewable:
        @pn.depends(i=self.time_slider)
        def _image(i: int) -> hv.Overlay:
            while i > self.launcher.t:
                self.launcher.sim_step()
                self.progress_bar.value = self.launcher.t
            return self._draw_overlay()

        preview = hv.DynamicMap(_image)
        return pn.Row(
            preview,
            pn.Column(
                pn.Row(pn.Column("Tick", self.time_slider)),
                pn.Row(pn.Column("Simulation timestep", self.progress_bar)),
                pn.Param(self.draw_ops),
            ),
            sizing_mode="stretch_width",
        )


class _SingleExperimentController:
    def __init__(self) -> None:
        experiment_ids = list(reg.conf.Exp.confIDs)
        default_experiment = "dish" if "dish" in experiment_ids else experiment_ids[0]
        self.experiment = pn.widgets.Select(
            name="Experiment template",
            value=default_experiment,
            options=experiment_ids,
        )
        self.run_name = pn.widgets.TextInput(
            name="Run name",
            value=_default_run_name(self.experiment.value),
        )
        self.environment_select = pn.widgets.Select(
            name="Environment preset",
            options={},
            value="__template__",
        )
        self.refresh_environments_btn = pn.widgets.Button(
            name="Refresh environments",
            button_type="default",
        )
        self.prepare_btn = pn.widgets.Button(
            name="Prepare preview",
            button_type="primary",
        )
        self.summary = pn.pane.HTML("", sizing_mode="stretch_width", margin=(0, 0, 4, 0))
        self.parameter_group = pn.widgets.Select(
            name="Parameter group",
            options=[],
            value=None,
        )
        self.parameters_editor = pn.Column(
            css_classes=["lw-single-exp-params"],
            sizing_mode="stretch_width",
            margin=0,
        )
        self._parameter_groups: dict[str, list[str]] = {}
        self._parameter_widgets: dict[str, tuple[str, Any]] = {}
        self._parameter_widget_specs: dict[str, tuple[str, Any, pn.viewable.Viewable]] = {}
        self.status = pn.pane.Markdown("", css_classes=["lw-single-exp-status"])
        self.preview_meta = pn.pane.HTML("", css_classes=["lw-single-exp-preview-meta"])
        self.preview = pn.Column(
            pn.pane.HTML(
                (
                    '<div class="lw-single-exp-preview-placeholder">'
                    "Choose an experiment template, optionally apply a workspace environment preset, "
                    "and prepare the simulation preview here."
                    "</div>"
                ),
                margin=0,
            ),
            sizing_mode="stretch_width",
        )

        self.experiment.param.watch(self._on_experiment_change, "value")
        self.environment_select.param.watch(self._on_parameter_override_change, "value")
        self.parameter_group.param.watch(self._on_parameter_group_change, "value")
        self.refresh_environments_btn.on_click(self._on_refresh_environments)
        self.prepare_btn.on_click(self._on_prepare_preview)

        self._refresh_environment_options()
        self._refresh_summary()
        self._refresh_parameter_editor()
        self.status.object = "Select a template and prepare a single-run preview."

    def _environment_dir(self) -> Path:
        return get_workspace_dir("environments")

    def _experiment_dir(self) -> Path:
        return get_workspace_dir("experiments")

    def _environment_options(self) -> dict[str, str]:
        options = {"Template default environment": "__template__"}
        preset_dir = self._environment_dir()
        preset_dir.mkdir(parents=True, exist_ok=True)
        for path in sorted(preset_dir.glob("*.json")):
            options[path.stem] = path.name
        return options

    def _load_selected_environment(self) -> util.AttrDict | None:
        selected = self.environment_select.value
        if selected in {None, "", "__template__"}:
            return None
        preset_path = self._environment_dir() / str(selected)
        payload = json.loads(preset_path.read_text(encoding="utf-8"))
        return util.AttrDict(payload)

    def _build_parameters(self) -> util.AttrDict:
        parameters = reg.conf.Exp.getID(self.experiment.value).get_copy()
        parameters["duration"] = float(parameters.get("duration", 5.0))
        environment_payload = self._load_selected_environment()
        if environment_payload is not None:
            env_params = util.AttrDict(parameters.env_params).get_copy()
            parameters["env_params"] = env_params.update_existingnestdict(
                environment_payload.flatten()
            )
        flat = parameters.flatten()
        for path, (kind, widget) in self._parameter_widgets.items():
            flat[path] = self._parse_widget_value(kind, widget)
        return util.AttrDict(flat.unflatten())

    def _refresh_environment_options(self) -> None:
        try:
            options = self._environment_options()
        except WorkspaceError as exc:
            self.environment_select.options = {"Workspace unavailable": "__template__"}
            self.environment_select.value = "__template__"
            self.environment_select.disabled = True
            self.refresh_environments_btn.disabled = True
            self.status.object = f"Cannot load workspace environment presets: {exc}"
            return
        selected = self.environment_select.value
        self.environment_select.options = options
        self.environment_select.disabled = False
        self.refresh_environments_btn.disabled = False
        self.environment_select.value = (
            selected if selected in options.values() else "__template__"
        )

    def _refresh_summary(self) -> None:
        parameters = reg.conf.Exp.getID(self.experiment.value).get_copy()
        larva_groups = list(parameters.get("larva_groups", {}).keys())
        env = util.AttrDict(parameters.env_params)
        epochs = parameters.get("trials", {}).get("epochs", {})
        self.summary.object = (
            '<div class="lw-single-exp-summary">'
            f"<strong>Template:</strong> <code>{self.experiment.value}</code><br>"
            f"<strong>Default duration:</strong> {float(parameters.get('duration', 0.0)):.2f} min<br>"
            f"<strong>Arena geometry:</strong> {env.arena.geometry}<br>"
            f"<strong>Larva groups:</strong> {', '.join(larva_groups) if larva_groups else 'None'}<br>"
            f"<strong>Epochs:</strong> {len(epochs)}<br>"
            "<strong>Parameter editing:</strong> all resolved experiment parameters are editable below."
            "</div>"
        )

    def _editable_flat_parameters(self) -> util.AttrDict:
        parameters = reg.conf.Exp.getID(self.experiment.value).get_copy()
        environment_payload = self._load_selected_environment()
        if environment_payload is not None:
            env_params = util.AttrDict(parameters.env_params).get_copy()
            parameters["env_params"] = env_params.update_existingnestdict(
                environment_payload.flatten()
            )
        flat = parameters.flatten()
        filtered = util.AttrDict()
        for path, value in flat.items():
            if path in _EDITOR_EXCLUDED_PATHS:
                continue
            filtered[path] = _normalize_scalar(value)
        return filtered

    @staticmethod
    def _options_for_path(path: str, value: Any) -> tuple[str, list[Any]] | None:
        if path == "collections":
            return "multi", list(reg.parDB.output_keys)
        if path == "enrichment.proc_keys":
            return "multi", list(_ENRICHMENT_PROC_KEY_OPTIONS)
        if path == "enrichment.anot_keys":
            return "multi", list(_ENRICHMENT_ANOT_KEY_OPTIONS)
        if path.endswith("arena.geometry"):
            return "single", list(_ARENA_GEOMETRY_OPTIONS)
        if path.endswith("distribution.mode"):
            return "single", list(_SPATIAL_DISTRO_MODE_OPTIONS)
        if path.endswith("distribution.shape"):
            return "single", list(_SPATIAL_DISTRO_SHAPE_OPTIONS)
        if path == "enrichment.mode":
            return "single", list(_ENRICHMENT_MODE_OPTIONS)
        if path == "env_params.odorscape":
            return "single_optional", [None] + list(_ODORSCAPE_OPTIONS)
        return None

    @staticmethod
    def _widget_for_value(path: str, value: Any) -> tuple[str, Any, pn.viewable.Viewable]:
        label = _editor_field_title(path.split(".", 1)[1] if "." in path else path)
        options = _SingleExperimentController._options_for_path(path, value)
        if options is not None:
            mode, option_values = options
            if mode == "multi":
                widget = pn.widgets.MultiChoice(
                    name=label,
                    value=list(value or []),
                    options=option_values,
                    sizing_mode="stretch_width",
                )
                return "multichoice", widget, widget
            normalized_options = ["None" if item is None else item for item in option_values]
            selected_value = "None" if value is None else value
            widget = pn.widgets.Select(
                name=label,
                value=selected_value if selected_value in normalized_options else normalized_options[0],
                options=normalized_options,
                sizing_mode="stretch_width",
            )
            return "option", widget, widget
        if isinstance(value, bool):
            widget = pn.widgets.Checkbox(name=label, value=value)
            return "bool", widget, widget
        if isinstance(value, int):
            widget = pn.widgets.IntInput(
                name=label,
                value=value,
                step=1,
                sizing_mode="stretch_width",
            )
            return "int", widget, widget
        if isinstance(value, float):
            widget = pn.widgets.FloatInput(
                name=label,
                value=value,
                step=0.1,
                sizing_mode="stretch_width",
            )
            return "float", widget, widget
        if (
            isinstance(value, (list, tuple))
            and 1 <= len(value) <= 4
            and all(isinstance(item, (int, float)) for item in value)
        ):
            scalar_kind = "int" if all(isinstance(item, int) for item in value) else "float"
            subwidgets: list[pn.viewable.Viewable] = []
            for index, item in enumerate(value, start=1):
                if scalar_kind == "int":
                    subwidgets.append(
                        pn.widgets.IntInput(
                            name=f"{index}",
                            value=int(item),
                            step=1,
                            width=86,
                        )
                    )
                else:
                    subwidgets.append(
                        pn.widgets.FloatInput(
                            name=f"{index}",
                            value=float(item),
                            step=0.1,
                            width=86,
                        )
                    )
            view = pn.Column(
                pn.pane.HTML(
                    f'<div class="lw-single-exp-param-sequence-label">{label}</div>',
                    margin=0,
                ),
                pn.Row(*subwidgets, sizing_mode="stretch_width", margin=0),
                css_classes=["lw-single-exp-param-sequence"],
                sizing_mode="stretch_width",
                margin=0,
            )
            control = {
                "widgets": subwidgets,
                "container": tuple if isinstance(value, tuple) else list,
                "scalar_kind": scalar_kind,
            }
            return "sequence", control, view
        if isinstance(value, str):
            widget = pn.widgets.TextInput(
                name=label,
                value=value,
                sizing_mode="stretch_width",
            )
            return "str", widget, widget
        if value is None:
            widget = pn.widgets.TextAreaInput(
                name=label,
                value="null",
                min_height=90,
                sizing_mode="stretch_width",
            )
            return "json", widget, widget
        widget = pn.widgets.TextAreaInput(
            name=label,
            value=json.dumps(_json_ready(value), indent=2, ensure_ascii=False),
            min_height=110,
            sizing_mode="stretch_width",
        )
        return "json", widget, widget

    @staticmethod
    def _parse_widget_value(kind: str, control: Any) -> Any:
        if kind == "sequence":
            scalar_kind = control["scalar_kind"]
            parsed = []
            for widget in control["widgets"]:
                value = getattr(widget, "value")
                parsed.append(int(value) if scalar_kind == "int" else float(value))
            return control["container"](parsed)
        value = getattr(control, "value")
        if kind == "bool":
            return bool(value)
        if kind == "int":
            return int(value)
        if kind == "float":
            return float(value)
        if kind == "str":
            return str(value)
        if kind == "option":
            return None if value == "None" else value
        if kind == "multichoice":
            return list(value)
        raw = str(value).strip()
        return json.loads(raw if raw else "null")

    def _render_parameter_group(self) -> None:
        group_key = self.parameter_group.value
        paths = self._parameter_groups.get(group_key, [])
        if not paths:
            self.parameters_editor[:] = []
            return
        self.parameters_editor[:] = [
            self._parameter_widget_specs[path][2] for path in paths
        ]

    def _refresh_parameter_editor(self) -> None:
        flat = self._editable_flat_parameters()
        self._parameter_widget_specs = {}
        grouped: dict[str, list[str]] = {}
        self._parameter_widgets = {}
        for path, value in flat.items():
            group_key = path.split(".", 1)[0]
            kind, control, view = self._widget_for_value(path, value)
            grouped.setdefault(group_key, []).append(path)
            self._parameter_widgets[path] = (kind, control)
            self._parameter_widget_specs[path] = (kind, control, view)
        self._parameter_groups = grouped
        options = {_editor_group_title(group): group for group in grouped.keys()}
        current_group = self.parameter_group.value
        self.parameter_group.options = options
        if current_group not in options.values():
            preferred = "env_params" if "env_params" in grouped else next(iter(grouped), None)
            self.parameter_group.value = preferred
        self._render_parameter_group()

    def _on_experiment_change(self, *_: object) -> None:
        self.run_name.value = _default_run_name(self.experiment.value)
        self._refresh_summary()
        self._refresh_parameter_editor()
        self.status.object = f'Template "{self.experiment.value}" loaded.'

    def _on_parameter_override_change(self, *_: object) -> None:
        self._refresh_parameter_editor()

    def _on_parameter_group_change(self, *_: object) -> None:
        self._render_parameter_group()

    def _on_refresh_environments(self, *_: object) -> None:
        self._refresh_environment_options()
        self._refresh_parameter_editor()
        self.status.object = "Refreshed workspace environment presets."

    def _build_run_directory(self) -> Path:
        run_id = _safe_slug(self.run_name.value or self.experiment.value)
        base_dir = self._experiment_dir()
        candidate = base_dir / run_id
        if not candidate.exists():
            return candidate
        suffix = 2
        while (base_dir / f"{run_id}_{suffix}").exists():
            suffix += 1
        return base_dir / f"{run_id}_{suffix}"

    @staticmethod
    def _preview_metadata_html(parameters: util.AttrDict, selected_env: str) -> str:
        env = util.AttrDict(parameters.env_params)
        larva_groups = util.AttrDict(parameters.get("larva_groups", {}))
        counts = []
        total = 0
        for group_id, group in larva_groups.items():
            try:
                count = int(group.distribution.N)
            except Exception:
                count = 0
            total += count
            counts.append(f"{group_id}: {count}")
        dims = getattr(env.arena, "dims", ("?", "?"))
        if isinstance(dims, (list, tuple)) and len(dims) >= 2:
            dims_text = f"{float(dims[0]):.3f} x {float(dims[1]):.3f} m"
        else:
            dims_text = str(dims)
        return (
            '<div class="lw-single-exp-preview-meta">'
            f"<strong>Applied preview config:</strong> "
            f"environment = {selected_env}; "
            f"arena = {env.arena.geometry} ({dims_text}); "
            f"duration = {float(parameters.duration):.2f} min; "
            f"larvae = {total}"
            + (f" ({', '.join(counts)})" if counts else "")
            + ".</div>"
        )

    def _finish_prepare_preview(
        self,
        parameters: util.AttrDict,
        run_dir: Path,
        selected_env: str,
    ) -> None:
        preview_parameters = parameters
        try:
            launcher = sim.ExpRun(
                experiment=self.experiment.value,
                parameters=preview_parameters,
                id=run_dir.name,
                dir=str(run_dir),
                store_data=False,
            )
            preview = _ExperimentPreview(launcher).view()
        except Exception as exc:
            if "get_polygon" in str(exc):
                preview_parameters = parameters.get_copy()
                preview_parameters["larva_collisions"] = True
                try:
                    launcher = sim.ExpRun(
                        experiment=self.experiment.value,
                        parameters=preview_parameters,
                        id=run_dir.name,
                        dir=str(run_dir),
                        store_data=False,
                    )
                    preview = _ExperimentPreview(launcher).view()
                except Exception:
                    pass
                else:
                    self.preview_meta.object = self._preview_metadata_html(
                        parameters, selected_env
                    )
                    self.preview[:] = [preview]
                    self.status.object = (
                        f'Prepared preview for "{self.experiment.value}" using {selected_env}. '
                        f'Planned experiment output directory: <code>{run_dir}</code>. '
                        "The interactive preview is capped to the first 300 steps for responsiveness. "
                        "Preview fallback disabled larva overlap elimination for this visualization."
                    )
                    return
            self.preview_meta.object = ""
            self.preview[:] = [
                pn.pane.HTML(
                    (
                        '<div class="lw-single-exp-preview-placeholder">'
                        f"Preview preparation failed: {exc}"
                        "</div>"
                    ),
                    margin=0,
                )
            ]
            self.status.object = f"Cannot prepare the single experiment preview: {exc}"
            return

        self.preview_meta.object = self._preview_metadata_html(parameters, selected_env)
        self.preview[:] = [preview]
        self.status.object = (
            f'Prepared preview for "{self.experiment.value}" using {selected_env}. '
            f'Planned experiment output directory: <code>{run_dir}</code>. '
            "The interactive preview is capped to the first 300 steps for responsiveness."
        )

    def _on_prepare_preview(self, *_: object) -> None:
        try:
            parameters = self._build_parameters()
            run_dir = self._build_run_directory()
        except (WorkspaceError, OSError, json.JSONDecodeError) as exc:
            self.status.object = f"Cannot prepare the single experiment preview: {exc}"
            return

        selected_env = (
            "template default"
            if self.environment_select.value == "__template__"
            else str(self.environment_select.value)
        )
        self.preview_meta.object = self._preview_metadata_html(parameters, selected_env)
        self.preview[:] = [
            pn.pane.HTML(
                (
                    '<div class="lw-single-exp-preview-placeholder">'
                    "Preparing preview. The simulation environment and agents are being initialized."
                    "</div>"
                ),
                margin=0,
            )
        ]
        self.status.object = (
            f'Preparing preview for "{self.experiment.value}" using {selected_env}.'
        )
        doc = pn.state.curdoc
        if doc is not None:
            doc.add_next_tick_callback(
                partial(self._finish_prepare_preview, parameters, run_dir, selected_env)
            )
        else:
            self._finish_prepare_preview(parameters, run_dir, selected_env)

    def view(self) -> pn.viewable.Viewable:
        intro = pn.pane.Markdown(
            (
                "### Single Experiment\n"
                "Prepare one Larvaworld `Exp` run in the portal: select an experiment template, "
                "optionally override its environment with a workspace preset, and inspect the arena "
                "dynamics in an interactive preview before broader simulation workflows are added. "
                f"References: [Single Experiments]({DOCS_SINGLE_EXPERIMENTS}) and "
                f"[Experiment Types]({DOCS_EXPERIMENT_TYPES})."
            ),
            css_classes=["lw-single-exp-intro"],
            margin=0,
        )
        controls = pn.Card(
            self.experiment,
            self.run_name,
            self.environment_select,
            self.summary,
            pn.Row(
                self.refresh_environments_btn,
                self.prepare_btn,
                css_classes=["lw-single-exp-actions"],
                sizing_mode="stretch_width",
                margin=0,
            ),
            self.status,
            title="Configuration",
            collapsed=False,
            width=360,
            sizing_mode="fixed",
        )
        preview = pn.Card(
            self.preview_meta,
            self.preview,
            title="Preview",
            collapsed=False,
            sizing_mode="stretch_both",
        )
        parameters = pn.Card(
            self.parameter_group,
            self.parameters_editor,
            title="Experiment Parameters",
            collapsed=False,
            width=420,
            sizing_mode="fixed",
            css_classes=["lw-single-exp-params-group"],
        )
        left_column = pn.Column(
            controls,
            parameters,
            width=420,
            sizing_mode="fixed",
        )
        return pn.Column(
            intro,
            pn.Row(left_column, preview, sizing_mode="stretch_width"),
            css_classes=["lw-single-exp-root"],
            sizing_mode="stretch_both",
        )


def single_experiment_app() -> pn.viewable.Viewable:
    pn.extension(raw_css=[PORTAL_RAW_CSS, SINGLE_EXPERIMENT_RAW_CSS])
    hv.extension("bokeh")
    controller = _SingleExperimentController()

    template = pn.template.MaterialTemplate(
        title="",
        header_background="#c1b0c2",
        header_color="#111111",
    )
    template.header.append(build_app_header(title="Single Experiment"))
    template.main.append(controller.view())
    return template
