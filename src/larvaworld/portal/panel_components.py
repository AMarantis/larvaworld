from __future__ import annotations

import base64
import importlib.metadata as im
from html import escape
from pathlib import Path
from typing import Callable

import panel as pn

from larvaworld.portal.landing_registry import DOCS_ROOT, GITHUB_ISSUES, GITHUB_ROOT
from larvaworld.portal.registry_logic import compute_badges, compute_primary_action, resolve_target
from larvaworld.portal.registry_types import LandingItem, LaneSpec


PORTAL_RAW_CSS = """
/* Scoped Portal styles (must not affect legacy dashboards). */
.lw-portal-root {
  max-width: 1240px;
  margin: 0 auto;
  padding: 16px 16px 56px 16px;
}

.lw-portal-root.lw-portal-dark {
  background: rgb(15, 23, 42);
  color: rgb(226, 232, 240);
  border-radius: 12px;
}

/* The template title bar is replaced by a custom top bar in #header-items. */
.app-header {
  display: none !important;
}

#header-items {
  margin-left: 0;
}

.lw-portal-topbar {
  display: flex;
  align-items: center !important;
  justify-content: space-between;
  gap: 16px;
  width: 100%;
  min-height: 60px;
}

.lw-portal-topbar > * {
  align-self: center !important;
}

.lw-portal-header-left {
  min-width: 0;
}

.lw-portal-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: inherit;
  min-width: 0;
}

.lw-portal-logo:hover {
  text-decoration: none;
}

.lw-portal-topbar .lw-portal-logo {
  color: rgba(255,255,255,0.96);
}

.lw-portal-logo-img {
  width: 58px;
  height: 58px;
  object-fit: contain;
  flex: 0 0 auto;
  background: #ffffff;
  border-radius: 10px;
  padding: 4px;
  box-sizing: border-box;
}

.lw-portal-logo-text {
  font-size: 22px;
  font-weight: 650;
  letter-spacing: 0.2px;
  margin: 0;
  line-height: 1;
}

.lw-portal-version-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
  border: 1px solid rgba(0,0,0,0.18);
  background: rgba(0,0,0,0.04);
  color: rgba(0,0,0,0.78);
}

.lw-portal-topbar .lw-portal-version-badge {
  border-color: rgba(255,255,255,0.35);
  background: rgba(255,255,255,0.16);
  color: rgba(255,255,255,0.96);
}

.lw-portal-header-right-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: auto;
  flex: 0 0 auto;
  align-self: center !important;
}

.lw-portal-header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.lw-portal-icon-link,
.lw-portal-topbar .lw-portal-settings-btn .bk-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 34px;
  border-radius: 10px;
  border: 1px solid rgba(0,0,0,0.18);
  background: #ffffff;
  color: #111111;
  text-decoration: none;
}

.lw-portal-icon-link {
  width: 38px;
  padding: 0;
}

.lw-portal-icon-link:hover,
.lw-portal-topbar .lw-portal-settings-btn .bk-btn:hover {
  background: #f3f4f6;
  color: #111111;
  text-decoration: none;
}

.lw-portal-header-icon {
  width: 24px;
  height: 24px;
  object-fit: contain;
}

.lw-portal-settings-btn .bk-btn {
  text-decoration: none;
  padding: 0 12px;
  font-size: 13px;
  font-weight: 500;
}

.lw-portal-settings-btn {
  margin: 0 !important;
}

.lw-portal-settings-dropdown-wrap {
  position: relative;
  display: flex;
  display: inline-flex;
  align-items: center;
  width: auto !important;
  flex: 0 0 auto;
  align-self: center !important;
}

.lw-portal-settings-panel {
  position: absolute;
  top: 40px;
  right: 0;
  min-width: 260px;
  padding: 0;
  border: 0;
  background: #ffffff;
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.16);
  z-index: 30;
  color: #111111 !important;
  opacity: 1;
  pointer-events: auto;
}

.lw-portal-settings-title {
  font-size: 13px;
  font-weight: 650;
  margin: 0 0 6px 0;
  color: #111111;
}

.lw-portal-settings-body {
  min-width: 260px;
  border: 1px solid rgba(0,0,0,0.22);
  border-radius: 12px;
  padding: 10px 12px;
  background: #ffffff !important;
  box-shadow: none;
  color: #111111 !important;
  opacity: 1;
  backdrop-filter: none;
}

.lw-portal-settings-row {
  font-size: 12px;
  color: rgba(0,0,0,0.72);
}

.lw-portal-settings-advanced {
  display: flex;
  align-items: center;
  gap: 6px;
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
  border-radius: 0 !important;
  padding: 0 !important;
}

.lw-portal-settings-check {
  color: rgba(17,17,17,0.72);
  font-size: 12px;
  line-height: 1;
}

.lw-portal-settings-panel .bk,
.lw-portal-settings-panel label,
.lw-portal-settings-panel .bk-input-group,
.lw-portal-settings-panel .bk-form-group {
  color: #111111 !important;
}

.lw-portal-settings-body .bk,
.lw-portal-settings-body label,
.lw-portal-settings-body .bk-input-group,
.lw-portal-settings-body .bk-form-group {
  color: #111111 !important;
}

.lw-portal-settings-panel * {
  color: #111111 !important;
}

.lw-portal-settings-body * {
  color: #111111 !important;
}

.lw-portal-settings-panel .bk-input-group,
.lw-portal-settings-panel .bk-form-group,
.lw-portal-settings-panel .bk-input-group input {
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
  padding: 0 !important;
}

.lw-portal-root.lw-portal-dark .lw-portal-section-title,
.lw-portal-root.lw-portal-dark .lw-portal-card-title {
  color: rgb(241, 245, 249);
}

.lw-portal-root.lw-portal-dark .lw-portal-card {
  border-color: rgba(148, 163, 184, 0.45);
  background: rgba(30, 41, 59, 0.88);
  box-shadow: none;
}

.lw-portal-root.lw-portal-dark .lw-portal-card-subtitle,
.lw-portal-root.lw-portal-dark .lw-portal-settings-row {
  color: rgba(203, 213, 225, 0.9);
}

.lw-portal-root.lw-portal-dark .lw-portal-badge,
.lw-portal-root.lw-portal-dark .lw-portal-version-badge {
  border-color: rgba(148, 163, 184, 0.42);
  background: rgba(15, 23, 42, 0.72);
  color: rgb(226, 232, 240);
}

.lw-portal-section-title {
  margin: 18px 0 10px 0;
  font-size: 18px;
  font-weight: 650;
}

.lw-portal-quick-start {
  margin: 8px 0 18px 0;
  padding: 8px 12px 14px 10px;
  border-radius: 14px;
  background: rgba(0,0,0,0.08);
  border-left: 4px solid #f5a142;
}

.lw-portal-root.lw-portal-dark .lw-portal-quick-start {
  background: rgba(2, 6, 23, 0.5);
}

.lw-portal-grid {
  /* Let Panel control layout; we only suggest spacing. */
  gap: 14px;
}

.lw-portal-card {
  position: relative;
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(0,0,0,0.12);
  border-radius: 14px;
  padding: 14px 14px 4px 14px;
  background: rgba(255,255,255,0.96);
  box-shadow: 0 1px 8px rgba(0,0,0,0.05);
  height: 186px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 140ms ease, box-shadow 140ms ease;
}

.lw-portal-card:hover {
  transform: scale(1.015);
  box-shadow: 0 10px 18px rgba(0,0,0,0.10);
}

.lw-portal-card-link-overlay {
  display: block;
  width: 100%;
  height: 100%;
  border-radius: 14px;
  text-decoration: none;
  cursor: pointer;
}

.lw-portal-card--planned {
  opacity: 0.86;
}

.lw-portal-card--lane-simulate {
  border-top: 3px solid #b5c2b0;
}

.lw-portal-card--lane-data {
  border-top: 3px solid #b0b4c2;
}

.lw-portal-card--lane-models {
  border-top: 3px solid #c1b0c2;
}

.lw-portal-card--lane-eval {
  border-top: 3px solid #b1b2de;
}

.lw-portal-card--lane-simulate:hover {
  box-shadow: 0 10px 18px rgba(0,0,0,0.08), 0 0 0 9999px rgba(181,194,176,0.14) inset;
}

.lw-portal-card--lane-data:hover {
  box-shadow: 0 10px 18px rgba(0,0,0,0.08), 0 0 0 9999px rgba(176,180,194,0.14) inset;
}

.lw-portal-card--lane-models:hover {
  box-shadow: 0 10px 18px rgba(0,0,0,0.08), 0 0 0 9999px rgba(193,176,194,0.14) inset;
}

.lw-portal-card--lane-eval:hover {
  box-shadow: 0 10px 18px rgba(0,0,0,0.08), 0 0 0 9999px rgba(177,178,222,0.14) inset;
}

.lw-portal-card-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 10px;
}

.lw-portal-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
  border: 1px solid rgba(0,0,0,0.18);
  background: rgba(0,0,0,0.04);
}

.lw-portal-badge--planned {
  border-color: rgba(239,108,0,0.55);
  background: rgba(239,108,0,0.10);
}

.lw-portal-card-title {
  font-size: 16px;
  font-weight: 650;
  margin: 0 0 6px 0;
}

.lw-portal-card-subtitle {
  font-size: 13px;
  line-height: 1.35;
  margin: 0 0 8px 0;
  min-height: calc(1.35em * 3);
  max-height: calc(1.35em * 3);
  overflow: hidden;
  color: rgba(0,0,0,0.72);
}

.lw-portal-actions {
  position: relative;
  z-index: 4;
  display: flex;
  align-items: center;
  margin-top: auto;
  gap: 10px;
}

.lw-portal-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 12px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  text-decoration: none;
  border: 1px solid rgba(25,118,210,0.35);
  background: rgba(25,118,210,0.10);
  color: rgb(25,118,210);
}

.lw-portal-btn:hover {
  background: rgba(25,118,210,0.14);
}

.lw-portal-btn--learn-more {
  padding: 4px 8px;
  font-size: 11px;
}

.lw-portal-btn--notebook-simulate {
  border-color: rgba(181,194,176,0.92);
  background: rgba(181,194,176,0.24);
  color: rgb(46, 60, 42);
}

.lw-portal-btn--notebook-data {
  border-color: rgba(176,180,194,0.92);
  background: rgba(176,180,194,0.24);
  color: rgb(44, 48, 61);
}

.lw-portal-btn--notebook-models {
  border-color: rgba(193,176,194,0.92);
  background: rgba(193,176,194,0.24);
  color: rgb(64, 47, 66);
}

.lw-portal-btn--notebook-eval {
  border-color: rgba(177,178,222,0.92);
  background: rgba(177,178,222,0.24);
  color: rgb(43, 44, 84);
}

.lw-portal-btn--notebook-simulate:hover {
  background: rgba(181,194,176,0.34);
}

.lw-portal-btn--notebook-data:hover {
  background: rgba(176,180,194,0.34);
}

.lw-portal-btn--notebook-models:hover {
  background: rgba(193,176,194,0.34);
}

.lw-portal-btn--notebook-eval:hover {
  background: rgba(177,178,222,0.34);
}

.lw-portal-btn--disabled {
  border-color: rgba(0,0,0,0.14);
  background: rgba(0,0,0,0.04);
  color: rgba(0,0,0,0.38);
  pointer-events: none;
}

.lw-portal-footer-shell {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 40;
}

.lw-portal-footer-bar {
  width: 100%;
  min-height: 24px;
  padding: 4px 10px;
  background: #f5a142;
  color: #111111;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 11px;
  box-sizing: border-box;
}

.lw-portal-footer-link {
  color: #111111;
  text-decoration: underline;
}

.lw-portal-footer-link:hover {
  color: #111111;
}
""".strip()


