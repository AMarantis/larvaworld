from __future__ import annotations

import json
from html import escape

import panel as pn

from larvaworld.portal.notebook_workspace import launch_notebook_for_item


def _query_param(name: str) -> str | None:
    # English comments inside code.
    values = pn.state.session_args.get(name, [])
    if not values:
        return None
    value = values[0]
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="ignore")
    return str(value)


def _error_view(message: str) -> pn.viewable.Viewable:
    # English comments inside code.
    html = (
        '<div style="max-width:720px;margin:36px auto;padding:16px 18px;'
        "border:1px solid rgba(0,0,0,0.15);border-radius:12px;"
        'font-family:system-ui, -apple-system, Segoe UI, Roboto, sans-serif;">'
        '<h3 style="margin:0 0 10px 0;">Notebook launch unavailable</h3>'
        f'<p style="margin:0 0 10px 0;">{escape(message)}</p>'
        '<p style="margin:0;"><a href="/landing">Back to landing</a></p>'
        "</div>"
    )
    return pn.Column(pn.pane.HTML(html, margin=0), sizing_mode="stretch_width")


def notebook_launch_app() -> pn.viewable.Viewable:
    # English comments inside code.
    pn.extension()

    item_id = (_query_param("id") or "").strip()
    if not item_id:
        return _error_view("Missing notebook id.")

    notebook_url, error = launch_notebook_for_item(item_id)
    if not notebook_url:
        return _error_view(error or "Notebook runtime is unavailable.")

    js_url = json.dumps(notebook_url)
    redirect = (
        f"<script>window.location.replace({js_url});</script>"
        "<p>Opening notebook...</p>"
        f'<p>If you are not redirected, <a href="{escape(notebook_url)}">open it here</a>.</p>'
    )
    return pn.Column(
        pn.pane.HTML(redirect, margin=30),
        sizing_mode="stretch_width",
    )
