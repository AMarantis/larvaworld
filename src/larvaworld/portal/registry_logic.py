from __future__ import annotations

import os
import warnings

from larvaworld.portal.landing_registry import ITEMS, LANES, PINNED_QUICK_START
from larvaworld.portal.registry_types import LandingItem, PrimaryAction


_TRUTHY = {"1", "true", "yes", "on"}


def read_showcase_mode() -> bool:
    # English comments inside code.
    value = os.getenv("LARVAWORLD_SHOWCASE", "").strip().lower()
    return value in _TRUTHY


def validate_registry(*, strict: bool = True) -> None:
    # English comments inside code.
    def _err(msg: str) -> None:
        raise ValueError(f"[larvaworld.portal] {msg}")

    referenced: list[str] = []
    referenced.extend(PINNED_QUICK_START)
    for lane in LANES:
        referenced.extend(lane.item_ids)

    missing = [item_id for item_id in referenced if item_id not in ITEMS]
    if missing:
        _err(f"Missing item definitions for: {missing}")

    if len(PINNED_QUICK_START) != len(set(PINNED_QUICK_START)):
        _err("Duplicate IDs in PINNED_QUICK_START")

    hidden_in_refs = [item_id for item_id in referenced if ITEMS[item_id].status == "hidden"]
    if hidden_in_refs:
        _err(f"Hidden items must not be referenced in lanes/pinned: {hidden_in_refs}")

    # Validate that each item listed in a lane matches the lane enum in the item itself.
    for lane in LANES:
        for item_id in lane.item_ids:
            item = ITEMS[item_id]
            if item.lane != lane.lane:
                _err(
                    f"Item '{item_id}' has lane='{item.lane}' but is listed under lane='{lane.lane}'"
                )

    for item in ITEMS.values():
        # Basic non-empty copy checks.
        if not item.title.strip():
            _err(f"Item '{item.id}' has empty title")
        if not item.subtitle.strip():
            _err(f"Item '{item.id}' has empty subtitle")
        if not item.cta.strip():
            _err(f"Item '{item.id}' has empty cta")

        # Kind-specific invariants.
        if item.kind == "panel_app":
            if not item.panel_app_id:
                _err(f"panel_app item '{item.id}' missing panel_app_id")
            if strict and item.panel_app_id != item.id:
                _err(
                    f"panel_app item '{item.id}' must have panel_app_id == id (got '{item.panel_app_id}')"
                )
        elif item.kind == "external_link":
            if not item.url:
                _err(f"external_link item '{item.id}' missing url")
        elif item.kind == "placeholder":
            if strict and item.url is not None:
                _err(f"placeholder item '{item.id}' must not define url")

        # Optional warning: planned items without any learn_more links.
        if item.status == "planned":
            has_links = bool(
                item.learn_more
                and (item.learn_more.issue_url or item.learn_more.docs_url)
            )
            if not has_links:
                warnings.warn(
                    f"[larvaworld.portal] planned item '{item.id}' has no learn_more links",
                    stacklevel=2,
                )


def resolve_target(item: LandingItem) -> str | None:
    # English comments inside code.
    if item.kind == "panel_app":
        return f"/{item.panel_app_id}"
    if item.kind == "external_link":
        return item.url
    return None


def compute_badges(item: LandingItem) -> list[str]:
    # English comments inside code.
    badges: list[str] = []

    if item.level == "core":
        badges.append("Core")
    elif item.level == "advanced":
        badges.append("Advanced")
    elif item.level == "demo":
        badges.append("Demo")

    if item.status == "planned":
        badges.append("Planned")

    for extra in item.badges:
        if extra not in badges:
            badges.append(extra)

    return badges


def compute_primary_action(item: LandingItem, *, showcase_mode: bool) -> PrimaryAction:
    # English comments inside code.
    if item.status == "hidden":
        return PrimaryAction(label="Hidden", href=None, enabled=False)

    if item.kind == "panel_app":
        return PrimaryAction(label=item.cta, href=resolve_target(item), enabled=True)

    if item.kind == "external_link":
        return PrimaryAction(label=item.cta, href=item.url, enabled=True)

    # Placeholders / planned workflows.
    if showcase_mode and item.preview_md:
        return PrimaryAction(
            label="Preview", href=f"/preview?id={item.id}", enabled=True
        )

    if item.learn_more and (item.learn_more.issue_url or item.learn_more.docs_url):
        href = item.learn_more.issue_url or item.learn_more.docs_url
        return PrimaryAction(label="Learn more", href=href, enabled=True)

    return PrimaryAction(label="Planned", href=None, enabled=False)

