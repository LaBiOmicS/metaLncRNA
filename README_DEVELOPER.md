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
# Run tests
pixi run test

# Build documentation
pixi run docs
```
