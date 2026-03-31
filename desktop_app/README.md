# Desktop App

This package contains the PySide6 desktop application layer for FHIRLake Generator.

Scope:
- desktop UI only
- profile management
- UI-to-engine integration

Non-goals:
- no generator logic lives here
- no replacement of existing `core`, `Storage`, or `Exporter` modules

Entry points:
- `app.py`: application bootstrap
- `main_window.py`: top-level desktop shell

