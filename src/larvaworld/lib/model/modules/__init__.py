"""
Modules comprising the layered behavioral architecture modeling the nervous system,body and metabolism
"""


# from . import crawler, turner,crawl_bend_interference,intermitter

__displayname__ = "Modular behavioral architecture"

# Public API: explicit, lazy re-exports of commonly used symbols
__all__ = [
    "Brain",
    "DefaultBrain",
    "Locomotor",
    "Crawler",
    "Turner",
    "Intermitter",
    "BranchIntermitter",
    "Sensor",
    "Memory",
    "Feeder",
    "Oscillator",
    "moduleDB",
    # Robot/actuator modules
    "RotTriangle",
    "Actuator",
    "MotorController",
    "ProximitySensor",
]

_NAME_TO_MODULE = {
    "Brain": "larvaworld.lib.model.modules.brain",
    "DefaultBrain": "larvaworld.lib.model.modules.brain",
    "Locomotor": "larvaworld.lib.model.modules.locomotor",
    "Crawler": "larvaworld.lib.model.modules.crawler",
    "Turner": "larvaworld.lib.model.modules.turner",
    "Intermitter": "larvaworld.lib.model.modules.intermitter",
    "BranchIntermitter": "larvaworld.lib.model.modules.intermitter",
    "Sensor": "larvaworld.lib.model.modules.sensor",
    "Memory": "larvaworld.lib.model.modules.memory",
    "Feeder": "larvaworld.lib.model.modules.feeder",
    "Oscillator": "larvaworld.lib.model.modules.oscillator",
    "moduleDB": "larvaworld.lib.model.modules.module_modes",
    # Robot/actuator modules
    "RotTriangle": "larvaworld.lib.model.modules.rot_surface",
    "Actuator": "larvaworld.lib.model.modules.motor_controller",
    "MotorController": "larvaworld.lib.model.modules.motor_controller",
    "ProximitySensor": "larvaworld.lib.model.modules.sensor2",
}

def __getattr__(name):
    """
    Lazily resolve public symbols on first access to avoid importing
    heavy submodules at package import time.
    """
    module_path = _NAME_TO_MODULE.get(name)
    if module_path is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    from importlib import import_module

    mod = import_module(module_path)
    obj = getattr(mod, name)
    globals()[name] = obj  # cache for subsequent lookups
    return obj

def __dir__():  # help tooling: list public symbols
    return sorted(list(globals().keys()) + __all__)
