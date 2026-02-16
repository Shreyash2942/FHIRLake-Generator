# Command Line Interface (CLI)

## Overview
The CLI module is the user-facing entry point for the FHIRLake Generator platform.
It translates command-line arguments into a structured request and delegates generation to Core.
The CLI stays thin and declarative.

## Responsibilities
- Parse command-line arguments
- Prompt for interactive inputs
- Build a UserRequest for the Core engine
- Trigger dataset generation and export
- Report run results

## Module Structure

```text
cli/
  config/
    cli.config.json      # CLI resource allowlist + defaults
    README.md            # Config guidance
  commands/
    cli_main.py          # Argument parsing and entrypoint logic
    interactive.py       # Interactive flow and engine invocation
    fhirlake.py          # Backward-compatible entrypoint
  parsing/
    config.py            # CLI config loader
    formats.py           # Export format parsing
  services/
    deps.py              # Dependency expansion helpers
  output/
    prompts.py           # User input helpers
  README.md
```

## Execution Flow

```text
User Command
  -> CLI Argument Parsing
  -> Interactive Prompts
  -> Dependency Expansion
  -> Engine Invocation
  -> Export + Storage
```

## Usage (Interactive)

Run the CLI and answer the prompts:

```bash
python cli/fhirlake.py
```

Optional flags:

```bash
python cli/fhirlake.py --datasets-root ./Datasets --output ./outputs
```

Optional CLI config:

```bash
python cli/fhirlake.py --cli-config ./cli/config/cli.config.json
```

## CLI Config

`cli/cli.config.json` controls which resources are shown in the CLI and the default count.

Example:

```json
{
  "allowed_resources": ["Patient", "Practitioner", "Encounter", "Location"],
  "default_count": 10
}
```

## Design Principles
- No business logic
- No resource-specific rules
- No file-format handling beyond validation
- Delegates generation and orchestration to Core

## Notes
- CLI is optional for library usage
- Core engine can be invoked programmatically
- CLI exists for ease of use and demos
