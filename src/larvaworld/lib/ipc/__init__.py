"""
Interface between a larvaworld simulation and a remote model
"""

__displayname__ = "Client-Server"

__all__ = ["Client", "Server", "BrianInterfaceMessage"]

from .ipc import Client, Server


class BrianInterfaceMessage(ipc.Message):
    def __init__(self, sim_id, model_id, step, **params):
        self.sim_id = sim_id
        self.model_id = model_id
        self.step = step
        self.params = params

    def _get_args(self):
        return [self.sim_id, self.model_id, self.step], self.params

    def with_params(self, **params):
        return BrianInterfaceMessage(self.sim_id, self.model_id, self.step, **params)

    def param(self, key):
        try:
            return self.params[key]
        except Exception:
            return None
