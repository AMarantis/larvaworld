from __future__ import annotations

from .environment_mapping import env_params_to_canvas_state
from .environment_models import (
    CanvasArena,
    CanvasRingOverlay,
    CanvasObject,
    CanvasObjectType,
    EnvironmentCanvasState,
    LarvaPreviewFrame,
)

__all__ = [
    "CanvasArena",
    "CanvasRingOverlay",
    "CanvasObject",
    "CanvasObjectType",
    "EnvironmentCanvasState",
    "LarvaPreviewFrame",
    "env_params_to_canvas_state",
]


def __getattr__(name: str):
    if name == "EnvironmentCanvas":
        from .environment_canvas import EnvironmentCanvas

        return EnvironmentCanvas
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
