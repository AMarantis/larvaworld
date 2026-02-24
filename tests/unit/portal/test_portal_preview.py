from __future__ import annotations

import panel as pn

from larvaworld.portal.preview_app import preview_app


def _first_markdown_object(viewable: pn.viewable.Viewable) -> str:
    # English comments inside code.
    # MaterialTemplate.main is a list-like container with `.objects`.
    panes = []
    if hasattr(viewable, "main") and hasattr(viewable.main, "objects"):  # type: ignore[attr-defined]
        panes = list(viewable.main.objects)  # type: ignore[attr-defined]
    for pane in panes:
        if isinstance(pane, pn.Column) and hasattr(pane, "objects"):
            for child in pane.objects:
                if isinstance(child, pn.pane.Markdown):
                    return str(child.object)
        if isinstance(pane, pn.pane.Markdown):
            return str(pane.object)
    raise AssertionError("No Markdown pane found in preview_app output.")


def test_preview_unknown_id_contains_back_link() -> None:
    view = preview_app(preview_id="unknown")
    text = _first_markdown_object(view)
    assert "Unknown preview id" in text
    assert "Back to landing" in text
    assert "(/landing)" in text


def test_preview_missing_id_contains_back_link() -> None:
    view = preview_app(preview_id=None)
    text = _first_markdown_object(view)
    assert "Unknown preview id" in text
    assert "Back to landing" in text
    assert "(/landing)" in text