def _load_icon_data_uri(filename: str, mime_type: str) -> str:
    # English comments inside code.
    icon_path = Path(__file__).with_name("icons") / filename
    try:
        encoded = base64.b64encode(icon_path.read_bytes()).decode("ascii")
    except OSError:
        return ""
    return f"data:{mime_type};base64,{encoded}"


def _resolve_portal_version() -> str:
    # English comments inside code.
    try:
        return im.version("larvaworld")
    except Exception:
        return "dev"


_LOGO_DATA_URI = _load_icon_data_uri("LarvaWorld_logo.png", "image/png")
_RTD_ICON_DATA_URI = _load_icon_data_uri("RTD_logo.svg", "image/svg+xml")
_GITHUB_ICON_DATA_URI = _load_icon_data_uri("github_logo.svg", "image/svg+xml")
_PORTAL_VERSION = _resolve_portal_version()


def _portal_logo_html(*, version: str) -> str:
    # English comments inside code.
    logo_img = ""
    if _LOGO_DATA_URI:
        logo_img = (
            f'<img class="lw-portal-logo-img" src="{_LOGO_DATA_URI}" alt="Larvaworld logo"/>'
        )

    return (
        '<a class="lw-portal-logo" href="/landing" '
        "onclick=\"if (window.location.pathname !== '/landing' && "
        "window.location.pathname !== '/') { return confirm('Leave this page?\\n\\nReturning "
        "to the landing page will reset the current view. Any unsaved selections or progress "
        "may be lost.'); } return true;\">"
        f"{logo_img}"
        '<span class="lw-portal-logo-text">Larvaworld</span>'
        f'<span class="lw-portal-version-badge">v{escape(version)}</span>'
        "</a>"
    )


