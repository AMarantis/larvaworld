"""
Plotting facade providing lazy access to submodules to keep imports lightweight.

Public usage remains the same: symbols are available under
`larvaworld.lib.plot.<submodule>` and are loaded on first access.
"""

__displayname__ = "Plotting"

__all__ = [
    "util",
    "base",
    "bar",
    "bearing",
    "box",
    "deb",
    "epochs",
    "freq",
    "grid",
    "hist",
    "metric",
    "scape",
    "stridecycle",
    "time",
    "traj",
    "table",
]

_SUBMODULES = {name: f"{__name__}.{name}" for name in __all__}

def __getattr__(name):
    module_path = _SUBMODULES.get(name)
    if module_path is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    from importlib import import_module

    mod = import_module(module_path)
    globals()[name] = mod
    return mod

def __dir__():
    return sorted(list(globals().keys()) + __all__)
