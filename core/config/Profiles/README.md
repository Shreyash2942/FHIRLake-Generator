# 📦 Profiles

## Purpose
Profiles are named configuration presets that define:
- dataset size
- distributions (future)
- enabled output formats
- performance tuning (future)

Profiles allow a user to run:
- a small quick demo
- a medium integration test
- a large stress test

---

## Examples
- `small_demo.yaml` → runs fast on any laptop
- `large_run.yaml` → validates scalability + performance

---

## Naming Convention
Use clear names:
- `small_demo`
- `medium_test`
- `large_run`
- `spark_ready` (future)

---

## Best Practice
Profiles should contain only overrides (do not duplicate defaults).
