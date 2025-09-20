"""
All classes supporting objects, agents and environment of the agent-based-modeling
simulations, as well as the modules comprising the layered behavioral architecture
modeling the nervous system, body and metabolism.
"""

__displayname__ = "Modeling"

# Keep legacy access to subpackages but avoid star-imports at import time.
from . import deb, modules, agents, envs, object  # noqa: F401
from .object import *  # noqa: F401,F403 (public surface kept for backwards compatibility)

# Provide a lazy facade for common classes historically re-exported from here.
__all__ = [
    # envs.valuegrid
    "AnalyticalValueLayer",
    "GaussianValueLayer",
    "DiffusionValueLayer",
    "OdorScape",
    "FoodGrid",
    "WindScape",
    "ThermoScape",
    # envs.obstacle
    "Border",
    # agents._source
    "Source",
    "Food",
]

_NAME_TO_MODULE = {
    # envs.valuegrid
    "AnalyticalValueLayer": "larvaworld.lib.model.envs.valuegrid",
    "GaussianValueLayer": "larvaworld.lib.model.envs.valuegrid",
    "DiffusionValueLayer": "larvaworld.lib.model.envs.valuegrid",
    "OdorScape": "larvaworld.lib.model.envs.valuegrid",
    "FoodGrid": "larvaworld.lib.model.envs.valuegrid",
    "WindScape": "larvaworld.lib.model.envs.valuegrid",
    "ThermoScape": "larvaworld.lib.model.envs.valuegrid",
    # envs.obstacle
    "Border": "larvaworld.lib.model.envs.obstacle",
    # agents._source
    "Source": "larvaworld.lib.model.agents._source",
    "Food": "larvaworld.lib.model.agents._source",
}


def __getattr__(name):
    module_path = _NAME_TO_MODULE.get(name)
    if module_path is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    from importlib import import_module

    mod = import_module(module_path)
    obj = getattr(mod, name)
    globals()[name] = obj
    return obj


def __dir__():
    return sorted(list(globals().keys()) + __all__)
