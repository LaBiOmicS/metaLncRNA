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
