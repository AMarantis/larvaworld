from __future__ import annotations
from typing import Any
import os
import warnings

# Deprecation: discourage deep imports from internal module paths
if os.getenv("LARVAWORLD_STRICT_DEPRECATIONS") == "1":
    raise ImportError(
        "Deep import path deprecated. Use public API: 'from larvaworld.lib.model.modules import basic'"
    )
else:
    warnings.warn(
        "Deep import path deprecated. Use public API: 'from larvaworld.lib.model.modules import basic'",
        DeprecationWarning,
        stacklevel=2,
    )
import numpy as np
import param

from ...param import PositiveNumber
from ..modules.oscillator import Oscillator, Timer

__all__: list[str] = [
    "Effector",
    "StepEffector",
    "StepOscillator",
    "SinOscillator",
    "NengoEffector",
]


class Effector(Timer):
    input_noise = param.Magnitude(
        0.0,
        step=0.01,
        precedence=-3,
        label="input noise",
        doc="The noise applied at the input of the module.",
    )
    output_noise = param.Magnitude(
        0.0,
        step=0.01,
        precedence=-3,
        label="output noise",
        doc="The noise applied at the output of the module.",
    )
    input_range = param.Range(
        precedence=-3, label="input range", doc="The input range of the module."
    )
    output_range = param.Range(
        precedence=-3, label="output range", doc="The output range of the module."
    )

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.input = 0
        self.output = 0

    def update_output(self, output: Any) -> Any:
        return self.apply_noise(output, self.output_noise, self.output_range)

    def update_input(self, input: Any) -> Any:
        return self.apply_noise(input, self.input_noise, self.input_range)

    def apply_noise(self, value: Any, noise: float = 0, range: Any | None = None) -> Any:
        if type(value) in [int, float]:
            value *= 1 + np.random.normal(scale=noise)
            if range is not None and len(range) == 2:
                A0, A1 = range
                if value > A1:
                    value = A1
                elif value < A0:
                    value = A0
        elif isinstance(value, dict):
            for k, v in value.items():
                value[k] = self.apply_noise(v, noise)
        else:
            pass
        return value

    def get_output(self, t: float) -> Any:
        return self.output

    def update(self) -> None:
        pass

    def act(self, **kwargs: Any) -> None:
        pass

    def inact(self, **kwargs: Any) -> None:
        pass

    def step(self, A_in: float = 0, **kwargs: Any) -> Any:
        self.input = self.update_input(A_in)
        self.update()
        if self.active:
            self.act(**kwargs)
        else:
            self.inact(**kwargs)
        self.output = self.update_output(self.output)
        return self.output


class StepEffector(Effector):
    amp = PositiveNumber(
        1.0,
        allow_None=True,
        label="oscillation amplitude",
        doc="The initial amplitude of the oscillation.",
    )

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    @property
    def Act_coef(self) -> Any:
        return self.amp

    @property
    def Act_Phi(self) -> float:
        return 1

    @property
    def Act(self) -> Any:
        return self.Act_coef * self.Act_Phi

    def set_amp(self, v: Any) -> None:
        self.amp = v

    def get_amp(self, t: float) -> Any:
        return self.amp

    def act(self) -> None:
        self.output = self.Act

    def inact(self) -> None:
        self.output = 0


class StepOscillator(Oscillator, StepEffector):
    def act(self) -> None:
        self.oscillate()
        self.output = self.Act


class SinOscillator(StepOscillator):
    @property
    def Act_Phi(self) -> float:
        return np.sin(self.phi)


class NengoEffector(StepOscillator):
    def start_effector(self) -> None:
        super().start_effector()
        self.set_freq(self.initial_freq)

    def stop_effector(self) -> None:
        super().stop_effector()
        self.set_freq(0)
