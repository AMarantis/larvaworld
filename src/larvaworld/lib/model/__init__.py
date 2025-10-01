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
    # modules
    "moduleDB",
    # agents (newly added)
    "Larva",
    "BaseController", 
    "LarvaSim",
    # envs (newly added)
    "Arena",
    "Maze",
    "Box",
    "Wall",
    # modules (newly added)
    "Brain",
    "DefaultBrain",
    "Locomotor",
    "SpaceDict",
    "Effector",
    "Timer",
    "LightSource",
    "NengoBrain",
    # deb (newly added)
    "DEB",
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
    # modules
    "moduleDB": "larvaworld.lib.model.modules.module_modes",
    "Larva": "larvaworld.lib.model.agents.larva_robot",
    "BaseController": "larvaworld.lib.model.agents._larva_sim",
    "LarvaSim": "larvaworld.lib.model.agents._larva_sim",
    "Arena": "larvaworld.lib.model.envs.arena",
    "Maze": "larvaworld.lib.model.envs.maze",
    "Box": "larvaworld.lib.model.envs.obstacle",
    "Wall": "larvaworld.lib.model.envs.obstacle",
    "Brain": "larvaworld.lib.model.modules.brain",
    "DefaultBrain": "larvaworld.lib.model.modules.brain",
    "Locomotor": "larvaworld.lib.model.modules.locomotor",
    "SpaceDict": "larvaworld.lib.model.modules.module_modes",
    "Effector": "larvaworld.lib.model.modules.effector",
    "Timer": "larvaworld.lib.model.modules.timer",
    "LightSource": "larvaworld.lib.model.modules.rot_surface",
    "NengoBrain": "larvaworld.lib.model.modules.nengobrain",
    "DEB": "larvaworld.lib.model.deb.deb",
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
