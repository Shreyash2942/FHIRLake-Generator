# CLI Config

This folder contains CLI configuration files.

## Default Config
- `cli.config.json` controls which resources appear in the interactive CLI and the default counts.

Example:
```json
{
  "allowed_resources": ["Patient", "Practitioner", "Encounter", "Location"],
  "default_count": 10
}
```

## Adding a New Module (CLI Command)

1. Create a new file in `cli/commands/` (one file per command).
2. Parse arguments in that file (or reuse helpers in `cli/parsing/`).
3. Call core/engine from `cli/services/` or directly.
4. Add any user-facing output helpers in `cli/output/`.
5. Update `cli/README.md` if the command should be documented.

Keep command modules small and avoid business logic.
