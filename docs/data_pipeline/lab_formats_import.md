# Lab-Specific Data Import

Larvaworld can import experimental datasets from diverse tracking systems. Each lab uses different hardware/software, resulting in different data formats.

---

## Supported Labs

| Lab          | Framerate (Hz) | Midline (#) | Contour (#) | Source                   |
| ------------ | -------------- | ----------- | ----------- | ------------------------ |
| **Schleyer** | 16             | 12          | 22          | Paisios et al. (2017)    |
| **Jovanic**  | 14.29\*        | 11          | 0           | de Tredern et al. (2024) |
| **Berni**    | 2              | 1           | 0           | Sims et al. (2019)       |
| **Arguello** | 10             | 5           | 0           | Kafle et al. (2025)      |

\*Nominal timestep is 0.07s; variable framerate supported via interpolation.

---

## Import Workflow

### 1. Create LabFormat

```python
from larvaworld.lib import reg

# Use the preconfigured lab format from the registry
lab = reg.gen.LabFormat(**reg.conf.LabFormat.getID("Schleyer"))
print("raw:", lab.raw_folder)
print("processed:", lab.processed_folder)
```

### 2. Import Single Dataset

```python
from pathlib import Path

raw_folder = Path("/path/to/raw")  # optional override (defaults to lab.raw_folder)
parent_dir = "exploration/dish"    # path relative to raw_folder

source_dir = raw_folder / parent_dir
if not source_dir.exists():
    print(f"Missing raw data folder: {source_dir} (skipping import)")
else:
    dataset = lab.import_dataset(
        parent_dir=parent_dir,
        raw_folder=str(raw_folder),
        merged=True,                     # Schleyer: merge multiple subfolders (e.g. boxes)
        max_Nagents=30,                  # Optional: limit number of larvae
        min_duration_in_sec=60,          # Optional: minimum track duration
        id="exploration.30controls",     # Dataset ID on disk
        refID="exploration.30controls",  # Reference ID in the registry
        save_dataset=True,               # Store processed dataset
    )
```

### 3. Import Multiple Datasets

```python
from pathlib import Path
from larvaworld.lib import reg

lab = reg.gen.LabFormat(**reg.conf.LabFormat.getID("Schleyer"))
raw_folder = Path("/path/to/raw")

datasets = lab.import_datasets(
    source_ids=["dish01", "dish02"],
    ids=["exploration.dish01", "exploration.dish02"],
    refIDs=["exploration.dish01", "exploration.dish02"],
    parent_dir="exploration",        # Common parent folder under raw/
    raw_folder=str(raw_folder),
    merged=True,
    save_dataset=True,
)
```

### 4. Load Imported Dataset

```python
from larvaworld.lib import reg

dataset = reg.loadRef(id="exploration.30controls", load=True)
print(dataset.e)  # Endpoint data
print(dataset.s.head())  # Step-wise data
```

---

## Lab-Specific Details

### Schleyer Lab

**Tracker**: Custom MATLAB tracker

**Data Structure**:

- 12-point midline
- 22-point contour
- 16 Hz framerate

**Example**:

```python
from larvaworld.lib import reg

lab = reg.gen.LabFormat(**reg.conf.LabFormat.getID("Schleyer"))
lab.import_dataset(
    parent_dir="chemotaxis/exp1",
    raw_folder="/data/schleyer/raw",
    id="schleyer_chemotaxis",
    refID="schleyer.chemotaxis",
    save_dataset=True,
)
```

---

### Jovanic Lab

**Tracker**: Custom Python tracker

**Data Structure**:

- 11-point midline
- Convex hull (variable points)
- ~11.27 Hz (variable framerate)

**Example**:

```python
from larvaworld.lib import reg

lab = reg.gen.LabFormat(**reg.conf.LabFormat.getID("Jovanic"))
lab.import_datasets(
    source_ids=["Fed", "Sucrose", "Starved"],  # Folder names under parent_dir
    ids=["Jovanic_Fed", "Jovanic_Sucrose", "Jovanic_Starved"],
    refIDs=["Jovanic.Fed", "Jovanic.Sucrose", "Jovanic.Starved"],
    parent_dir="AttP2",
    raw_folder="/data/jovanic/raw",
    save_dataset=True,
)
```

---

### Berni Lab

**Tracker**: FIM (Frustrated Total Internal Reflection Microscopy)

**Data Structure**:

- Centroid only (no midline)
- 2 Hz framerate

**Example**:

```python
from larvaworld.lib import reg

lab = reg.gen.LabFormat(**reg.conf.LabFormat.getID("Berni"))

# Note: the Berni importer currently expects an explicit list of raw files.
# LabFormat.import_dataset is not yet wired for this lab format.
# (See: larvaworld.lib.process.importing.import_Berni)
```

---

### Arguello Lab

**Tracker**: Custom tracker

**Data Structure**:

- 5-point midline
- 10 Hz framerate

**Example**:

```python
from larvaworld.lib import reg

lab = reg.gen.LabFormat(**reg.conf.LabFormat.getID("Arguello"))

# Note: the Arguello importer currently expects an explicit list of raw files.
# LabFormat.import_dataset is not yet wired for this lab format.
# (See: larvaworld.lib.process.importing.import_Arguello)
```

---

## Data Processing After Import

```python
from larvaworld.lib import reg

# Load dataset
dataset = reg.loadRef(id="exploration.30controls", load=True)

# Preprocess
dataset.preprocess(
    drop_collisions=True,
    interpolate_nans=True,
    filter_f=3.0,
)

# Process metrics
dataset.process(
    proc_keys=["angular", "spatial"],
    dsp_starts=[0],
    dsp_stops=[40, 60],
    tor_durs=[5, 10, 20],
)

# Annotate bouts
dataset.annotate(
    anot_keys=[
        "bout_detection",
        "bout_distribution",
        "interference",
    ]
)
```

See {doc}`data_processing` for details.

---

## Custom Lab Format

To add a new lab format, you typically need:

1. A parser/import function in `larvaworld.lib.process.importing` (and register it in `lab_specific_import_functions`).
2. A `LabFormat` entry in the registry (see `larvaworld.lib.reg.stored_confs.data_conf.LabFormat_dict`) defining:
   - `tracker` (`TrackerOps`)
   - `filesystem` (`Filesystem`)
   - `env_params` (`EnvConf`)
   - `preprocess` (`PreprocessConf`)

```python
from larvaworld.lib.process.importing import lab_specific_import_functions

def import_MyLab(source_dir, tracker, filesystem, **kwargs):
    # Custom raw data parsing logic
    # Return (step_df, end_df)
    ...

lab_specific_import_functions["MyLab"] = import_MyLab
```

---

## Related Documentation

- {doc}`data_processing` - Data processing pipeline
- {doc}`reference_datasets` - Reference dataset management
- {doc}`../working_with_larvaworld/model_evaluation` - Using imported data for evaluation
