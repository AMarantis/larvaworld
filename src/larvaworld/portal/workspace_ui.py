from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
import os
import shutil
import subprocess
from typing import Callable

import panel as pn

from larvaworld.portal.workspace import (
    WorkspaceState,
    clear_active_workspace_path,
    get_active_workspace,
    get_active_workspace_path,
    initialize_workspace,
    set_active_workspace_path,
    validate_workspace,
)


def _short_path(path: Path, *, keep_parts: int = 3) -> str:
    parts = path.parts
    if len(parts) <= keep_parts:
        return str(path)
    return str(Path("...").joinpath(*parts[-keep_parts:]))


def _workspace_chip_html(workspace: WorkspaceState | None) -> str:
    if workspace is None:
        return (
            '<div class="lw-portal-workspace-chip lw-portal-workspace-chip--missing">'
            '<span class="lw-portal-workspace-chip-label">Workspace</span>'
            '<span class="lw-portal-workspace-chip-value">Not set</span>'
            "</div>"
        )

    return (
        '<div class="lw-portal-workspace-chip" '
        f'title="{escape(str(workspace.root))}">'
        '<span class="lw-portal-workspace-chip-label">Workspace</span>'
        f'<span class="lw-portal-workspace-chip-value">{escape(workspace.name)}</span>'
        f'<span class="lw-portal-workspace-chip-path">{escape(_short_path(workspace.root))}</span>'
        "</div>"
    )


def _workspace_led_html(workspace: WorkspaceState | None) -> str:
    active = workspace is not None
    title = "Workspace configured" if active else "Workspace not configured"
    cls = "lw-portal-workspace-led"
    if active:
        cls += " lw-portal-workspace-led--active"
    else:
        cls += " lw-portal-workspace-led--inactive"
    return f'<div class="{cls}" title="{escape(title)}" aria-label="{escape(title)}"></div>'


def _status_html(*, text: str, tone: str = "neutral", detail: str | None = None) -> str:
    detail_html = ""
    if detail:
        detail_html = (
            f'<div class="lw-portal-workspace-status-detail">{escape(detail)}</div>'
        )
    return (
        f'<div class="lw-portal-workspace-status lw-portal-workspace-status--{escape(tone)}">'
        f"{escape(text)}"
        f"{detail_html}"
        "</div>"
    )


def _default_workspace_candidate() -> Path:
    active = get_active_workspace_path()
    if active is not None:
        return active
    return Path.home() / "Documents" / "Larvaworld" / "workspace"


def _pick_directory_via_windows_dialog(initial_dir: Path | None = None) -> Path | None:
    if not os.getenv("WSL_DISTRO_NAME") or shutil.which("powershell.exe") is None:
        return None

    initial_linux = str((initial_dir or _default_workspace_candidate()).expanduser())
    initial_windows = ""
    converted = subprocess.run(
        ["wslpath", "-w", initial_linux],
        capture_output=True,
        text=True,
        check=False,
    )
    if converted.returncode == 0:
        initial_windows = converted.stdout.strip()
    initial_windows = initial_windows.replace("'", "''")

    script = rf"""
Add-Type -AssemblyName PresentationFramework
$defaultRoot = [Environment]::GetFolderPath('MyDocuments')
$initialDir = '{initial_windows}'
if ([string]::IsNullOrWhiteSpace($initialDir) -or -not (Test-Path $initialDir)) {{
    $initialDir = Join-Path $defaultRoot 'Larvaworld'
}}
if (-not (Test-Path $initialDir)) {{
    $initialDir = $defaultRoot
}}
$dialog = New-Object Microsoft.Win32.OpenFileDialog
$dialog.Title = 'Select Larvaworld workspace folder'
$dialog.CheckFileExists = $false
$dialog.CheckPathExists = $true
$dialog.ValidateNames = $false
$dialog.FileName = 'Select this folder'
$dialog.InitialDirectory = $initialDir
$dialog.Filter = 'Folders|*.folder'
if ($dialog.ShowDialog() -eq $true) {{
    $selectedPath = Split-Path -Parent $dialog.FileName
    if ($selectedPath) {{
        Write-Output $selectedPath
    }}
}}
"""
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", script],
        capture_output=True,
        text=True,
        check=False,
    )
    selected = result.stdout.strip()
    if not selected:
        return None
    converted = subprocess.run(
        ["wslpath", "-u", selected],
        capture_output=True,
        text=True,
        check=False,
    )
    linux_path = converted.stdout.strip()
    return Path(linux_path) if linux_path else None


