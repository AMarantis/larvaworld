from __future__ import annotations

import panel as pn

from larvaworld.portal.landing_registry import ITEMS, LANES
from larvaworld.portal.panel_components import PORTAL_RAW_CSS, build_template_header
from larvaworld.portal.registry_logic import read_showcase_mode, validate_registry


def _preview_ids() -> list[str]:
    # English comments inside code.
    ids: list[str] = []
    for lane in LANES:
        for item_id in lane.item_ids:
            item = ITEMS[item_id]
            if item.status == "planned" and item.preview_md:
                ids.append(item_id)
    return ids


def preview_app(preview_id: str | None = None) -> pn.viewable.Viewable:
    # English comments inside code.
    pn.extension(raw_css=[PORTAL_RAW_CSS])
    validate_registry(strict=True)

    showcase_mode = read_showcase_mode()

    if preview_id is None:
        try:
            raw = pn.state.location.query_params.get("id")  # type: ignore[union-attr]
            if isinstance(raw, list):
                preview_id = raw[0] if raw else None
            else:
                preview_id = raw
        except Exception:
            preview_id = None

    item = ITEMS.get(preview_id) if preview_id else None

    template = pn.template.MaterialTemplate(
        title="Larvaworld Portal — Preview",
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
        showcase_mode=showcase_mode,
        on_dark_mode_change=_set_dark_mode,
    )
    template.header.append(topbar)

    back = "[Back to landing](/landing)"

    if not item or not item.preview_md:
        unknown = preview_id if preview_id else "<missing>"
        available = _preview_ids()
        available_md = ""
        if available:
            available_md = "\n\nAvailable preview ids:\n" + "\n".join(f"- `{x}`" for x in available)

        md = f"## Preview\n\nUnknown preview id: {unknown}\n\n{back}{available_md}"
        root.append(pn.pane.Markdown(md, sizing_mode="stretch_width"))
        template.main.append(root)
        return template

    learn_more_lines: list[str] = []
    if item.learn_more and item.learn_more.issue_url:
        learn_more_lines.append(
            f"[Learn more (GitHub issues)]({item.learn_more.issue_url})"
        )
    if item.learn_more and item.learn_more.docs_url:
        learn_more_lines.append(f"[Docs]({item.learn_more.docs_url})")

    footer = ""
    if learn_more_lines:
        footer = "\n\n---\n\n" + " · ".join(learn_more_lines)

    md = f"# {item.title}\n\n{item.preview_md}\n\n{back}{footer}"
    root.append(pn.pane.Markdown(md, sizing_mode="stretch_width"))
    template.main.append(root)
    return template
