# Brain Module Architecture

The Brain module integrates sensory input, memory systems, and locomotor control. Larvaworld provides two implementations: `DefaultBrain` (standard) and `NengoBrain` (neural network-based).

---

## Brain architecture overview

```{mermaid}
graph TD
    %% Brain implementations
    subgraph Brain_Impl ["Brain Implementations"]
        BrainBase["Brain"<br/>Base class]:::base
        DefaultBrain["DefaultBrain"<br/>Standard implementation]:::impl
        NengoBrain["NengoBrain"<br/>Nengo-based implementation]:::impl
    end

    BrainBase --> DefaultBrain
    BrainBase --> NengoBrain

    %% Modalities
    subgraph Modalities
        OlfMod["olfaction"<br/>odor sensing]:::modality
        TouchMod["touch"<br/>mechanoreception/feeding]:::modality
        ThermoMod["thermosensation"<br/>temperature]:::modality
        WindMod["windsensation"<br/>wind/airflow]:::modality
    end

    %% Sensors
    OlfSensor["Olfactor"<br/>odor sensor]:::sensor
    TouchSensor["Toucher"<br/>contact/food sensor]:::sensor
    ThermoSensor["Thermosensor"<br/>temperature sensor]:::sensor
    WindSensor["Windsensor"<br/>wind sensor]:::sensor

    %% Memory modules
    RLmem["RLOlfMemory / RLTouchMemory"<br/>reinforcement learning]:::memory
    NullMem["No memory"]:::memory

    %% Locomotor interface
    subgraph Locomotor_System ["Locomotor System"]
        Locomotor["Locomotor"<br/>crawl/turn/feed]:::locomotor
        A_in["A_in"<br/>sensory drive]:::signal
        MotorCmds["motor commands"<br/>crawl/turn/feed rates]:::output
    end

    %% Wiring: Brain -> Modalities
    DefaultBrain --> OlfMod
    DefaultBrain --> TouchMod
    DefaultBrain --> ThermoMod
    DefaultBrain --> WindMod

    %% Wiring: Modalities -> Sensors
    OlfMod --> OlfSensor
    TouchMod --> TouchSensor
    ThermoMod --> ThermoSensor
    WindMod --> WindSensor

    %% Wiring: Memory attachment (example: olfaction)
    OlfMod --> RLmem
    TouchMod --> NullMem
    ThermoMod --> NullMem
    WindMod --> NullMem

    %% Wiring: Modalities -> Locomotor
    OlfMod --> A_in
    TouchMod --> A_in
    ThermoMod --> A_in
    WindMod --> A_in

    A_in --> Locomotor
    Locomotor --> MotorCmds

    %% Color definitions
    classDef base fill:#2c3e50,stroke:#34495e,stroke-width:3px,color:#ffffff
    classDef impl fill:#3498db,stroke:#2980b9,stroke-width:2px,color:#ffffff
    classDef modality fill:#9b59b6,stroke:#8e44ad,stroke-width:2px,color:#ffffff
    classDef sensor fill:#f39c12,stroke:#e67e22,stroke-width:2px,color:#ffffff
    classDef signal fill:#e74c3c,stroke:#c0392b,stroke-width:2px,color:#ffffff
    classDef memory fill:#e91e63,stroke:#c2185b,stroke-width:2px,color:#ffffff
    classDef locomotor fill:#27ae60,stroke:#229954,stroke-width:2px,color:#ffffff
    classDef output fill:#f1c40f,stroke:#f39c12,stroke-width:3px,color:#000000
```

---

## Sensory Modalities

The brain organizes sensors into **modalities**, each processing a specific sensory channel:

| Modality            | Sensor Class   | Signal      | Memory   | Purpose              |
| ------------------- | -------------- | ----------- | -------- | -------------------- |
| **olfaction**       | `Olfactor`     | `A` (float) | Optional | Odor detection       |
| **touch**           | `Toucher`      | `A` (float) | Optional | Contact/food sensing |
| **thermosensation** | `Thermosensor` | `A` (float) | Optional | Temperature sensing  |
| **windsensation**   | `Windsensor`   | `A` (float) | Optional | Wind/airflow sensing |

### Modality Structure

```python
# This mirrors `Brain.modalities` (see `larvaworld/lib/model/modules/brain.py`)
modality = {
    "sensor": self.olfactor,        # Sensor instance (or None)
    "func": self.sense_odors,       # Processing function
    "A": 0.0,                       # Sensory drive from this modality
    "mem": None,                    # Optional memory module (per modality)
}
```

---

## Sensor Modules

### Olfactor

**Purpose**: Odor detection

**Key Attributes**:

- `gain_dict` / `gain`: Gain per odor ID (memory can update this per step)
- `X`: Current odor concentrations per odor ID
- `dX`: Perceived change per odor ID (depends on `perception`: `log`/`linear`/`null`)
- `output`: Integrated sensory drive (used as modality `A`)

**Processing**:

1. Query odorscape value layers at larva position (via `Brain.sense_odors`)
2. Compute `dX` from current/previous `X` based on `perception`
3. Integrate `output` using `gain[id] * dX[id]` with exponential decay (`decay_coef`)

**Code Location**: `/lib/model/modules/sensor.py` (class `Olfactor`)

---

### Toucher

**Purpose**: Tactile sensing (touch sensors around the body contour)

**Key Attributes**:

- `touch_sensors`: Indices of touch sensors on the body contour
- `gain_dict` / `gain`: Gain per touch sensor ID
- `X` / `dX` / `output`: Same Sensor state variables as above

