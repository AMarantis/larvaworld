# Experiment Types

Larvaworld provides **57 preconfigured behavioral experiments** spanning multiple categories, from basic exploration to complex learning tasks and competitive games. This page groups them by behavioral question rather than by internal configuration keys.

---

## Conceptual Overview

The diagram below summarizes the main experiment categories, emphasizing how Larvaworld covers exploration, sensory navigation, learning, foraging, growth, competition and multi-sensory paradigms.

```{mermaid}
mindmap
    root((Larvaworld<br/>Experiments))
        Exploratory
            Dish exploration
            Dispersion analysis
            Free movement
            Tethered tracking
        Chemotaxis
            Odor gradients
            Source navigation
            Orbiting behavior
            Reorientation
        Chemanemotaxis
            Odor puffs
            Wind + odor integration
        Learning
            Odor conditioning
            Preference training
            Memory retention
            Choice tests
        Feeding
            Single patch
            Food grids
            Consumption rates
            Quality effects
        Foraging
            Rover vs Sitter
            Patch exploitation
            Search strategies
            Multi-patch
        Growth
            DEB simulation
            Life-history
            Development tracking
            Starvation effects
        Odor preference
            Train
            Test (on/off food)
            OSN / RL variants
        Competition
            Capture the flag
            Keep the flag
            Chase games
            Maze navigation
        Anemotaxis
            Wind navigation
            Puff responses
            Border effects
        Thermotaxis
            Temperature gradients
            Thermal preference
        Tactile
            Touch detection
            Multi-patch sensing
        Other
            Realistic body
            Prey detection
        Games
            Maze
            Capture/Keep the flag
            Catch me
```

---

## Summary Table

The following table groups experiments by **behavioral category** (conceptual view):

