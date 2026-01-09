# Experiment Configuration Pipeline

Larvaworld provides a **systematic configuration pipeline** that balances ease-of-use with flexibility. You can use predefined templates for quick experiments or customize every parameter for detailed research.

---

## Configuration Flow

```{mermaid}
flowchart LR
    Start([Select Experiment Type]) --> LoadTemplate[Load Experiment Template<br/>Predefined configuration]

    LoadTemplate --> ConfigEnv{Configure<br/>Environment}

    ConfigEnv --> ArenaType[Arena Type<br/>Circular, rectangular, custom]
    ConfigEnv --> OdorSetup[Odorscape Setup<br/>Sources, gradients]
    ConfigEnv --> FoodSetup[Food Setup<br/>Patches, grid, quality]
    ConfigEnv --> Obstacles[Obstacles<br/>Borders, walls]

    ArenaType --> ConfigAgents
    OdorSetup --> ConfigAgents
    FoodSetup --> ConfigAgents
    Obstacles --> ConfigAgents

    ConfigAgents{Configure<br/>Agents} --> ModelSelect[Select Larva Model<br/>Basic to complex]
    ConfigAgents --> NumAgents[Number of Agents<br/>N larvae]
    ConfigAgents --> InitPos[Initial Positions<br/>Distribution]
    ConfigAgents --> InitState[Initial State<br/>Age, hunger, etc.]

    ModelSelect --> ConfigSim
    NumAgents --> ConfigSim
    InitPos --> ConfigSim
    InitState --> ConfigSim

    ConfigSim{Configure<br/>Simulation} --> Duration[Duration<br/>Minutes]
    ConfigSim --> Epochs[Epochs<br/>Pre/test/post]
    ConfigSim --> Timestep[Timestep<br/>dt = 0.1 s]
    ConfigSim --> VisMode[Visualization<br/>video/image (export), display (show_display), or headless]

    Duration --> Analysis
    Epochs --> Analysis
    Timestep --> Analysis
    VisMode --> Analysis

    Analysis{Configure<br/>Analysis} --> Metrics[Metrics to Compute<br/>Auto-select by exp type]
    Analysis --> RefData[Reference Data<br/>Compare to real?]
    Analysis --> Output[Output Options<br/>Save location, format]

    Metrics --> Ready
    RefData --> Ready
    Output --> Ready

    Ready[Ready to Run] --> Execute([Execute Simulation])

    style Start fill:#2196f3,stroke:#1976d2,stroke-width:3px,color:#fff
    style ConfigEnv fill:#ff9800,stroke:#f57c00,stroke-width:3px,color:#000
    style ConfigAgents fill:#9c27b0,stroke:#7b1fa2,stroke-width:3px,color:#fff
    style ConfigSim fill:#4caf50,stroke:#388e3c,stroke-width:3px,color:#000
    style Analysis fill:#f44336,stroke:#d32f2f,stroke-width:3px,color:#fff
    style Execute fill:#2196f3,stroke:#1976d2,stroke-width:3px,color:#fff
```

---

## Pipeline Stages

### 1. Select Experiment Type

**Purpose**: Choose from 57 preconfigured experiments.

**Code**:

```python
from larvaworld.lib import reg

# List all available experiments
exp_ids = reg.conf.Exp.confIDs
print(f"Available: {len(exp_ids)} experiments")

# Select an experiment
exp_conf = reg.conf.Exp.getID("chemotaxis")
```

**Predefined Experiments**: See {doc}`experiment_types` for the full list.

---

### 2. Load Template

**Purpose**: Load a complete configuration template.

**Implementation**: Templates are defined in `/lib/reg/stored_confs/sim_conf.py`.

**Template Structure**:

```python
{
    "experiment": "...",      # Experiment ID
    "duration": 5.0,          # Minutes
    "dt": 0.1,                # Seconds
    "env_params": {...},      # Environment configuration
    "larva_groups": {...},    # Larva groups (dict-like, keyed by group_id)
    "trials": {...},          # Trial structure (epochs)
    "enrichment": {...},      # Additional modules
}
```

**Example**:

```python
from larvaworld.lib import reg

exp_conf = reg.conf.Exp.getID("chemotaxis")
print(exp_conf.keys())
# dict_keys(['experiment', 'duration', 'dt', 'env_params', 'larva_groups', 'trials', 'enrichment', ...])
```

---

### 3. Configure Environment

**Purpose**: Set up the virtual arena and stimuli.

#### Arena Type

Load predefined arenas via the registry:

```python
from larvaworld.lib import reg

# Preconfigured circular arena
env_conf = reg.conf.Env.getID("dish")

# Rectangular arena (200mm x 200mm)
env_conf_rect = reg.conf.Env.getID("arena_200mm")
```

#### Odorscape Setup

**Purpose**: Define odor sources and gradients.

**Example**:

