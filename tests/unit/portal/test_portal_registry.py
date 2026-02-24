from __future__ import annotations

import pytest

from larvaworld.portal.landing_registry import ITEMS
from larvaworld.portal.registry_logic import read_showcase_mode, validate_registry
from larvaworld.portal.serve import SERVED_APP_IDS


def test_validate_registry_strict_passes() -> None:
    validate_registry(strict=True)


def test_ready_panel_apps_are_served() -> None:
    ready_panel_app_ids = {
        item.panel_app_id
        for item in ITEMS.values()
        if item.kind == "panel_app" and item.status == "ready"
    }
    assert None not in ready_panel_app_ids
    assert {x for x in ready_panel_app_ids if x is not None} <= SERVED_APP_IDS


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, False),
        ("", False),
        ("0", False),
        ("false", False),
        ("no", False),
        ("off", False),
        ("1", True),
        ("true", True),
        ("yes", True),
        ("on", True),
        ("TRUE", True),
        (" YeS ", True),
    ],
)
def test_read_showcase_mode_parsing(monkeypatch, value: str | None, expected: bool) -> None:
    if value is None:
        monkeypatch.delenv("LARVAWORLD_SHOWCASE", raising=False)
    else:
        monkeypatch.setenv("LARVAWORLD_SHOWCASE", value)

    assert read_showcase_mode() is expected