def _pick_directory_via_tk(initial_dir: Path | None = None) -> Path | None:
    try:
        import tkinter as tk
        from tkinter import filedialog
    except Exception:
        return None

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        selected = filedialog.askdirectory(
            title="Select Larvaworld workspace folder",
            initialdir=str((initial_dir or _default_workspace_candidate()).expanduser()),
        )
    finally:
        root.destroy()
    return Path(selected).expanduser() if selected else None


def _pick_workspace_directory(initial_dir: Path | None = None) -> tuple[Path | None, str | None]:
    if os.getenv("WSL_DISTRO_NAME") and shutil.which("powershell.exe") is not None:
        try:
            return _pick_directory_via_windows_dialog(initial_dir), None
        except Exception as exc:
            return None, f"Windows folder picker failed: {exc}"

    try:
        selected = _pick_directory_via_tk(initial_dir)
        if selected is not None:
            return selected, None
    except Exception as exc:
        return None, f"Folder picker failed: {exc}"

    return None, "No folder picker is available in this environment."


@dataclass
class WorkspaceUiController:
    on_workspace_change: Callable[[WorkspaceState | None], None] | None = None

    def __post_init__(self) -> None:
        self.trigger_button = pn.widgets.Button(
            name="",
            button_type="default",
            margin=0,
            width=22,
            height=22,
            css_classes=["lw-portal-workspace-trigger-button"],
        )
        self.trigger_led = pn.pane.HTML(margin=0, width=22, height=22)
        current = get_active_workspace_path()
        self.path_input = pn.widgets.TextInput(
            name="Workspace folder",
            value=str(current) if current is not None else str(_default_workspace_candidate()),
            placeholder="/path/to/larvaworld-workspace",
            sizing_mode="stretch_width",
            css_classes=["lw-portal-workspace-input"],
        )
        self.set_button = pn.widgets.Button(
            name="Use Existing",
            button_type="primary",
            width=110,
            margin=0,
        )
        self.browse_button = pn.widgets.Button(
            name="Browse",
            button_type="default",
            width=80,
            margin=0,
        )
        self.init_button = pn.widgets.Button(
            name="Initialize",
            button_type="default",
            width=96,
            margin=0,
        )
        self.clear_button = pn.widgets.Button(
            name="Clear",
            button_type="default",
            width=72,
            margin=0,
        )
        self.current_pane = pn.pane.HTML(margin=0, sizing_mode="stretch_width")
        self.status_pane = pn.pane.HTML(
            margin=(8, 0, 0, 0),
            sizing_mode="stretch_width",
        )
        self.chip_pane = pn.pane.HTML(margin=0)
        self.trigger_view = pn.Column(
            self.trigger_led,
            self.trigger_button,
            margin=0,
            width=22,
            height=22,
            css_classes=["lw-portal-workspace-trigger-shell"],
        )

        self.set_button.on_click(self._on_use_existing)
        self.browse_button.on_click(self._on_browse)
        self.init_button.on_click(self._on_initialize)
        self.clear_button.on_click(self._on_clear)

        self._refresh()

    def _emit(self, workspace: WorkspaceState | None) -> None:
        if self.on_workspace_change is not None:
            self.on_workspace_change(workspace)

    def _refresh(
        self,
        message: str | None = None,
        tone: str = "neutral",
        *,
        preserve_input: bool = False,
    ) -> None:
        workspace = get_active_workspace()
        self.chip_pane.object = _workspace_chip_html(workspace)
        self.trigger_led.object = _workspace_led_html(workspace)

        if workspace is None:
            self.trigger_button.css_classes = ["lw-portal-workspace-trigger-button"]
            current = get_active_workspace_path()
            if not preserve_input and current is not None and not self.path_input.value.strip():
                self.path_input.value = str(current)
            self.current_pane.object = _status_html(
                text="No active workspace is configured.",
                tone="warning",
                detail="Select an initialized workspace or initialize a new one.",
            )
        else:
            self.trigger_button.css_classes = ["lw-portal-workspace-trigger-button"]
            if not preserve_input:
                self.path_input.value = str(workspace.root)
            self.current_pane.object = _status_html(
                text=f'Active workspace: "{workspace.name}"',
                tone="success",
                detail=str(workspace.root),
            )

        self.status_pane.object = ""
        if message is not None:
            self.status_pane.object = _status_html(text=message, tone=tone)

    def _candidate_path(self) -> Path | None:
        raw = self.path_input.value.strip()
        if not raw:
            self._refresh("Enter a workspace folder path first.", tone="warning")
            return None
        return Path(raw).expanduser()

    def _on_use_existing(self, _: object) -> None:
        candidate = self._candidate_path()
        if candidate is None:
            return

        validation = validate_workspace(candidate)
        if validation.errors:
            self._refresh("; ".join(validation.errors), tone="danger")
            return
        if not validation.initialized:
            self.status_pane.object = _status_html(
                text="Workspace exists but is not initialized.",
                tone="warning",
                detail="Missing folders: " + ", ".join(validation.missing_dirs),
            )
            return

        set_active_workspace_path(validation.path)
        workspace = get_active_workspace()
        self._refresh("Active workspace updated.", tone="success")
        self._emit(workspace)

    def _on_initialize(self, _: object) -> None:
        candidate = self._candidate_path()
        if candidate is None:
            return

        validation = validate_workspace(candidate)
        if validation.errors:
            self._refresh("; ".join(validation.errors), tone="danger")
            return

        workspace = initialize_workspace(candidate)
        set_active_workspace_path(workspace.root)
        self._refresh("Workspace initialized and activated.", tone="success")
        self._emit(workspace)

    def _on_browse(self, _: object) -> None:
        current = self.path_input.value.strip()
        initial_dir = Path(current).expanduser() if current else _default_workspace_candidate()
        selected, error = _pick_workspace_directory(initial_dir)
        if selected is not None:
            self.path_input.value = str(selected)
            self._refresh(
                "Selected workspace folder.",
                tone="neutral",
                preserve_input=True,
            )
            return
        if error is not None:
            self._refresh(error, tone="warning")

    def _on_clear(self, _: object) -> None:
        clear_active_workspace_path()
        self.path_input.value = str(_default_workspace_candidate())
        self._refresh("Active workspace cleared.", tone="warning", preserve_input=True)
        self._emit(None)

    def build_controls(self) -> pn.viewable.Viewable:
        return pn.Column(
            pn.pane.HTML(
                '<div class="lw-portal-settings-title">Workspace</div>',
                margin=0,
            ),
            self.current_pane,
            pn.Row(
                self.path_input,
                self.browse_button,
                sizing_mode="stretch_width",
                margin=(8, 0, 0, 0),
                css_classes=["lw-portal-workspace-path-row"],
            ),
            pn.Row(
                self.set_button,
                self.init_button,
                self.clear_button,
                sizing_mode="stretch_width",
                margin=(6, 0, 0, 0),
                css_classes=["lw-portal-workspace-actions"],
            ),
            self.status_pane,
            sizing_mode="stretch_width",
            margin=0,
            css_classes=["lw-portal-workspace-controls"],
        )
