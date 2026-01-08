# Module Interaction

This page describes how Larvaworld's modules interact **at runtime** during simulation execution. Understanding these interactions is crucial for extending the platform or debugging behavior.

---

## High-Level Interaction Flow

```{mermaid}
sequenceDiagram
    participant User as User
    participant CLI as CLI
    participant SimEngine as SimEngine
    participant LarvaAgent as LarvaAgent
    participant Brain as Brain
    participant Crawler as Crawler
    participant Feeder as Feeder
    participant Sensor as Sensor
    participant Environment as Environment

    User->>CLI: Run simulation command
    CLI->>SimEngine: Initialize simulation
    SimEngine->>Environment: Create arena
    SimEngine->>LarvaAgent: Create larva agents

    loop Simulation Loop
        SimEngine->>LarvaAgent: Update timestep
        LarvaAgent->>Sensor: Read environment
        Sensor->>Environment: Get sensory input
        Environment-->>Sensor: Return sensory data
        Sensor-->>LarvaAgent: Sensory feedback

        LarvaAgent->>Brain: Process sensory input
        Brain->>Crawler: Generate crawling commands
        Brain->>Feeder: Generate feeding commands

        Crawler-->>LarvaAgent: Movement commands
        Feeder-->>LarvaAgent: Feeding commands

        LarvaAgent->>Environment: Execute actions
        Environment-->>LarvaAgent: Action results

        LarvaAgent-->>SimEngine: Update state
        SimEngine->>SimEngine: Record data
    end

    SimEngine-->>CLI: Simulation complete
    CLI-->>User: Results available
```

---

## Detailed Phase-by-Phase Breakdown

### Phase 1: Initialization

**Sequence**:

1. **User Command**: User runs `larvaworld Exp chemotaxis -N 20`
2. **CLI Parsing**: `argparser.py` parses arguments
3. **SimEngine Setup**: `ExpRun.__init__()` initializes
4. **Environment Creation**: `Env` object created with arena, food, odorscape
5. **Agent Creation**: `LarvaSim` objects created (N=20)
6. **Module Initialization**: Each larva initializes Brain, Locomotor, Sensors

**Code Path**:

```python
# cli/main.py
main() → SimModeParser.parse_args()

# sim/single_run.py
ExpRun.__init__() → self.build_env() → self.build_agents()

# model/envs/env.py
Env.__init__() → create arena, food_grid, odorscape

# model/agents/larva_robot.py
LarvaSim.__init__() → Brain(), Locomotor(), Sensors()
```

---

### Phase 2: Simulation Loop

The core execution loop runs for `Nsteps` timesteps (typically `duration * 600` for 0.1s timestep).

#### 2.1 Timestep Update

**SimEngine → LarvaAgent**: "Update to step t"

**Code**:

```python
# sim/base_run.py (BaseRun.simulate)
for step in range(self.Nsteps):
    self.model.step()  # Agentpy ABM step
```

#### 2.2 Sensory Input

**LarvaAgent → Sensors → Environment**

**Sequence**:

1. Larva queries sensors
2. Sensors read environment state (odor, food, obstacles)
3. Environment returns sensory data
4. Sensors process and return to larva

**Code (excerpt)**:

```python
# model/agents/_larva.py (LarvaMotile.step)
self.cum_dur += m.dt
self.sense()                      # placeholder; subclasses/robots can override
pos = self.olfactor_pos
if m.space.accessible_sources:
    self.food_detected = m.space.accessible_sources[self]
elif self.brain.locomotor.feeder or self.brain.toucher:
    self.food_detected = util.sense_food(
        pos, sources=m.sources, grid=m.food_grid, radius=self.radius
    )
self.resolve_carrying(self.food_detected)
lin, ang, self.feeder_motion = self.brain.step(
    pos, length=self.length, on_food=self.on_food
)
```

**Olfactory Example**:

```python
# model/modules/sensor.py (class Olfactor)
from larvaworld.lib.model.modules.sensor import Olfactor

olf = Olfactor(brain=my_brain, decay_coef=0.15, perception="log")
olf.step(input={"odor_A": 0.6, "odor_B": 0.2})
print("First odor:", olf.first_odor_concentration)
```

#### 2.3 Neural Processing

**LarvaAgent → Brain**: "Process sensory input"

**Brain Responsibilities**:

