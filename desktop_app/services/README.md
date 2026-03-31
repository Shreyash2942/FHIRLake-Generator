# Services

This package coordinates UI actions with the existing project engine.

Rules:
- services may call existing `core`, `Storage`, and `Exporter` code
- services must not duplicate generation logic
- services should stay thin and adapter-oriented