def _header_links_html() -> str:
    # English comments inside code.
    docs_icon = ""
    if _RTD_ICON_DATA_URI:
        docs_icon = (
            f'<img class="lw-portal-header-icon" src="{_RTD_ICON_DATA_URI}" '
            'alt="Read the Docs logo"/>'
        )

    github_icon = ""
    if _GITHUB_ICON_DATA_URI:
        github_icon = (
            f'<img class="lw-portal-header-icon" src="{_GITHUB_ICON_DATA_URI}" '
            'alt="GitHub logo"/>'
        )

    return (
        '<div class="lw-portal-header-right">'
        f'<a class="lw-portal-icon-link" href="{escape(DOCS_ROOT)}" '
        'target="_blank" rel="noopener noreferrer" title="Read the Docs">'
        f"{docs_icon}"
        "</a>"
        f'<a class="lw-portal-icon-link" href="{escape(GITHUB_ROOT)}" '
        'target="_blank" rel="noopener noreferrer" title="GitHub">'
        f"{github_icon}"
        "</a>"
        "</div>"
    )


def _badge_html(badge: str) -> str:
    # English comments inside code.
    cls = "lw-portal-badge"
    if badge.lower() == "planned":
        cls += " lw-portal-badge--planned"
    return f'<span class="{cls}">{escape(badge)}</span>'