- Integrate multi-sensory information
- Update memory (reinforcement learning, gain adaptation)
- Generate locomotor commands

**Code**:

```python
# model/modules/brain.py (DefaultBrain.step)
def step(self, pos, on_food: bool = False, **kwargs):
    # 1. Sense environment and update neural drive
    self.sense(pos=pos, reward=on_food)

    # 2. Compute locomotor commands (crawler/turner/feeder)
    return self.locomotor.step(A_in=self.A_in, on_food=on_food, **kwargs)
```

#### 2.4 Motor Command Generation

**Brain → Crawler/Turner/Feeder**: "Generate actions"

**Locomotor Coordination**:

```python
# model/modules/locomotor.py (Locomotor.step)
def step(self, A_in=0, length=1, on_food=False):
    C, F, T, If = self.crawler, self.feeder, self.turner, self.interference
    if If:
        If.cur_attenuation = 1
    if F:
        F.step()
        if F.active and If:
            If.check_module(F, "Feeder")
    if C:
        lin = C.step() * length
        if C.active and If:
            If.check_module(C, "Crawler")
    else:
        lin = 0

    # Run/pause/feed state machine
    self.step_intermitter(
        stride_completed=self.stride_completed,
        feed_motion=self.feed_motion,
        on_food=on_food,
    )

    # Turning with optional crawl–turn interference
    if T:
        if If:
            cur_att_in, cur_att_out = If.apply_attenuation(If.cur_attenuation)
        else:
            cur_att_in, cur_att_out = 1, 1
        ang = T.step(A_in=A_in * cur_att_in) * cur_att_out
    else:
        ang = 0
    return lin, ang, self.feed_motion
```

#### 2.5 Action Execution

**LarvaAgent → Environment**: "Execute actions"

**Physics Update**:

```python
# model/agents/_larva.py (LarvaMotile.step)
lin, ang, self.feeder_motion = self.brain.step(
    pos, length=self.length, on_food=self.on_food
)
self.prepare_motion(lin=lin, ang=ang)
```

**Feeding Action**:

```python
# model/agents/_larva.py (LarvaMotile.feed)
def feed(self, source, motion):
    def get_max_V_bite():
        return self.brain.locomotor.feeder.V_bite * self.V * 1000

    if motion and source is not None:
        grid = self.model.food_grid
        a_max = get_max_V_bite()
        if grid:
            V = -grid.add_cell_value(source, -a_max)
        else:
            V = source.subtract_amount(a_max)
        return V
    return 0
```

**DEB Update** (energetics):

```python
# model/agents/_larva.py (LarvaMotile.run_energetics)
def run_energetics(self, V_eaten):
    self.deb.run_check(dt=self.model.dt, X_V=V_eaten)
    self.length = self.deb.Lw * 10 / 1000
    self.mass = self.deb.Ww
    self.V = self.deb.V
```

#### 2.6 State Recording

**SimEngine**: Record data

**Data Collection**:

```python
# sim/base_run.py (BaseRun.set_collectors)
self.collectors = reg.par.get_reporters(cs=cs, agents=self.agents)

# sim/single_run.py (update/end)
self.agents.nest_record(self.collectors["step"])  # per-step variables
...
self.agents.nest_record(self.collectors["end"])   # endpoint variables

# sim/single_run.py (simulate)
self.data_collection = LarvaDatasetCollection.from_agentpy_output(self.output)
self.datasets = self.data_collection.datasets
```

---

### Phase 3: Finalization

**Sequence**:

1. **SimEngine**: Simulation loop completes
2. **Data Processing**: Convert raw data to `LarvaDataset`
3. **Storage**: Save to HDF5
4. **Visualization**: Generate plots (optional)
5. **CLI**: Return control to user

**Code**:

```python
# sim/single_run.py (ExpRun.simulate)
def simulate(self, **kwargs):
    self.run(**kwargs)  # AgentPy run loop
    if getattr(self, "aborted", False):
        self.datasets = []
        return self.datasets

    # Collect into datasets
    self.data_collection = LarvaDatasetCollection.from_agentpy_output(self.output)
    self.datasets = self.data_collection.datasets

    # Optional enrichment and storage
    if self.p.enrichment:
        for d in self.datasets:
            d.enrich(**self.p.enrichment, is_last=False)
    if self.store_data and not getattr(self, "aborted", False):
        self.store()
```

---

## Module Dependencies

### Larva Agent Dependencies