```python
from larvaworld.lib import reg, util

env_params = reg.conf.Env.getID("arena_200mm").get_copy()
if env_params.odorscape is None:
    env_params.odorscape = util.AttrDict()
env_params.odorscape.update({"odorscape": "Gaussian", "grid_dims": (51, 51)})
```

#### Food Setup

**Purpose**: Place food sources.

**Options**:

- **Patches**: Discrete food patches
- **Grid**: Regular grid of patches
- **Uniform**: Continuous substrate

**Example**:

```python
from larvaworld.lib import reg, util

env_params = reg.conf.Env.getID("arena_200mm").get_copy()
if env_params.food_params is None:
    env_params.food_params = util.AttrDict()
if not getattr(env_params.food_params, "source_units", None):
    env_params.food_params.source_units = {}

env_params.food_params.source_units["apple_patch"] = {
    "pos": (0.02, 0.0),
    "radius": 0.005,  # 5 mm
    "amount": 3.0,
    "odor": {"id": "apple", "intensity": 1.0, "spread": 0.02},
    "color": "green",
    "regeneration": False,
}
```

#### Obstacles

**Purpose**: Add borders or walls.

**Example**:

```python
from larvaworld.lib import reg, util

env_params = reg.conf.Env.getID("arena_200mm").get_copy()
env_params.border_list = {
    "wall0": {"vertices": [(0.0, 0.0), (0.1, 0.0), (0.1, 0.1), (0.0, 0.1)]}
}
```

For detailed environment options, see {doc}`../agents_environments/arenas_and_substrates`.

---

### 4. Configure Agents

**Purpose**: Define larva models and initial conditions.

#### Model Selection

Retrieve stored models from the registry:

```python
from larvaworld.lib import reg

model_conf = reg.conf.Model.getID("explorer")
larva_groups = reg.gen.LarvaGroup(mID="explorer", N=10).entry("explorer")
print("model loaded:", getattr(model_conf, "name", "explorer"))
```

#### Number of Agents

**Parameter**: `N` (default: 10)

```python
from larvaworld.lib import reg

larva_groups = {}
larva_groups.update(reg.gen.LarvaGroup(mID="explorer", N=20).entry("explorer"))
larva_groups.update(reg.gen.LarvaGroup(mID="navigator", N=10).entry("navigator"))
```

#### Initial Positions

Set initial distribution with registry-compatible keys:

```python
from larvaworld.lib import reg

larva_groups = reg.gen.LarvaGroup(
    mID="explorer",
    N=20,
    mode="uniform",
    loc=(0.0, 0.0),           # center (x, y) in meters
    scale=(0.02, 0.02),       # spread in meters
    sh="circle",
    ors=(-30.0, 30.0),        # orientation range (degrees)
).entry("explorer")
```

#### Initial State

**Options**:

- `life_history.age`: Initial age in hours (default: 0.0)
- `life_history.epochs`: Feeding schedule (optional)
- `life_history.reach_pupation`: Whether to grow to pupation (optional)

**Example**:

```python
from larvaworld.lib import reg
from larvaworld.lib.param import Life

larva_groups = reg.gen.LarvaGroup(
    mID="explorer",
    N=10,
    life_history=Life(age=48.0),  # hours
).entry("explorer")
```

For detailed agent options, see {doc}`../agents_environments/larva_agent_architecture`.

---

### 5. Configure Simulation

**Purpose**: Set runtime parameters.

#### Duration

**Parameter**: `duration` (minutes)

```python
from larvaworld.lib.sim import ExpRun

run = ExpRun(experiment="chemotaxis", duration=0.2, screen_kws={})  # 0.2 min (~12s)
```

#### Epochs

**Purpose**: Multi-phase experiments (e.g., training + test).

**Example**:

```python
from larvaworld.lib import reg

# Use a predefined trial template (epochs) from the registry
trials = reg.conf.Trial.getID("odor_preference").get_copy()
exp_params = reg.conf.Exp.getID("chemotaxis").get_copy()
exp_params.trials = trials

run = ExpRun(experiment="chemotaxis", parameters=exp_params, screen_kws={})
```

#### Timestep

**Parameter**: `dt` (seconds, default: 0.1s)

```python
run = ExpRun(experiment="chemotaxis", dt=0.05)  # Finer timestep
```

#### Visualization

**Options**:

- `'video'`: Export MP4/AVI
- `'screen'`: Real-time display (show_display=True)
- `'image'`: Save snapshots
- `None`: No visualization (faster)

**Example**:

```python
screen_kws = {
    "vis_mode": "video",
    "save_video": True,
    "video_file": "chemotaxis",
    "fps": 10,
}

run = ExpRun(experiment="chemotaxis", screen_kws=screen_kws)
```

For keyboard controls, see {doc}`../visualization/keyboard_controls`.

---

### 6. Configure Analysis

**Purpose**: Define what to compute and save.

#### Metrics

**Auto-Selection**: Larvaworld auto-selects metrics based on experiment type.

