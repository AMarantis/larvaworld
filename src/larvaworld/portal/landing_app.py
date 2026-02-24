from __future__ import annotations

import panel as pn

from larvaworld.portal.landing_registry import ITEMS, LANES, PINNED_QUICK_START
from larvaworld.portal.panel_components import (
    PORTAL_RAW_CSS,
    render_card,
    render_header,
    render_lane,
)
from larvaworld.portal.registry_logic import read_showcase_mode, validate_registry


def landing_app() -> pn.viewable.Viewable:
    # English comments inside code.
    pn.extension(raw_css=[PORTAL_RAW_CSS])
    validate_registry(strict=True)

    showcase_mode = read_showcase_mode()

    template = pn.template.MaterialTemplate(title="Larvaworld Portal")
    root = pn.Column(css_classes=["lw-portal-root"], sizing_mode="stretch_width")

    root.append(render_header(showcase_mode=showcase_mode))

    # Quick Start (pinned)
    pinned_items = [ITEMS[item_id] for item_id in PINNED_QUICK_START]
    root.append(pn.pane.HTML('<div class="lw-portal-section-title">Quick Start</div>', margin=0))
    root.append(
        pn.GridBox(
            *[
                # No special logic: pinned renders the same items by ID.
                # (Guided-only rendering; deterministic order).
                render_card(item, showcase_mode=showcase_mode)
                for item in pinned_items
            ],
            ncols=4,
            css_classes=["lw-portal-grid"],
            sizing_mode="stretch_width",
        )
    )

    # Lanes
    for lane in LANES:
        lane_items = [ITEMS[item_id] for item_id in lane.item_ids if ITEMS[item_id].status != "hidden"]
        root.append(render_lane(lane, showcase_mode=showcase_mode, items=lane_items))

    template.main.append(root)
    return template