def _button_html(
    *,
    label: str,
    href: str | None,
    enabled: bool,
    extra_classes: tuple[str, ...] = (),
) -> str:
    # English comments inside code.
    normalized_label = label.strip().lower()
    button_classes = ["lw-portal-btn"]
    if normalized_label in {"learn more", "notebook"}:
        button_classes.append("lw-portal-btn--learn-more")
    if normalized_label == "notebook":
        button_classes.append("lw-portal-btn--notebook")
    button_classes.extend(extra_classes)
    class_attr = " ".join(button_classes)

    if not enabled or not href:
        return f'<span class="{class_attr} lw-portal-btn--disabled">{escape(label)}</span>'

    attrs = ""
    if normalized_label == "notebook":
        attrs = ' target="_blank" rel="noopener noreferrer"'
    elif href.startswith("http://") or href.startswith("https://"):
        attrs = ' target="_blank" rel="noopener noreferrer"'

    return f'<a class="{class_attr}" href="{escape(href)}"{attrs}>{escape(label)}</a>'


def _subtitle_html(text: str) -> str:
    # English comments inside code.
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        lines = [""]
    return "<br/>".join(escape(line) for line in lines[:3])


def build_footer() -> pn.viewable.Viewable:
    # English comments inside code.
    html = (
        '<div class="lw-portal-footer-shell"><div class="lw-portal-footer-bar">'
        '<span>&copy; Larvaworld</span>'
        f'<span>v{escape(_PORTAL_VERSION)}</span>'
        '<span>University of Cologne</span>'
        f'<a class="lw-portal-footer-link" href="{escape(DOCS_ROOT)}" '
        'target="_blank" rel="noopener noreferrer">Docs</a>'
        f'<a class="lw-portal-footer-link" href="{escape(GITHUB_ROOT)}" '
        'target="_blank" rel="noopener noreferrer">GitHub</a>'
        f'<a class="lw-portal-footer-link" href="{escape(GITHUB_ISSUES)}" '
        'target="_blank" rel="noopener noreferrer">Issues</a>'
        '<a class="lw-portal-footer-link" href="mailto:p.sakagiannis@uni-koeln.de">'
        'Contact</a>'
        "</div></div>"
    )
    return pn.pane.HTML(html, margin=0, sizing_mode="stretch_width")


