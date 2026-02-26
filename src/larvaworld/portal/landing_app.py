from __future__ import annotations

import panel as pn

from larvaworld.portal.landing_registry import ITEMS, LANES, PINNED_QUICK_START
from larvaworld.portal.panel_components import (
    PORTAL_RAW_CSS,
    build_template_header,
    render_card,
    render_lane,
)
from larvaworld.portal.registry_logic import validate_registry


def landing_app() -> pn.viewable.Viewable:
    # English comments inside code.
    pn.extension(raw_css=[PORTAL_RAW_CSS])
    validate_registry(strict=True)

    template = pn.template.MaterialTemplate(
        title="Larvaworld Portal",
        header_background="#f5a142",
        header_color="#111111",
    )
    root = pn.Column(css_classes=["lw-portal-root"], sizing_mode="stretch_width")

    def _set_dark_mode(enabled: bool) -> None:
        classes = [cls for cls in root.css_classes if cls != "lw-portal-dark"]
        if enabled:
            classes.append("lw-portal-dark")
        root.css_classes = classes

    topbar = build_template_header(
        on_dark_mode_change=_set_dark_mode,
    )
    template.header.append(topbar)

    # Quick Start (pinned)
    pinned_items = [ITEMS[item_id] for item_id in PINNED_QUICK_START]
    quick_start = pn.Column(
        pn.pane.HTML('<div class="lw-portal-section-title">Quick Start</div>', margin=0),
        pn.GridBox(
            *[
                # No special logic: pinned renders the same items by ID.
                # (Guided-only rendering; deterministic order).
                render_card(item, show_lane_accent=False)
                for item in pinned_items
            ],
            ncols=4,
            css_classes=["lw-portal-grid"],
            sizing_mode="stretch_width",
        ),
        css_classes=["lw-portal-quick-start"],
        sizing_mode="stretch_width",
        margin=0,
    )
    root.append(quick_start)

    # Lanes
    for lane in LANES:
        lane_items = [ITEMS[item_id] for item_id in lane.item_ids if ITEMS[item_id].status != "hidden"]
        root.append(render_lane(lane, items=lane_items))

    template.main.append(root)
    return template
