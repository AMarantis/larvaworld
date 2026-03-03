from __future__ import annotations

import panel as pn

from larvaworld.portal.landing_registry import (
    ITEMS,
    LANES,
    QUICK_START_DEFAULT_MODE,
    QUICK_START_MODES,
)
from larvaworld.portal.panel_components import (
    PORTAL_RAW_CSS,
    build_footer,
    build_template_header,
    render_card,
    render_lane,
)
from larvaworld.portal.notebook_workspace import notebook_names_by_item, notebook_urls_by_item
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
    notebook_urls = notebook_urls_by_item()
    notebook_names = notebook_names_by_item()

    mode_by_id = {mode.mode_id: mode for mode in QUICK_START_MODES}
    active_mode_id = QUICK_START_DEFAULT_MODE if QUICK_START_DEFAULT_MODE in mode_by_id else QUICK_START_MODES[0].mode_id

    def _quick_start_grid(mode_id: str) -> pn.viewable.Viewable:
        mode = mode_by_id[mode_id]
        cards = [
            render_card(
                ITEMS[item_id],
                show_lane_accent=False,
                notebook_urls=notebook_urls,
                notebook_names=notebook_names,
            )
            for item_id in mode.item_ids
            if item_id in ITEMS and ITEMS[item_id].status != "hidden"
        ]
        return pn.GridBox(
            *cards,
            ncols=3,
            css_classes=["lw-portal-grid"],
            sizing_mode="stretch_width",
        )

    quick_start_cards = pn.Column(
        _quick_start_grid(active_mode_id),
        css_classes=["lw-portal-quick-start-cards"],
        sizing_mode="stretch_width",
        margin=0,
    )

    def _apply_mode_animation() -> None:
        classes = [cls for cls in quick_start_cards.css_classes if cls != "lw-portal-qs-flip"]
        classes.append("lw-portal-qs-flip")
        quick_start_cards.css_classes = classes

        document = pn.state.curdoc
        if document is None:
            quick_start_cards.css_classes = [cls for cls in classes if cls != "lw-portal-qs-flip"]
            return

        def _clear_animation() -> None:
            quick_start_cards.css_classes = [
                cls for cls in quick_start_cards.css_classes if cls != "lw-portal-qs-flip"
            ]

        document.add_timeout_callback(_clear_animation, 430)

    mode_buttons: dict[str, pn.widgets.Button] = {}
    quick_start_mode_classes = {
        "user": "lw-portal-quick-start--user",
        "modeler": "lw-portal-quick-start--modeler",
        "experimentalist": "lw-portal-quick-start--experimentalist",
    }

    def _set_active_mode(mode_id: str) -> None:
        nonlocal active_mode_id
        if mode_id == active_mode_id:
            return
        active_mode_id = mode_id
        classes = [cls for cls in quick_start.css_classes if not cls.startswith("lw-portal-quick-start--")]
        mode_cls = quick_start_mode_classes.get(mode_id)
        if mode_cls:
            classes.append(mode_cls)
        quick_start.css_classes = classes
        quick_start_cards[:] = [_quick_start_grid(mode_id)]
        _apply_mode_animation()
        for key, button in mode_buttons.items():
            classes = [cls for cls in button.css_classes if cls != "lw-portal-qs-top-tab--active"]
            if key == mode_id:
                classes.append("lw-portal-qs-top-tab--active")
            button.css_classes = classes

    mode_tabs: list[pn.widgets.Button] = []
    mode_label_by_id = {
        "user": "User",
        "modeler": "Modeler",
        "experimentalist": "Experimentalist",
    }
    mode_class_by_id = {
        "user": "lw-portal-qs-top-tab--user",
        "modeler": "lw-portal-qs-top-tab--modeler",
        "experimentalist": "lw-portal-qs-top-tab--experimentalist",
    }
    for mode in QUICK_START_MODES:
        classes = ["lw-portal-qs-top-tab"]
        mode_class = mode_class_by_id.get(mode.mode_id)
        if mode_class:
            classes.append(mode_class)
        if mode.mode_id == active_mode_id:
            classes.append("lw-portal-qs-top-tab--active")
        button = pn.widgets.Button(
            name=mode_label_by_id.get(mode.mode_id, mode.title),
            button_type="default",
            margin=0,
            css_classes=classes,
            sizing_mode="fixed",
            width=124,
            height=28,
        )
        mode_buttons[mode.mode_id] = button
        mode_tabs.append(button)
        button.on_click(lambda _event, mid=mode.mode_id: _set_active_mode(mid))

    mode_tabs_row = pn.Row(
        *mode_tabs,
        css_classes=["lw-portal-quick-start-tabs"],
        margin=(0, 0, 10, 0),
    )

    quick_start_main = pn.Column(
        pn.pane.HTML('<div class="lw-portal-section-title">Quick Start</div>', margin=0),
        quick_start_cards,
        css_classes=["lw-portal-quick-start-main"],
        margin=0,
        sizing_mode="stretch_width",
    )
    quick_start = pn.Column(
        pn.Column(
            mode_tabs_row,
            quick_start_main,
            css_classes=["lw-portal-quick-start-shell"],
            margin=0,
            sizing_mode="stretch_width",
        ),
        css_classes=["lw-portal-quick-start"],
        sizing_mode="stretch_width",
        margin=0,
    )
    quick_start.css_classes = [
        *quick_start.css_classes,
        quick_start_mode_classes.get(active_mode_id, "lw-portal-quick-start--modeler"),
    ]
    root.append(quick_start)

    # Lanes
    for lane in LANES:
        lane_items = [ITEMS[item_id] for item_id in lane.item_ids if ITEMS[item_id].status != "hidden"]
        root.append(
            render_lane(
                lane,
                items=lane_items,
                notebook_urls=notebook_urls,
                notebook_names=notebook_names,
            )
        )

    template.main.append(root)
    template.main.append(build_footer())
    return template
