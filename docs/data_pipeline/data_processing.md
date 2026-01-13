# Data Processing

Larvaworld provides a comprehensive data processing pipeline for trajectory analysis. All processing operates on `LarvaDataset` objects.

---

## Processing Pipeline

```
Raw Data → Preprocess → Process → Annotate → Plot/Analyze
```

---

## 1. Preprocessing

**Purpose**: Clean and standardize raw trajectories

```python
dataset.preprocess(
    # Note: drop_collisions requires a "collision_flag" column (typically present in imported datasets)
    drop_collisions=False,
    interpolate_nans=True,     # Fill missing data
    filter_f=3.0,              # Low-pass filter at 3 Hz
    rescale_by=0.001,          # Scale (e.g., mm to m)
    transposition="center"     # Center trajectories
)
```

### Available Options

| Parameter          | Description                                        | Default |
| ------------------ | -------------------------------------------------- | ------- |
| `drop_collisions`  | Remove frames with collisions                      | `False` |
| `interpolate_nans` | Interpolate missing values                         | `False` |
| `filter_f`         | Low-pass filter cutoff (Hz)                        | `None`  |
| `rescale_by`       | Scale factor                                       | `None`  |
| `transposition`    | Alignment mode (`"center"`, `"origin"`, `"arena"`) | `None`  |

---

## 2. Processing

**Purpose**: Compute behavioral metrics

```python
dataset.process(
    proc_keys=["angular", "spatial"],
    dsp_starts=[0],
    dsp_stops=[40, 60],
    tor_durs=[5, 10, 20]
)
```

### Processing Categories

#### Angular Metrics

```python
proc_keys = ["angular"]
```

**Computes**:

- Orientation angle
- Angular velocity
- Angular acceleration
- Head direction

#### Spatial Metrics

```python
proc_keys = ["spatial"]
```

**Computes**:

- Linear velocity
- Linear acceleration
- Cumulative distance

#### Forward Components

Forward/sideways components are part of the spatial metrics computed when
`"spatial"` is included in `proc_keys`. They are not a separate `proc_keys`
entry.

#### Dispersal

Dispersal metrics are always computed for the combinations of
`dsp_starts` and `dsp_stops` passed to `process`:

```python
dataset.process(
    proc_keys=["angular", "spatial"],
    dsp_starts=[0],       # Start times (s)
    dsp_stops=[40, 60],   # Stop times (s)
)
```

This adds endpoint columns such as `dispersion_0_60_mean` / `std` / `max` and
their scaled counterparts (e.g. `scaled_dispersion_0_60_mean`).

#### Tortuosity

Tortuosity metrics are controlled by `tor_durs`:

```python
dataset.process(
    proc_keys=["angular", "spatial"],
    tor_durs=[5, 10, 20],  # Window durations (s)
)
```

This adds endpoint columns such as `tortuosity_5_mean` / `std`,
`tortuosity_10_mean` / `std`, etc.

---

## 3. Annotation

**Purpose**: Detect behavioral events

```python
dataset.annotate(
    anot_keys=[
        "bout_detection",
        "bout_distribution",
        "interference"
    ]
)
```

### Annotation Types

#### Bout Detection

```python
anot_keys = ["bout_detection"]
```

**Detects**:

- **Strides**: Individual peristaltic waves
- **Runs**: Chains of strides
- **Pauses**: Immobility epochs
- **Turns**: Reorientation maneuvers

#### Bout Distribution

```python
anot_keys = ["bout_distribution"]
```

**Computes**:

- Distribution fitting (exponential, power-law)
- Duration/length statistics

#### Interference

```python
anot_keys = ["interference"]
```

**Analyzes**:

- Crawl-turn coupling
- Phase relationships

---

## Data Structure

### LarvaDataset

```python
dataset = run.datasets[0]

# Endpoint data (summary per larva)
print(dataset.e)         # Pandas DataFrame

# Step-wise data (time-series)
print(dataset.s)         # Pandas DataFrame

# Configuration
print(dataset.c)         # AttrDict
```

### Endpoint Metrics

```python
dataset.e.columns
```

**Available**:

- `cum_dur`: Total duration (s)
- `velocity_mean`, `scaled_velocity_mean`: Mean speed (and scaled variant)
- `dispersion_0_60_mean`: Example dispersal metric (if computed)
- `tortuosity_5_mean`: Example tortuosity metric (if computed)

### Step-wise Data

```python
dataset.s.columns
```

**Available**:

- `x`, `y`: Position
- `bend`, `front_orientation`, `rear_orientation`: Angular kinematics
- `velocity`, `scaled_velocity`: Speed (and scaled variant)

---

## Example Workflow

```python
from larvaworld.lib.sim import ExpRun

# Run experiment
run = ExpRun(experiment="dish", N=3, duration=1.0, screen_kws={}, store_data=False)
run.simulate()

# Get dataset
dataset = run.datasets[0]

# 1. Preprocess
dataset.preprocess(
    interpolate_nans=True,
    filter_f=3.0,
    transposition="center"
)

# 2. Process
dataset.process(
    proc_keys=["angular", "spatial"],
    dsp_starts=[0],
    dsp_stops=[40, 60],
    tor_durs=[5, 10],
)

# 3. Annotate
dataset.annotate(
    anot_keys=["bout_detection", "bout_distribution"]
)

# 4. Analyze
print("=== Summary Statistics ===")
cols = [c for c in ["cum_dur", "velocity_mean", "dispersion_0_60_mean", "tortuosity_5_mean"] if c in dataset.e.columns]
print(dataset.e[cols].describe() if cols else dataset.e.describe())
```

---

## Saving Processed Data

```python
from larvaworld.lib import reg

# Save dataset to HDF5 and register as a reference ID
dataset.save(refID="my_experiment")

# Load later
dataset = reg.loadRef(id="my_experiment", load=True)
```

---

## Related Documentation

- {doc}`lab_formats_import` - Importing experimental data
- {doc}`reference_datasets` - Reference dataset management
- {doc}`../working_with_larvaworld/model_evaluation` - Using processed data for evaluation
- {doc}`../visualization/plotting_api` - Plotting processed data
