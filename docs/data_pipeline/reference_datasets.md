# Reference Datasets

Reference datasets are experimental recordings imported into Larvaworld and registered in the configuration system for easy access.

---

## Purpose

Reference datasets enable:

- ✅ **Model validation**: Compare simulations to real data
- ✅ **Replay visualization**: View experimental trajectories
- ✅ **Genetic algorithm optimization**: Fitness evaluation against real behavior
- ✅ **Baseline comparisons**: Control experiments

---

## Registry System

### List Available References

```python
from larvaworld.lib import reg

# List all reference datasets
ref_ids = reg.conf.Ref.confIDs
print(f"Available: {len(ref_ids)} reference datasets")

for ref_id in ref_ids:
    print(f"  - {ref_id}")
```

### Load Reference Dataset

```python
from larvaworld.lib import reg

dataset = reg.loadRef(id="exploration.30controls", load=True)

print(f"Ref ID: {dataset.config.refID}")
print(f"Agents: {len(dataset.agent_ids)}")
print(f"Duration: {dataset.config.duration} min")
```

---

## Using Reference Datasets

### Model Evaluation

```python
from larvaworld.lib.sim import EvalRun

eval_run = EvalRun(
    refID='exploration.30controls',
    modelIDs=['explorer', 'navigator'],
    duration=0.5,  # minutes (use larger values for full evaluations)
    N=5,           # agents per model
    screen_kws={}, # headless
)
eval_run.simulate()
```

See {doc}`../working_with_larvaworld/model_evaluation` for details.

---

### Replay Visualization

```python
from larvaworld.lib import reg
from larvaworld.lib.sim import ReplayRun

# Build replay parameters (select a short slice for a quick run)
replay_params = reg.gen.Replay(
    refID="exploration.30controls",
    time_range=(0, 10),  # seconds
    agent_ids=[0, 1, 2],
).nestedConf

replay = ReplayRun(parameters=replay_params, screen_kws={"show_display": False})
replay.run()  # Reconstructs and visualizes stored trajectories (no simulation)
```

See {doc}`../working_with_larvaworld/replay` for details.

---

### Genetic Algorithm Optimization

```python
from larvaworld.lib.sim.genetic_algorithm import GAevaluation, optimize_mID

evaluator = GAevaluation(
    refID="exploration.30controls",
    # Keep evaluation metrics aligned with what GAlauncher enriches by default.
    cycle_curve_metrics=[],
    eval_metrics={
        "angular kinematics": ["b", "fov"],
        "spatial displacement": ["v", "a"],
    },
)

results = optimize_mID(
    mID0="explorer",
    mID1="explorer_opt",          # ID for optimized model config
    ks=["crawler", "turner"],  # Module names to optimize
    evaluator=evaluator,
    Ngenerations=1,                # Increase for real runs
    Nagents=10,                    # GA population size
    duration=0.05,                 # minutes per agent (increase for real runs)
    screen_kws={"show_display": False, "vis_mode": None},
    store_data=False,
)

best_conf = results["explorer_opt"]  # Optimized model configuration (AttrDict)
```

See {doc}`../working_with_larvaworld/ga_optimization_advanced` for details.

---

## Creating Reference Datasets

### 1. Import Experimental Data

```python
from larvaworld.lib import reg

lab = reg.gen.LabFormat(**reg.conf.LabFormat.getID("Schleyer"))
lab.import_dataset(
    parent_dir="exploration",
    merged=True,
    max_Nagents=30,
    min_duration_in_sec=60,
    id="my_experiment",
    refID="my_experiment",
    save_dataset=True,
)
```

### 2. Process Dataset

```python
dataset = reg.loadRef(id="my_experiment", load=True)

dataset.preprocess(filter_f=3.0)
dataset.process(proc_keys=["angular", "spatial"])
dataset.annotate(
    anot_keys=["bout_detection", "bout_distribution", "interference"]
)
```

### 3. Save as Reference

```python
# Dataset is automatically registered as a reference
# when imported via LabFormat
```

---

## Reference Dataset Structure

Reference datasets have the same structure as simulation datasets:

```python
dataset = reg.loadRef(id="exploration.30controls", load=True)

# Endpoint data (summary per larva)
print(dataset.e)

# Step-wise data (time-series)
print(dataset.s)

# Configuration
print(dataset.c)

# Agent IDs
print(dataset.agent_ids)
```

---

## Related Documentation

- {doc}`lab_formats_import` - Importing experimental data
- {doc}`data_processing` - Processing pipeline
- {doc}`../working_with_larvaworld/model_evaluation` - Model evaluation
- {doc}`../working_with_larvaworld/replay` - Replay visualization
