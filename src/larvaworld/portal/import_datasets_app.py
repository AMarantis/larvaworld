from __future__ import annotations

from html import escape
from pathlib import Path

import panel as pn

from larvaworld.lib import reg
from larvaworld.portal.datasets.discovery import (
    RawDatasetCandidate,
    _candidate_import_overrides,
    discover_raw_datasets,
)
from larvaworld.portal.datasets.import_adapter import (
    build_workspace_proc_folder,
    import_into_workspace,
)
from larvaworld.portal.datasets.models import ImportRequest
from larvaworld.portal.panel_components import PORTAL_RAW_CSS, build_app_header
from larvaworld.portal.workspace import get_active_workspace


__all__ = ["_ImportDatasetsController", "import_datasets_app"]


IMPORT_DATASETS_RAW_CSS = """
.lw-import-datasets-root {
  padding: 14px 12px 20px 12px;
}

.lw-import-datasets-intro {
  border-left: 4px solid #7aa6c2;
  background: rgba(122, 166, 194, 0.16);
  border-radius: 10px;
  padding: 10px 12px;
  margin: 0 0 10px 0;
}

.lw-import-datasets-summary,
.lw-import-datasets-status {
  font-size: 12px;
  line-height: 1.5;
  border-radius: 10px;
  padding: 10px 12px;
  border: 1px solid rgba(17, 17, 17, 0.1);
  background: rgba(248, 250, 252, 0.94);
}

.lw-import-datasets-status--success {
  border-color: rgba(62,124,67,0.24);
  background: rgba(62,124,67,0.10);
}

.lw-import-datasets-status--warning {
  border-color: rgba(176,112,33,0.28);
  background: rgba(245,161,66,0.12);
}

.lw-import-datasets-status--danger {
  border-color: rgba(160,40,40,0.24);
  background: rgba(160,40,40,0.10);
}
""".strip()


def _status_html(text: str, *, tone: str = "neutral", detail: str | None = None) -> str:
    detail_html = ""
    if detail:
        detail_html = (
            '<div style="margin-top:4px;font-size:11px;opacity:0.84;word-break:break-word;">'
            f"{escape(detail)}"
            "</div>"
        )
    tone_class = ""
    if tone in {"success", "warning", "danger"}:
        tone_class = f" lw-import-datasets-status--{escape(tone)}"
    return (
        f'<div class="lw-import-datasets-status{tone_class}">'
        f"{escape(text)}"
        f"{detail_html}"
        "</div>"
    )


def _candidate_summary_html(candidate: RawDatasetCandidate | None) -> str:
    if candidate is None:
        return (
            '<div class="lw-import-datasets-summary">'
            "Select one discovered candidate to inspect its source path and warnings."
            "</div>"
        )
    warnings_html = (
        "<ul>"
        + "".join(f"<li>{escape(warning)}</li>" for warning in candidate.warnings)
        + "</ul>"
        if candidate.warnings
        else "<div>No warnings.</div>"
    )
    return (
        '<div class="lw-import-datasets-summary">'
        f"<div><strong>Candidate</strong>: {escape(candidate.candidate_id)}</div>"
        f"<div><strong>Parent dir</strong>: {escape(candidate.parent_dir)}</div>"
        f"<div><strong>Source path</strong>: {escape(str(candidate.source_path))}</div>"
        f'<div style="margin-top:6px;"><strong>Warnings</strong>:</div>{warnings_html}'
        "</div>"
    )