def build_template_header(
    *,
    on_dark_mode_change: Callable[[bool], None] | None = None,
) -> pn.viewable.Viewable:
    # English comments inside code.
    left = pn.pane.HTML(
        _portal_logo_html(version=_PORTAL_VERSION),
        margin=0,
        css_classes=["lw-portal-header-left"],
    )
    links = pn.pane.HTML(
        _header_links_html(),
        margin=0,
    )
    settings_button = pn.widgets.Button(
        name="Settings",
        button_type="default",
        width=88,
        margin=0,
        css_classes=["lw-portal-settings-btn"],
    )
    advanced_toggle = pn.pane.HTML(
        (
            '<div class="lw-portal-settings-row lw-portal-settings-advanced">'
            '<span class="lw-portal-settings-check">☑</span>'
            "<span>Show Advanced items</span>"
            "</div>"
        ),
        margin=0,
    )
    dark_mode_toggle = pn.widgets.Switch(name="Dark mode", value=False, margin=0)
    settings_body = pn.Column(
        advanced_toggle,
        dark_mode_toggle,
        css_classes=["lw-portal-settings-body"],
        sizing_mode="stretch_width",
        margin=0,
    )
    settings_panel = pn.Column(
        settings_body,
        visible=False,
        css_classes=["lw-portal-settings-panel"],
        margin=0,
    )

    def _toggle_settings(_: object) -> None:
        settings_panel.visible = not settings_panel.visible

    if on_dark_mode_change is not None:
        def _toggle_dark_mode(event: object) -> None:
            value = bool(getattr(event, "new", False))
            on_dark_mode_change(value)

        dark_mode_toggle.param.watch(_toggle_dark_mode, "value")
    settings_button.on_click(_toggle_settings)

    settings_dropdown = pn.Column(
        settings_button,
        settings_panel,
        css_classes=["lw-portal-settings-dropdown-wrap"],
        margin=0,
        sizing_mode="fixed",
        width_policy="min",
    )
    right = pn.Row(
        links,
        settings_dropdown,
        css_classes=["lw-portal-header-right-wrap"],
        margin=0,
        sizing_mode="fixed",
        width_policy="min",
    )
    header_row = pn.Row(
        left,
        pn.Spacer(),
        pn.Spacer(sizing_mode="stretch_width"),
        right,
        css_classes=["lw-portal-topbar"],
        sizing_mode="stretch_width",
        margin=0,
    )
    return header_row