```
LarvaSim
├── LarvaMotile (parent)
│   ├── Brain
│   │   ├── Olfactor (sensor)
│   │   ├── Toucher (sensor)
│   │   ├── Memory (learning)
│   │   └── Locomotor
│   │       ├── Crawler
│   │       ├── Turner
│   │       ├── Feeder
│   │       ├── Intermitter
│   │       └── Interference
│   ├── DEB (energetics)
│   └── Body (morphology)
└── BaseController (parent)
    └── Visualization methods
```

### Environment Dependencies

```
Env
├── Arena (geometry)
├── FoodGrid (food sources)
├── Odorscape (odor gradients)
├── Thermoscape (thermal gradients, optional)
├── Windscape (wind fields, optional)
└── Space (collision detection)
```

---

## Communication Patterns

### 1. Sensor → Environment (Pull)

**Pattern**: Sensors **pull** data from environment on each timestep.

```python
# model/modules/sensor.py (Olfactor.step)
odor_value = self.model.odorscape.get_value(self.pos)
self.sensed_odor = self.process_olfaction(odor_value)
```

### 2. Brain → Locomotor (Command)

**Pattern**: Brain **commands** locomotor modules.

```python
# model/modules/brain.py (DefaultBrain.step)
def step(self, pos, on_food=False, **kwargs):
    self.sense(pos=pos, reward=on_food)
    return self.locomotor.step(A_in=self.A_in, on_food=on_food, **kwargs)
```

### 3. Locomotor → Agent (Update)

**Pattern**: Locomotor modules **update** agent state.

```python
# model/agents/_larva.py (LarvaMotile.step)
lin, ang, self.feeder_motion = self.brain.step(
    pos, length=self.length, on_food=self.on_food
)
self.prepare_motion(lin=lin, ang=ang)  # applies lin/ang to body pose
```

### 4. Agent → Environment (Modify)

**Pattern**: Agents **modify** environment state (feeding, collisions).

```python
# model/agents/_larva.py (LarvaMotile.feed)
if motion and source is not None:
    a_max = self.brain.locomotor.feeder.V_bite * self.V * 1000
    grid = self.model.food_grid
    V = -grid.add_cell_value(source, -a_max) if grid else source.subtract_amount(a_max)
```

### 5. SimEngine → Agent (Broadcast)

**Pattern**: SimEngine **broadcasts** timestep update to all agents.

```python
# sim/single_run.py (ExpRun.step)
self.agents.step()  # AgentPy: steps all agents synchronously
```

## Extending the Platform

### Adding a New Sensor

**Steps**:

1. Create subclass of `Sensor` in `/lib/model/modules/sensor.py`
2. Implement `update()` method to process sensory input
3. Register sensor in `Brain` initialization
4. Add sensory data to `Brain.step()` integration

**Example**:

```python
# model/modules/sensor.py
from larvaworld.lib.model.modules.sensor import Sensor

class MySensor(Sensor):
    def update(self):
        # Query environment (e.g., odorscape / custom field)
        value = self.brain.agent.model.odorscape.get_value(self.brain.agent.pos)

        # Provide input and run base Sensor.update (handles decay/gain/dX)
        self.input = {"my_stimulus": value}
        super().update()

        # Output is now in self.output (and dX/X for changes)
```

### Adding a New Behavioral Module

**Steps**:

1. Create subclass of `Effector` in `/lib/model/modules/`
2. Implement `update()` method
3. Register module in `Locomotor` or `Brain`
4. Add module output to agent actions

**Example**:

```python
# model/modules/custom.py
from larvaworld.lib.model.modules.basic import Effector
import numpy as np

class MyEffector(Effector):
    def update(self):
        # Compute output (e.g., random drive or function of self.input)
        self.output = float(np.random.rand())

    def act(self, **kwargs):
        # Apply action when active (e.g., set torque/velocity)
        pass

    def inact(self, **kwargs):
        # Idle action when inactive
        pass
```

For detailed tutorial, see {doc}`../tutorials/custom_module`.

---

## Related Documentation

- {doc}`architecture_overview` - Platform layers
- {doc}`../agents_environments/larva_agent_architecture` - Agent architecture
- {doc}`../agents_environments/brain_module_architecture` - Brain module details
- {doc}`simulation_modes` - Simulation execution modes
- {doc}`../tutorials/custom_module` - Adding custom modules
