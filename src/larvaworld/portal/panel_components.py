from __future__ import annotations

from html import escape

import panel as pn

from larvaworld.portal.registry_logic import compute_badges, compute_primary_action
from larvaworld.portal.registry_types import LandingItem, LaneSpec


PORTAL_RAW_CSS = """
/* Scoped Portal styles (must not affect legacy dashboards). */
.lw-portal-root {
  max-width: 1240px;
  margin: 0 auto;
  padding: 16px 16px 48px 16px;
}

.lw-portal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 8px 0 16px 0;
}

.lw-portal-brand {
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.lw-portal-brand-title {
  font-size: 22px;
  font-weight: 650;
  letter-spacing: 0.2px;
  margin: 0;
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

.lw-portal-nav {
  display: flex;
  align-items: center;
  gap: 10px;
}

.lw-portal-link {
  text-decoration: none;
  font-size: 13px;
}

.lw-portal-section-title {
  margin: 18px 0 10px 0;
  font-size: 18px;
  font-weight: 650;
}

.lw-portal-grid {
  /* Let Panel control layout; we only suggest spacing. */
  gap: 14px;
}

.lw-portal-card {
  border: 1px solid rgba(0,0,0,0.12);
  border-radius: 14px;
  padding: 14px 14px 12px 14px;
  background: rgba(255,255,255,0.96);
  box-shadow: 0 1px 8px rgba(0,0,0,0.05);
  min-height: 140px;
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


def render_header(*, showcase_mode: bool) -> pn.viewable.Viewable:
    # English comments inside code.
    pill = ""
    if showcase_mode:
        pill = '<span class="lw-portal-pill lw-portal-pill--showcase">Showcase mode</span>'

    left = pn.pane.HTML(
        (
            '<div class="lw-portal-brand">'
            '<div class="lw-portal-brand-title">Larvaworld</div>'
            f"{pill}"
            "</div>"
        ),
        margin=0,
    )
    nav = pn.pane.HTML(
        (
            '<div class="lw-portal-nav">'
            '<a class="lw-portal-link" href="/landing">Landing</a>'
            '<a class="lw-portal-link" href="/preview">Preview</a>'
            "</div>"
        ),
        margin=0,
    )
    return pn.Row(left, pn.Spacer(), nav, css_classes=["lw-portal-header"])


def render_card(item: LandingItem, *, showcase_mode: bool) -> pn.viewable.Viewable:
    # English comments inside code.
    action = compute_primary_action(item, showcase_mode=showcase_mode)
    badges = compute_badges(item)

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

    actions_html = (
        '<div class="lw-portal-actions">'
        + _button_html(label=action.label, href=action.href, enabled=action.enabled)
        + secondary
        + "</div>"
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
        pn.pane.HTML(actions_html, margin=0),
        css_classes=card_classes,
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
