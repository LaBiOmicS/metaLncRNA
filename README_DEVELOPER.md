# Developer Guide: metaLncRNA

## Architectural Overview
metaLncRNA uses the **Adapter Design Pattern**. To add a new tool:
1. Create a new adapter in `src/metalncrna/adapters/` inheriting from `BaseAdapter`.
2. Implement `run()` (execution logic) and `parse_results()` (output standardization).
3. Register the tool in `Dispatcher._init_adapters()`.

## Environment Isolation
metaLncRNA automates environment creation via `mamba`. 
- **Core Env (`metalnc_core`):** Orchestrator, CLI, Plotly, Pandas.
- **Tool Envs:** Environment-per-tool (e.g., `metalnc_rnasamba`, `metalnc_cpc2`).

## Configuration Management
The system uses a hierarchical configuration loader implemented in `cli.py`:
1.  **Package Defaults:** `src/metalncrna/data/default_config.yaml` (Always loaded first).
2.  **Working Directory:** `./metaLncRNA_config.yaml` (Overrides defaults).
3.  **Home Directory:** `~/.metalncrna/config.yaml` (Overrides previous).
4.  **CLI Flag:** Path specified via `-c` (Highest priority).

## Environment & Tool Setup
The `metalncrna setup` command is optimized for CI/CD and portability:
- **Environment Detection:** Automatically skips creation if a Mamba environment with the same name already exists.
- **Resource Filtering:** If `--tools` is specified, it only downloads data/models for those specific tools.
- **Legacy Integration:** Uses local source code from `src/metalncrna/third_party/` to avoid broken external links.

## Development Workflow (using Pixi)
```bash
# Setup development environment (including pre-commit hooks)
pixi run install
pixi run pre-commit

# Run consensus tests
pixi run test
```

# Run mock tests (faster, doesn't require tools installed)
pixi run test-mock

# Build documentation
pixi run docs
```

## Continuous Integration (CI)
We use **GitHub Actions** (`.github/workflows/ci.yml`) to automatically validate every push to `main`.
The CI pipeline performs:
1. Environment setup via Pixi.
2. Code linting using `ruff`.
3. Execution of both Mock and Consensus tests.

## Production Scripts
The `scripts/` directory contains production utilities:
- `run_long_analysis.sh`: Optimized for long sequences or large datasets.
- `run_serial.sh`: Guaranteed serial execution for low-memory environments.