| Type/Behavior       | Experiment (ID)     | Description                             | Literature Source                                                       |
| ------------------- | ------------------- | --------------------------------------- | ----------------------------------------------------------------------- |
| **exploration**     | focus               | Single larva in tiny arena (close-view) | -                                                                       |
|                     | dish                | Petri-dish exploration                  | -                                                                       |
|                     | dispersion          | Dispersion from center                  | -                                                                       |
| **chemotaxis**      | chemotaxis          | Navigation up odor gradient             | [Gomez-Marin et al. (2012)](https://doi.org/10.1016/j.conb.2011.11.008) |
|                     | chemorbit           | Odor-source orbital search              | [Gomez-Marin et al. (2012)](https://doi.org/10.1016/j.conb.2011.11.008) |
| **chemanemotaxis**  | single_puff         | Odor puff + wind integration            | -                                                                       |
| **odor preference** | PItrain             | Olfactory associative learning (train)  | The Maggot Learning Manual                                              |
|                     | PItest_off          | Olfactory associative learning (test)   | The Maggot Learning Manual                                              |
| **foraging**        | patchy_food         | Food search in single patch             | -                                                                       |
|                     | patch_grid          | Food search in grid of patches          | -                                                                       |
| **tactile**         | tactile_detection   | Obstacle/tactile sensing                | -                                                                       |
| **growth**          | RvsS                | Rovers vs sitters; phenotypes           | [Kaun et al. (2007)](https://doi.org/10.1242/jeb.006924)                |
|                     | growth              | Long-term rearing                       | [Kaun et al. (2007)](https://doi.org/10.1242/jeb.006924)                |
| **games**           | maze                | Maze navigation                         | -                                                                       |
|                     | capture_the_flag    | Team competition                        | -                                                                       |
| **other**           | realistic_imitation | Multisegment larvae in Box2D            | -                                                                       |

---

## Category Details

### 1. Exploration

**Purpose**: Study baseline locomotory behavior without specific targets.

**Experiments**:

- `tethered`: Larva constrained to small area (high-resolution tracking)
- `focus`: Single larva in tiny arena (close-view)
- `dish`: Standard Petri dish exploration
- `dispersion`: Larvae disperse from central starting point
- `dispersion_x2`: Dispersion with two groups

**Use Cases**:

- Baseline movement statistics
- Spatial exploration patterns
- Activity level assessment
- Kinematic analysis

**Example**:

```bash
larvaworld Exp dish -N 10 -duration 5.0
```

---

### 2. Chemotaxis

**Purpose**: Navigation along odor gradients.

**Key Experiments**:

- `chemotaxis`: Standard navigation up gradient
- `chemorbit`: Odor source navigation with orbital search
- `chemorbit_OSN`: Chemotaxis with olfactory sensory neurons (OSN) model
- `chemorbit_x2` / `chemorbit_x4`: Competing chemotaxis models
- `chemotaxis_diffusion`: Gaussian plume diffusion
- `chemotaxis_RL`: Reinforcement learning-based navigation
- `reorientation`: Study reorientation maneuvers
- `food_at_bottom`: Navigate to food source at arena bottom

**Literature**:

- Gomez-Marin et al. (2012): Active sensation during orientation

**Example**:

```bash
larvaworld Exp chemotaxis -N 20 -duration 10.0
```

---

### 3. Anemotaxis

**Purpose**: Navigation using wind/airflow cues.

**Experiments**:

- `anemotaxis`: Standard wind-guided navigation
- `anemotaxis_bordered`: Anemotaxis in bounded arena
- `puff_anemotaxis_bordered`: Pulsed wind stimuli

**Use Cases**:

- Wind-guided navigation
- Multi-modal integration (odor + wind)

---

### 4. Chemanemotaxis

**Purpose**: Combined odor and wind navigation.

**Experiments**:

- `single_puff`: Single odor puff release

**Use Cases**:

- Realistic odor plume tracking
- Multi-sensory integration

---

### 5. Thermotaxis

**Purpose**: Temperature-guided navigation.

**Experiments**:

- `thermotaxis`: Navigate along thermal gradient

**Use Cases**:

- Temperature preference
- Thermal gradient navigation

---

### 6. Odor Preference

**Purpose**: Olfactory associative learning.

**Key Experiments**:

- `PItrain`: Train phase (odor + food pairing)
- `PItest_off`: Test phase without food
- `PItest_on`: Test phase with food
- `PItrain_mini`: Shortened training
- `PItest_off_OSN`: Test with OSN model
- `PItest_off_RL`: Test with RL-based learning

**Literature**:

- The Maggot Learning Manual

**Metrics**:

- **Preference Index (PI)**: Quantifies odor preference

**Example**:

```bash
# Training phase
larvaworld Exp PItrain -N 30 -duration 10.0

# Test phase
larvaworld Exp PItest_off -N 30 -duration 5.0
```

---

### 7. Foraging

**Purpose**: Food search and consumption.

**Key Experiments**:

- `patchy_food`: Single food patch
- `patch_grid`: Grid of food patches
- `MB_patch_grid` / `noMB_patch_grid`: Mushroom body variants
- `random_food`: Randomly placed food
- `uniform_food`: Uniformly distributed food
- `food_grid`: Structured food grid
- `single_odor_patch` / `single_odor_patch_x4`: Food + odor patch (multi-model)
- `double_patch`: Two competing patches
- `4corners`: Four patches in corners

**Literature**:

- Kaun et al. (2007): Rovers vs. sitters phenotypes

**Metrics**:

- Food intake
- Patch residence time
- Search efficiency

**Example**:

```bash
larvaworld Exp patchy_food -N 20 -duration 15.0
```

---

### 8. Tactile

**Purpose**: Mechanical sensation and obstacle navigation.

**Experiments**:

- `tactile_detection`: Single obstacle detection
- `tactile_detection_x4`: Four obstacles
- `multi_tactile_detection`: Multiple obstacles

**Use Cases**:

- Collision avoidance
- Tactile-guided navigation
- Mechanical sensing

---

### 9. Growth

**Purpose**: Long-term development and energetics.

**Key Experiments**:

- `growth`: Standard rearing
- `RvsS`: Rovers vs. sitters comparison
- `RvsS_on`: RvsS on food
- `RvsS_off`: RvsS off food
- `RvsS_on_q*`: RvsS with varying food quality (q75, q50, q25, q15)
- `RvsS_on_*h_prestarved`: RvsS with pre-starvation (1h, 2h, 3h, 4h)

**Literature**:

- Kaun et al. (2007): Foraging phenotypes

**Metrics**:

- Body mass growth (DEB)
- Feeding rate
- Activity patterns

**Example**:

```bash
larvaworld Exp growth -N 10 -duration 60.0  # 1 hour simulated time
```

---

### 10. Games

**Purpose**: Multi-agent competitive scenarios.

**Experiments**:

- `maze`: Navigate maze to find odor source
- `keep_the_flag`: One team keeps food, others try to steal
- `capture_the_flag`: Retrieve food and return to base
- `catch_me`: One larva escapes, others chase

**Use Cases**:

- Multi-agent dynamics
- Competitive behaviors
- Team strategies

**Example**:

```bash
larvaworld Exp maze -N 5 -duration 10.0
```

---

### 11. Other

**Purpose**: Specialized experiments.

**Experiments**:

- `realistic_imitation`: Multisegment body with Box2D physics
- `prey_detection`: Predator-prey interactions

---

## Accessing Experiments

### Via CLI

```bash
# List all available experiments (via help)
larvaworld Exp --help

# Run a specific experiment
larvaworld Exp chemotaxis -N 20 -duration 5.0
```

### Via Python

```python
from larvaworld.lib import reg
from larvaworld.lib.sim import ExpRun

# Load experiment configuration
exp_conf = reg.conf.Exp.getID("chemotaxis").get_copy()

# Run experiment
run = ExpRun(experiment="chemotaxis", parameters=exp_conf, duration=5.0)
run.simulate()
```

### Inspect Configuration

```python
from larvaworld.lib import reg

# Get all experiment IDs
exp_ids = reg.conf.Exp.confIDs
print(f"Available experiments: {len(exp_ids)}")
print(exp_ids)

# Inspect a specific experiment
exp_conf = reg.conf.Exp.getID("chemotaxis")
print(exp_conf)
```

---

## Creating Custom Experiments

You can define new experiments by:

1. **Modifying `sim_conf.py`**: Add entries to `Exp_dict()`
2. **Using Python API**: Start from a template (`exp_params = reg.conf.Exp.getID(...).get_copy()`), override `exp_params.env_params` / `exp_params.larva_groups`, and pass it via `parameters=exp_params`

**Example: Custom Experiment**

```python
from larvaworld.lib import reg
from larvaworld.lib.sim import ExpRun

# Start from an existing experiment template
exp_params = reg.conf.Exp.getID("dish").get_copy()
lg = reg.gen.LarvaGroup

# Override environment (use a 200mm arena template and add food patches)
env_params = reg.conf.Env.getID("arena_200mm").get_copy()
env_params.food_params.source_groups = {
    "patches": {"group": "patches", "amount": 3}
}
exp_params.env_params = env_params

# Override larva groups
exp_params.larva_groups = {}
exp_params.larva_groups.update(lg(mID="explorer", N=10, c="blue").entry("explorer"))
exp_params.larva_groups.update(lg(mID="navigator", N=10, c="red").entry("navigator"))

# Run custom experiment
run = ExpRun(
    experiment="dish",  # base template id
    parameters=exp_params,
    duration=5.0,
)
run.simulate()
```

---

## Related Documentation

- {doc}`simulation_modes` - Experiment execution modes
- {doc}`experiment_configuration_pipeline` - Configuration system
- {doc}`../working_with_larvaworld/single_experiments` - Running experiments
- {doc}`../agents_environments/arenas_and_substrates` - Environment configuration
