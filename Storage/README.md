# Storage Module

The Storage module is responsible for persisting generated data to a destination.
It also owns format serialization so that engines can stay storage-agnostic.

---

## Backends

- Local filesystem: `Storage.local.LocalStorage`
- Docker container: `Storage.docker.DockerStorage`

---

## Module Structure

```text
Storage/
+-- __init__.py
+-- base/
¦   +-- __init__.py
¦   +-- base.py
+-- local/
¦   +-- __init__.py
¦   +-- local_storage.py
+-- docker/
¦   +-- __init__.py
¦   +-- docker_storage.py
+-- base.py          # shim for backward compatibility
+-- local.py         # shim for backward compatibility
```

---

## Output Layout

Files are written under per-format directories and grouped by resource type:

```
output/
  json/patient/patient-<timestamp>.json
  ndjson/patient/patient-<timestamp>.ndjson
  csv/patient/patient-<timestamp>.csv
  xml/patient/patient-<timestamp>.xml
  turtle/patient/patient-<timestamp>.ttl
  logs/<timestamp>/engine.log
  summary/<timestamp>/run_summary_<timestamp>_<run_id>.json
```

---

## Docker Storage

`DockerStorage` writes files into a running container using the docker CLI.

Required arguments:
- `container_name`: name or ID of the running container
- `container_base_dir`: base directory inside the container (default: `/output`)

By default it validates the container exists and is running. You can disable
that check with `validate_container=False` or `--docker-skip-validate`.

When using Docker storage for exports only, you can avoid creating metadata,
summary, and log folders inside the container by setting:
- `create_metadata_dir=False`
- `create_summary_dir=False`
- `create_log_dir=False`

Example usage:

```python
from Storage import DockerStorage

storage = DockerStorage(
    container_name="fhirlake",
    container_base_dir="/data/fhirlake",
    create_metadata_dir=False,
    create_summary_dir=False,
    create_log_dir=False,
)
```

---

## Notes

- The `base.py` and `local.py` files at the Storage root are shims to preserve
  existing imports.
- The engine selects formats; storage writes and serializes the output.
