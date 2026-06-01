# Contributing to metaLncRNA

We welcome contributions to metaLncRNA! Whether you want to add a new tool adapter, improve the consensus engine, or enhance the reporting UI, your help is appreciated.

## How to Contribute
1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Add tests for your changes.
4. Submit a Pull Request with a clear description of your work.

## Development Setup
```bash
pip install -e .
metalncrna setup
```

## Adding a New Tool
To add a new tool, create a new class in `src/metalncrna/adapters/` that inherits from `BaseAdapter` and implement the `run` and `parse_results` methods.
