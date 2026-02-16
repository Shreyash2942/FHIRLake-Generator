# ⚙️ Core Config

## Purpose
The `config/` folder defines how a generation run behaves.  
It contains:
- **defaults.yaml** (global defaults used for every run)
- **profiles/** (named presets like `small_demo`, `large_run`)

Core loads defaults first, then overlays a selected profile, then overlays CLI/UI overrides.

---

## Files

### `defaults.yaml`
Global default settings:
- dataset size (patients, encounters per patient, etc.)
- output formats
- run settings (seed, output path)

### `profiles/`
Named config presets:
- `small_demo.yaml` → quick local testing
- `large_run.yaml` → stress/performance testing
- more profiles can be added anytime without changing Core logic

---

## How to Add a New Profile
1. Create a new YAML file: `profiles/my_profile.yaml`
2. Add dataset/export/run overrides
3. UI/CLI should list it automatically (future enhancement)

---

## Design Rules
- Profiles should be small (only overrides, not full copies)
- Keep values deterministic when possible (use `seed` support)