**Manual Selection** (lightweight example on a small simulated dataset):

```python
from larvaworld.lib.sim import ExpRun

# Small sim to produce a dataset quickly
run = ExpRun(experiment="chemotaxis", duration=0.2, screen_kws={})
run.simulate()
dataset = run.datasets[0]

# Annotation (minimal)
dataset.annotate(
    anot_keys=[
        "bout_detection",    # Detect strides, runs, pauses, turns
    ]
)
```

For details, see {doc}`../data_pipeline/data_processing`.

#### Reference Data

**Purpose**: Compare simulation to experimental data.

**Example**:

```python
from larvaworld.lib.sim import EvalRun

# Compare model against reference
eval_run = EvalRun(
    refID='exploration.30controls',  # Reference dataset
    modelIDs=['explorer', 'navigator'],
    duration=0.2,   # minutes
    N=5,            # agents per model
    screen_kws={},  # headless
)
eval_run.simulate()
```

For details, see {doc}`../working_with_larvaworld/model_evaluation`.

#### Output Options

**Storage Location**:

```python
from larvaworld.lib.sim import ExpRun

run = ExpRun(
    experiment="chemotaxis",
    dir="/path/to/output"  # choose a writable location
)
```

**HDF5 Format**: All datasets are saved as HDF5 files for efficient I/O.

---

### 7. Execute Simulation

**Purpose**: Run the configured experiment.

**Example**:

```python
from larvaworld.lib import reg
from larvaworld.lib.sim import ExpRun

# Load base experiment config and (optionally) override fields (env, agents, screen)
exp_params = reg.conf.Exp.getID("chemotaxis").get_copy()
# exp_params.env_params = env_params
# exp_params.larva_groups = larva_groups

run = ExpRun(experiment="chemotaxis", parameters=exp_params, duration=0.2, screen_kws={})

# Execute
run.simulate()

# Access results
dataset = run.datasets[0]
print(dataset.e.head())  # endpoint data
```

---

## Configuration Registry

Larvaworld uses a **configuration registry** (`/lib/reg/`) to manage templates:

### Registry Structure

```
lib/reg/
├── stored_confs/         # Predefined configurations
│   ├── sim_conf.py       # Experiments, environments
│   ├── data_conf.py      # Reference datasets
│   └── model_conf.py     # Larva models
├── conf.py               # Configuration classes
└── generators/           # Generators (EnvConf, LabFormat)
```

### Accessing Configurations

```python
from larvaworld.lib import reg

# Experiments
exp_conf = reg.conf.Exp.getID("chemotaxis")

# Environments
env_conf = reg.conf.Env.getID("arena_200mm")

# Models
model_conf = reg.conf.Model.getID("explorer")

# Reference datasets
ref_dataset = reg.loadRef(id="exploration.30controls", load=True)
```

---

## Complete Example

```python
from larvaworld.lib import reg
from larvaworld.lib.sim import ExpRun

# 1) Start from an existing experiment template
exp_params = reg.conf.Exp.getID("chemotaxis").get_copy()

# 2) Customize environment (start from a predefined arena template)
env_params = reg.conf.Env.getID("arena_200mm").get_copy()
if env_params.odorscape is None:
    from larvaworld.lib import util

    env_params.odorscape = util.AttrDict()
env_params.odorscape.update({"odorscape": "Gaussian", "grid_dims": (51, 51)})
if env_params.food_params is None:
    from larvaworld.lib import util

    env_params.food_params = util.AttrDict()
if not getattr(env_params.food_params, "source_units", None):
    env_params.food_params.source_units = {}
env_params.food_params.source_units["banana_patch"] = {
    "pos": (0.02, 0.0),
    "radius": 0.005,  # 5 mm
    "amount": 3.0,
    "odor": {"id": "banana", "intensity": 2.0, "spread": 0.02},
    "color": "yellow",
    "regeneration": False,
}
exp_params.env_params = env_params

# 3) Customize agents (larva groups keyed by group_id)
exp_params.larva_groups = reg.gen.LarvaGroup(mID="navigator", N=10).entry("navigator")

# 4) Configure simulation + execute (headless quick run)
run = ExpRun(experiment="chemotaxis", parameters=exp_params, duration=0.2, screen_kws={})
run.simulate()

# 6. Analyze
dataset = run.datasets[0]
dataset.preprocess(filter_f=3.0)
dataset.process(proc_keys=["angular", "spatial"])

# See :doc:`../visualization/plotting_api` for plotting examples.
```

---

## Related Documentation

- {doc}`experiment_types` - All 57 preconfigured experiments
- {doc}`../agents_environments/arenas_and_substrates` - Environment configuration
- {doc}`../agents_environments/larva_agent_architecture` - Agent models
- {doc}`../working_with_larvaworld/single_experiments` - Running experiments
- {doc}`../data_pipeline/data_processing` - Data processing pipeline