**Processing**:

1. `Brain.init_sensors()` registers touch sensors on the agent body
2. `Brain.sense_food_multi()` converts touch sensor positions to a `dict` of `0/1` activations
3. `Toucher.step(input=...)` integrates these into a tactile drive `A`

**Code Location**: `/lib/model/modules/sensor.py` (class `Toucher`)

---

### Windsensor

**Purpose**: Wind/airflow detection

**Key Attributes**:

- `weights`: Wind response weights (passed from brain config)
- `gain_dict` / `gain`: Gain for the `"windsensor"` channel (default `{"windsensor": 1.0}`)
- `perception`: Fixed to `"null"` (direct transduction)

**Code Location**: `/lib/model/modules/sensor.py` (class `Windsensor`)

---

### Thermosensor

**Purpose**: Temperature sensing

**Key Attributes**:

- `gain_dict` / `gain`: Gains for warm/cool channels
- `X` / `dX` / `output`: Same Sensor state variables as above

**Code Location**: `/lib/model/modules/sensor.py` (class `Thermosensor`)

---

## Memory Modules

Memory modules **attach to sensory modalities** and modulate their gain through learning.

### RLmemory

**Algorithm**: Q-learning (reinforcement learning) via a Q-table over discretized sensory change states.

**Mechanism**:

- Uses `rewardSum` + `dx` to update the Q-table and choose gain actions from `gain_space`.

**Code Location**: `/lib/model/modules/memory.py` (`RLmemory` class)

---

### RemoteBrianModelMemory (MB memory)

**Algorithm**: Mushroom Body model (Hebbian learning)

**Mechanism**:

- KC-MBON synaptic plasticity
- Reward-modulated learning

**Code Location**: `/lib/model/modules/memory.py` (`RemoteBrianModelMemory` class)

---

## Locomotor Integration

The brain coordinates locomotor modules through the `Locomotor` class:

```{mermaid}
graph LR
    BRAIN[Brain] --> LOCOMOTOR[Locomotor]
    LOCOMOTOR --> CRAWLER[Crawler]
    LOCOMOTOR --> TURNER[Turner]
    LOCOMOTOR --> FEEDER[Feeder]
    LOCOMOTOR --> INTERMITTER[Intermitter]
```

### Brain → Locomotor Flow

1. **Brain.sense()**: Update each enabled sensor module and its modality drive `A`
2. **Brain.step()**: Call `Locomotor.step(A_in=..., on_food=...)`
3. **Locomotor.step()**: Run crawler/turner/feeder (+ interference + intermitter state machine)

---

## DefaultBrain

**Implementation**: Rule-based sensorimotor control

**Step Sequence**:

```python
def step(self, pos, on_food=False, **kwargs):
    self.sense(pos=pos, reward=on_food)
    return self.locomotor.step(A_in=self.A_in, on_food=on_food, **kwargs)
```

---

## NengoBrain

**Implementation**: Spiking neural network (Nengo)

:::{warning}
`NengoBrain` is experimental. In the current codebase it may fail at runtime with newer `nengo` versions (e.g. `nengo.exceptions.ReadonlyError: probes is read-only`) when initializing internal probes.
If you hit this, use `DefaultBrain` models until `NengoBrain` is updated for the installed `nengo` API.
:::

**Architecture**:

- **Input**: Sensory neurons (olfactory, tactile, etc.)
- **Hidden**: Processing layers
- **Output**: Motor neurons (forward, turn)

**Step Sequence**:

```python
def step(self):
    # See `larvaworld/lib/model/modules/nengobrain.py` for the real implementation.
    # NengoBrain runs an internal Nengo Simulator and maps probe outputs to (lin, ang, feed_motion).
    ...
```

---

## Configuration

### Enable Specific Modalities

```python
from larvaworld.lib import reg
from larvaworld.lib.sim import ExpRun
from larvaworld.lib.util import AttrDict

exp_params = reg.conf.Exp.getID("dish").get_copy()
model_conf = reg.conf.Model.getID("navigator").get_copy()

# Disable modalities by disabling their sensor modules in the brain config
model_conf.brain.windsensor = None
model_conf.brain.thermosensor = None

exp_params.larva_groups = AttrDict(
    {
        "nav": AttrDict(
            {
                "model": model_conf,
                "distribution": AttrDict({"shape": "circle", "mode": "uniform", "N": 5}),
            }
        )
    }
)

run = ExpRun(
    experiment="dish",
    parameters=exp_params,
    duration=0.5,
    screen_kws={"show_display": False, "vis_mode": None},
    store_data=False,
)
run.simulate()
```

### Attach Memory

```python
from larvaworld.lib import reg
from larvaworld.lib.model.modules.module_modes import moduleDB

model_conf = reg.conf.Model.getID("navigator").get_copy()
model_conf.brain.memory = moduleDB.memory_kws(
    mode="RL", modality="olfaction", as_entry=False
)
```

### Use NengoBrain

```python
from larvaworld.lib import reg

# NengoBrain is used when the model's crawler module has mode "nengo".
# Built-in model IDs include many `nengo_*` variants:
nengo_ids = [m for m in reg.conf.Model.confIDs if m.startswith("nengo_")]
print(nengo_ids[:20])
```

---

## Related Documentation

- {doc}`larva_agent_architecture` - Complete agent structure
- {doc}`../concepts/module_interaction` - Runtime interactions
- {doc}`../working_with_larvaworld/single_experiments` - Olfactory learning example
