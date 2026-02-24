from __future__ import annotations

import os
from importlib import import_module
from typing import Any, Callable


# String-only mapping to keep unit tests free of heavy imports.
APP_ID_TO_FACTORY_PATH: dict[str, str] = {
    # Portal apps
    "landing": "larvaworld.portal.landing_app:landing_app",
    "preview": "larvaworld.portal.preview_app:preview_app",
    # Legacy destinations (served as-is)
    "track_viewer": "larvaworld.dashboards.track_viewer:track_viewer_app",
    "experiment_viewer": "larvaworld.dashboards.experiment_viewer:experiment_viewer_app",
    "larva_models": "larvaworld.dashboards.model_inspector:model_inspector_app",
    "locomotory_modules": "larvaworld.dashboards.module_inspector:module_inspector_app",
    "lateral_oscillator": "larvaworld.dashboards.lateral_oscillator_inspector:lateral_oscillator_app",
}

SERVED_APP_IDS: set[str] = set(APP_ID_TO_FACTORY_PATH.keys())


def _import_attr(path: str) -> object:
    # English comments inside code.
    module_name, attr_name = path.split(":", 1)
    module = import_module(module_name)
    return getattr(module, attr_name)


def main() -> None:
    # English comments inside code.
    import panel as pn

    port = int(os.getenv("LARVAWORLD_PORTAL_PORT", "5006"))

    apps: dict[str, Callable[..., Any]] = {
        app_id: _import_attr(factory_path)
        for app_id, factory_path in APP_ID_TO_FACTORY_PATH.items()
    }

    pn.serve(apps, port=port, show=False)


if __name__ == "__main__":
    main()