class _ImportDatasetsController:
    def __init__(self) -> None:
        self.workspace = get_active_workspace()
        self._candidate_by_key: dict[str, RawDatasetCandidate] = {}
        self._selected_record_path: Path | None = None

        self.lab_select = pn.widgets.Select(
            name="Lab format",
            options=self._lab_options(),
            value=self._default_lab_value(),
            width=260,
        )
        self.raw_root_input = pn.widgets.TextInput(
            name="Raw root",
            placeholder="/path/to/raw/data",
            width=520,
        )
        self.reset_button = pn.widgets.Button(
            name="Reset source",
            button_type="default",
            width=140,
        )
        self.discover_button = pn.widgets.Button(
            name="Discover datasets",
            button_type="primary",
            width=170,
        )
        self.candidate_select = pn.widgets.Select(
            name="Candidate",
            options={"Select a candidate": ""},
            value="",
            width=520,
        )
        self.dataset_id_input = pn.widgets.TextInput(name="Dataset ID", width=260)
        self.group_id_input = pn.widgets.TextInput(
            name="Group ID override", placeholder="optional", width=260
        )
        self.color_input = pn.widgets.TextInput(name="Color", value="black", width=160)
        self.import_button = pn.widgets.Button(
            name="Import into workspace",
            button_type="primary",
            width=180,
        )
        self.workspace_summary = pn.pane.HTML("", margin=0)
        self.candidate_summary = pn.pane.HTML(
            _candidate_summary_html(None), margin=(0, 0, 0, 0)
        )
        self.status = pn.pane.HTML("", margin=0)

        self.lab_select.param.watch(self._on_source_change, "value")
        self.raw_root_input.param.watch(self._on_source_change, "value")
        self.candidate_select.param.watch(self._on_candidate_change, "value")
        self.reset_button.on_click(self._handle_reset)
        self.discover_button.on_click(self._handle_discover)
        self.import_button.on_click(self._handle_import)

        self._refresh_workspace_summary()
        if self.workspace is None:
            self._set_status(
                "Configure an active workspace before importing datasets.",
                tone="warning",
            )
        else:
            self._set_status(
                "Choose a lab format and raw root, then discover one import candidate.",
                tone="neutral",
            )
        self._sync_controls()

    @staticmethod
    def _lab_options() -> dict[str, str]:
        return {lab_id: lab_id for lab_id in sorted(reg.conf.LabFormat.confIDs)}

    def _default_lab_value(self) -> str | None:
        options = self._lab_options()
        if not options:
            return None
        return next(iter(options.values()))

    def _active_workspace_ready(self) -> bool:
        return self.workspace is not None

    def _raw_root_text(self) -> str:
        return self.raw_root_input.value.strip()

    def _raw_root_path(self) -> Path | None:
        raw_text = self._raw_root_text()
        if not raw_text:
            return None
        return Path(raw_text).expanduser()

    def _selected_candidate(self) -> RawDatasetCandidate | None:
        return self._candidate_by_key.get(self.candidate_select.value)

    def _set_status(
        self, text: str, *, tone: str = "neutral", detail: str | None = None
    ) -> None:
        self.status.object = _status_html(text, tone=tone, detail=detail)

    def _refresh_workspace_summary(self) -> None:
        if self.workspace is None:
            self.workspace_summary.object = (
                '<div class="lw-import-datasets-summary">'
                "No active workspace is configured."
                "</div>"
            )
            return
        proc_root = None
        if self.lab_select.value:
            try:
                proc_root = build_workspace_proc_folder(
                    self.workspace, self.lab_select.value
                )
            except Exception:
                proc_root = None
        target_html = ""
        if proc_root is not None:
            target_html = (
                f"<div><strong>Import target</strong>: {escape(str(proc_root))}</div>"
            )
        self.workspace_summary.object = (
            '<div class="lw-import-datasets-summary">'
            f"<div><strong>Workspace</strong>: {escape(self.workspace.name)}</div>"
            f"<div><strong>Root</strong>: {escape(str(self.workspace.root))}</div>"
            f"{target_html}"
            "</div>"
        )

    def _candidate_option_key(self, candidate: RawDatasetCandidate) -> str:
        return (
            f"{candidate.parent_dir}::{candidate.candidate_id}::{candidate.source_path}"
        )

    def _clear_candidates(self) -> None:
        self._candidate_by_key.clear()
        self.candidate_select.options = {"Select a candidate": ""}
        self.candidate_select.value = ""
        self.dataset_id_input.value = ""
        self.candidate_summary.object = _candidate_summary_html(None)
        self._selected_record_path = None

    def _sync_controls(self) -> None:
        workspace_ready = self._active_workspace_ready()
        source_ready = bool(
            workspace_ready and self.lab_select.value and self._raw_root_text()
        )
        candidate_ready = self._selected_candidate() is not None
        self.discover_button.disabled = not source_ready
        self.candidate_select.disabled = not bool(self._candidate_by_key)
        self.dataset_id_input.disabled = not candidate_ready
        self.group_id_input.disabled = not candidate_ready
        self.color_input.disabled = not candidate_ready
        self.import_button.disabled = not (workspace_ready and candidate_ready)
        self.lab_select.disabled = (
            not bool(self.lab_select.options) or not workspace_ready
        )
        self.raw_root_input.disabled = not workspace_ready
        self.reset_button.disabled = not (
            workspace_ready and (self._raw_root_text() or self._candidate_by_key)
        )

    def _on_source_change(self, *_events) -> None:
        self._clear_candidates()
        self._refresh_workspace_summary()
        if self.workspace is not None:
            self._set_status(
                "Source changed. Discover datasets again to refresh the candidate list."
            )
        self._sync_controls()

    def _on_candidate_change(self, *_events) -> None:
        candidate = self._selected_candidate()
        if candidate is None:
            self.candidate_summary.object = _candidate_summary_html(None)
            self.dataset_id_input.value = ""
            self._sync_controls()
            return
        self.candidate_summary.object = _candidate_summary_html(candidate)
        self.dataset_id_input.value = candidate.candidate_id
        self._set_status(
            "Candidate selected. Review the import options and start the workspace import."
        )
        self._sync_controls()

    def _handle_reset(self, _event=None) -> None:
        self.raw_root_input.value = ""
        self.group_id_input.value = ""
        self.color_input.value = "black"
        self._clear_candidates()
        if self.workspace is not None:
            self._set_status(
                "Source state cleared. Enter a raw root path to start a new discovery pass."
            )
        self._sync_controls()

    def _handle_discover(self, _event=None) -> None:
        raw_root = self._raw_root_path()
        if self.workspace is None:
            self._set_status(
                "Configure an active workspace before importing datasets.",
                tone="warning",
            )
            self._sync_controls()
            return
        if raw_root is None:
            self._set_status("Enter a raw root path before discovery.", tone="warning")
            self._sync_controls()
            return
        candidates = discover_raw_datasets(self.lab_select.value, raw_root)
        self._clear_candidates()
        if not candidates:
            self._set_status(
                "No import candidates were found under the selected raw root.",
                tone="warning",
                detail=str(raw_root),
            )
            self._sync_controls()
            return
        options: dict[str, str] = {"Select a candidate": ""}
        for candidate in candidates:
            key = self._candidate_option_key(candidate)
            self._candidate_by_key[key] = candidate
            options[candidate.display_name] = key
        self.candidate_select.options = options
        self._set_status(
            f"Discovered {len(candidates)} candidate(s). Select one candidate to continue.",
            tone="success",
            detail=str(raw_root),
        )
        self._sync_controls()

    def _build_import_request(self) -> ImportRequest:
        candidate = self._selected_candidate()
        raw_root = self._raw_root_path()
        if candidate is None or raw_root is None:
            raise RuntimeError(
                "Import is not ready: select a discovered candidate first"
            )
        dataset_id = self.dataset_id_input.value.strip() or candidate.candidate_id
        group_id = self.group_id_input.value.strip() or None
        extra_kwargs = _candidate_import_overrides(
            self.lab_select.value,
            raw_root,
            candidate,
        )
        return ImportRequest(
            lab_id=self.lab_select.value,
            parent_dir=candidate.parent_dir,
            raw_folder=raw_root,
            group_id=group_id,
            dataset_id=dataset_id,
            color=self.color_input.value.strip() or "black",
            extra_kwargs=extra_kwargs,
        )

    def _handle_import(self, _event=None) -> None:
        if self.workspace is None:
            self._set_status(
                "Configure an active workspace before importing datasets.",
                tone="warning",
            )
            self._sync_controls()
            return
        try:
            request = self._build_import_request()
            record = import_into_workspace(request, workspace=self.workspace)
        except Exception as exc:
            self._set_status(str(exc), tone="danger")
            self._sync_controls()
            return
        self._selected_record_path = record.dataset_dir
        self._set_status(
            f'Dataset "{record.dataset_id}" imported into the active workspace.',
            tone="success",
            detail=str(record.dataset_dir),
        )
        self._sync_controls()

    def view(self) -> pn.viewable.Viewable:
        source_actions = pn.Row(
            self.discover_button,
            self.reset_button,
            sizing_mode="stretch_width",
        )
        source_section = pn.Card(
            pn.Column(
                self.lab_select,
                self.raw_root_input,
                source_actions,
                sizing_mode="stretch_width",
            ),
            title="Source",
            collapsed=False,
            sizing_mode="stretch_width",
        )
        discovery_section = pn.Card(
            pn.Column(
                self.candidate_select,
                self.candidate_summary,
                sizing_mode="stretch_width",
            ),
            title="Discovery",
            collapsed=False,
            sizing_mode="stretch_width",
        )
        import_section = pn.Card(
            pn.Column(
                pn.Row(
                    self.dataset_id_input,
                    self.group_id_input,
                    self.color_input,
                    sizing_mode="stretch_width",
                ),
                self.import_button,
                sizing_mode="stretch_width",
            ),
            title="Import Options",
            collapsed=False,
            sizing_mode="stretch_width",
        )
        status_section = pn.Card(
            pn.Column(
                self.workspace_summary,
                self.status,
                sizing_mode="stretch_width",
            ),
            title="Status",
            collapsed=False,
            sizing_mode="stretch_width",
        )
        intro = pn.pane.HTML(
            (
                '<div class="lw-import-datasets-intro">'
                "Import one experimental raw dataset into the active workspace. "
                "This MVP stays workspace-first and does not set active-dataset state or register references."
                "</div>"
            ),
            margin=0,
        )
        return pn.Column(
            intro,
            source_section,
            discovery_section,
            import_section,
            status_section,
            css_classes=["lw-import-datasets-root"],
            sizing_mode="stretch_width",
        )


def import_datasets_app() -> pn.viewable.Viewable:
    pn.extension(raw_css=[PORTAL_RAW_CSS, IMPORT_DATASETS_RAW_CSS])
    controller = _ImportDatasetsController()

    template = pn.template.MaterialTemplate(
        title="",
        header_background="#b0b4c2",
        header_color="#111111",
    )
    template.header.append(build_app_header(title="Import Experimental Datasets"))
    template.main.append(controller.view())
    return template
