from __future__ import annotations

import base64
import importlib.metadata as im
from html import escape
from pathlib import Path
from typing import Callable

import panel as pn

from larvaworld.portal.landing_registry import DOCS_ROOT, GITHUB_ROOT
from larvaworld.portal.registry_logic import compute_badges, compute_primary_action, resolve_target
from larvaworld.portal.registry_types import LandingItem, LaneSpec


PORTAL_RAW_CSS = """
/* Scoped Portal styles (must not affect legacy dashboards). */
.lw-portal-root {
  max-width: 1240px;
  margin: 0 auto;
  padding: 16px 16px 48px 16px;
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

.lw-portal-pill {
  display: inline-flex;
  align-items: center;
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 12px;
  border: 1px solid rgba(0,0,0,0.15);
  background: rgba(0,0,0,0.04);
}

.lw-portal-pill--showcase {
  border-color: rgba(239,108,0,0.55);
  background: rgba(239,108,0,0.10);
}

.lw-portal-topbar .lw-portal-pill--showcase {
  border-color: rgba(255,255,255,0.45);
  background: rgba(255,255,255,0.2);
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
.lw-portal-root.lw-portal-dark .lw-portal-card-hint,
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
  border: 1px solid rgba(0,0,0,0.12);
  border-radius: 14px;
  padding: 14px 14px 12px 14px;
  background: rgba(255,255,255,0.96);
  box-shadow: 0 1px 8px rgba(0,0,0,0.05);
  min-height: 140px;
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
  margin: 0 0 10px 0;
  color: rgba(0,0,0,0.72);
}

.lw-portal-card-hint {
  font-size: 12px;
  margin: 0 0 12px 0;
  color: rgba(0,0,0,0.62);
}

.lw-portal-actions {
  position: relative;
  z-index: 4;
  display: flex;
  align-items: center;
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

.lw-portal-btn--disabled {
  border-color: rgba(0,0,0,0.14);
  background: rgba(0,0,0,0.04);
  color: rgba(0,0,0,0.38);
  pointer-events: none;
}

.lw-portal-secondary {
  font-size: 12px;
  text-decoration: none;
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


def _portal_logo_html(*, version: str, showcase_mode: bool) -> str:
    # English comments inside code.
    logo_img = ""
    if _LOGO_DATA_URI:
        logo_img = (
            f'<img class="lw-portal-logo-img" src="{_LOGO_DATA_URI}" alt="Larvaworld logo"/>'
        )

    showcase_pill = ""
    if showcase_mode:
        showcase_pill = '<span class="lw-portal-pill lw-portal-pill--showcase">Showcase mode</span>'

    return (
        '<a class="lw-portal-logo" href="/landing" '
        "onclick=\"if (window.location.pathname !== '/landing' && "
        "window.location.pathname !== '/') { return confirm('Leave this page?\\n\\nReturning "
        "to the landing page will reset the current view. Any unsaved selections or progress "
        "may be lost.'); } return true;\">"
        f"{logo_img}"
        '<span class="lw-portal-logo-text">Larvaworld</span>'
        f'<span class="lw-portal-version-badge">v{escape(version)}</span>'
        f"{showcase_pill}"
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


def _button_html(*, label: str, href: str | None, enabled: bool) -> str:
    # English comments inside code.
    if not enabled or not href:
        return f'<span class="lw-portal-btn lw-portal-btn--disabled">{escape(label)}</span>'

    attrs = ""
    if href.startswith("http://") or href.startswith("https://"):
        attrs = ' target="_blank" rel="noopener noreferrer"'

    return f'<a class="lw-portal-btn" href="{escape(href)}"{attrs}>{escape(label)}</a>'


def _secondary_docs_link(item: LandingItem) -> str:
    # English comments inside code.
    if not item.learn_more or not item.learn_more.docs_url:
        return ""
    url = item.learn_more.docs_url
    return (
        f'<a class="lw-portal-secondary" href="{escape(url)}" '
        'target="_blank" rel="noopener noreferrer">Docs</a>'
    )


def build_template_header(
    *,
    showcase_mode: bool,
    on_dark_mode_change: Callable[[bool], None] | None = None,
) -> pn.viewable.Viewable:
    # English comments inside code.
    left = pn.pane.HTML(
        _portal_logo_html(version=_PORTAL_VERSION, showcase_mode=showcase_mode),
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
    showcase_status = "ON" if showcase_mode else "OFF"
    showcase_info = pn.pane.HTML(
        f'<div class="lw-portal-settings-row">Showcase mode: <b>{showcase_status}</b></div>',
        margin=0,
    )
    settings_body = pn.Column(
        advanced_toggle,
        dark_mode_toggle,
        showcase_info,
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


def render_card(item: LandingItem, *, showcase_mode: bool) -> pn.viewable.Viewable:
    # English comments inside code.
    action = compute_primary_action(item, showcase_mode=showcase_mode)
    badges = compute_badges(item)
    card_href = resolve_target(item) or f"/{item.id}"

    card_classes = ["lw-portal-card"]
    if item.status == "planned" or item.kind == "placeholder":
        card_classes.append("lw-portal-card--planned")

    badges_html = "".join(_badge_html(b) for b in badges)
    hint = item.prereq_hint or "Planned."
    show_hint = item.status == "planned" or item.kind == "placeholder"

    # Secondary docs link appears when Learn more points to an issue and docs_url exists.
    secondary = ""
    if action.label.lower() == "learn more" and item.learn_more and item.learn_more.issue_url:
        secondary = _secondary_docs_link(item)

    primary_action_html = ""
    if not (item.kind == "panel_app" and item.status == "ready"):
        primary_action_html = _button_html(label=action.label, href=action.href, enabled=action.enabled)

    actions_html = (
        '<div class="lw-portal-actions">' + primary_action_html + secondary + "</div>"
    )
    show_actions = bool(primary_action_html or secondary)

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
            f'<div class="lw-portal-card-subtitle">{escape(item.subtitle)}</div>', margin=0
        ),
        pn.pane.HTML(
            f'<div class="lw-portal-card-hint">{escape(hint)}</div>',
            margin=0,
            visible=show_hint,
        ),
        actions_pane,
        overlay_pane,
        css_classes=card_classes,
        styles={"position": "relative"},
        margin=0,
        sizing_mode="stretch_width",
    )
    return body


def render_lane(lane: LaneSpec, *, showcase_mode: bool, items: list[LandingItem]) -> pn.viewable.Viewable:
    # English comments inside code.
    title = pn.pane.HTML(
        f'<div class="lw-portal-section-title">{escape(lane.title)}</div>', margin=0
    )
    cards = [render_card(item, showcase_mode=showcase_mode) for item in items]
    grid = pn.pane.HTML("", visible=False)  # placeholder to keep types simple
    if cards:
        grid = pn.GridBox(*cards, ncols=4, css_classes=["lw-portal-grid"], sizing_mode="stretch_width")

    content = pn.Column(title, grid, sizing_mode="stretch_width", margin=0)
    if not lane.collapsed_by_default:
        return content

    # Collapsed lane (demo/tutorials) uses an accordion to avoid distracting the main workflows.
    return pn.Accordion((lane.title, content), active=[], sizing_mode="stretch_width")