def render_card(
    item: LandingItem,
    *,
    show_lane_accent: bool = True,
    notebook_urls: dict[str, str] | None = None,
) -> pn.viewable.Viewable:
    # English comments inside code.
    action = compute_primary_action(item)
    badges = compute_badges(item)
    card_href = resolve_target(item) or f"/{item.id}"

    card_classes = ["lw-portal-card"]
    lane_classes = {
        "simulate": "lw-portal-card--lane-simulate",
        "data": "lw-portal-card--lane-data",
        "models": "lw-portal-card--lane-models",
        "eval": "lw-portal-card--lane-eval",
    }
    lane_class = lane_classes.get(item.lane)
    if lane_class and show_lane_accent:
        card_classes.append(lane_class)
    if item.status == "planned" or item.kind == "placeholder":
        card_classes.append("lw-portal-card--planned")

    badges_html = "".join(_badge_html(b) for b in badges)

    primary_action_html = _button_html(
        label="Learn more",
        href=action.href,
        enabled=action.enabled,
    )
    notebook_href = notebook_urls.get(item.id) if notebook_urls else None
    notebook_action_html = ""
    if notebook_href:
        notebook_lane_classes = {
            "simulate": "lw-portal-btn--notebook-simulate",
            "data": "lw-portal-btn--notebook-data",
            "models": "lw-portal-btn--notebook-models",
            "eval": "lw-portal-btn--notebook-eval",
        }
        notebook_lane_class = notebook_lane_classes.get(item.lane)
        extra_classes: tuple[str, ...] = ()
        if notebook_lane_class:
            extra_classes = (notebook_lane_class,)
        notebook_action_html = _button_html(
            label="Notebook",
            href=notebook_href,
            enabled=True,
            extra_classes=extra_classes,
        )

    actions_html = (
        '<div class="lw-portal-actions">'
        + primary_action_html
        + notebook_action_html
        + "</div>"
    )
    show_actions = bool(primary_action_html or notebook_action_html)

    overlay_attrs = ""
    if card_href.startswith("http://") or card_href.startswith("https://"):
        overlay_attrs = ' target="_blank" rel="noopener noreferrer"'
    overlay_style = (
        "position:absolute;inset:0;display:block;width:100%;height:100%;"
        "border-radius:14px;text-decoration:none;cursor:pointer;"
    )
    overlay_html = (
        f'<a class="lw-portal-card-link-overlay" style="{overlay_style}" '
        f'href="{escape(card_href)}"{overlay_attrs} '
        f'aria-label="Open {escape(item.title)}"></a>'
    )
    actions_pane = pn.pane.HTML(
        actions_html,
        margin=0,
        visible=show_actions,
        styles={"position": "relative", "z-index": "4"},
    )
    overlay_pane = pn.pane.HTML(
        overlay_html,
        margin=0,
        visible=bool(card_href),
        styles={
            "position": "absolute",
            "inset": "0",
            "width": "100%",
            "height": "100%",
            "z-index": "3",
            "pointer-events": "auto",
        },
    )

    body = pn.Column(
        pn.pane.HTML(f'<div class="lw-portal-card-badges">{badges_html}</div>', margin=0),
        pn.pane.HTML(f'<div class="lw-portal-card-title">{escape(item.title)}</div>', margin=0),
        pn.pane.HTML(
            f'<div class="lw-portal-card-subtitle">{_subtitle_html(item.subtitle)}</div>', margin=0
        ),
        actions_pane,
        overlay_pane,
        css_classes=card_classes,
        styles={"position": "relative"},
        margin=0,
        sizing_mode="stretch_width",
    )
    return body


def render_lane(
    lane: LaneSpec,
    *,
    items: list[LandingItem],
    notebook_urls: dict[str, str] | None = None,
) -> pn.viewable.Viewable:
    # English comments inside code.
    title = pn.pane.HTML(
        f'<div class="lw-portal-section-title">{escape(lane.title)}</div>', margin=0
    )
    cards = [render_card(item, notebook_urls=notebook_urls) for item in items]
    grid = pn.pane.HTML("", visible=False)  # placeholder to keep types simple
    if cards:
        grid = pn.GridBox(*cards, ncols=4, css_classes=["lw-portal-grid"], sizing_mode="stretch_width")

    content = pn.Column(title, grid, sizing_mode="stretch_width", margin=0)
    if not lane.collapsed_by_default:
        return content

    # Collapsed lane (demo/tutorials) uses an accordion to avoid distracting the main workflows.
    return pn.Accordion((lane.title, content), active=[], sizing_mode="stretch_width")
