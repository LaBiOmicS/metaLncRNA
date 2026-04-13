# metaLncRNA v1.1.6 🧬🤖

<p align="center">
  <img src="logo.png" alt="metaLncRNA Logo" width="50%">
</p>

<!-- Institutional Badges -->
[![DOI](https://zenodo.org/badge/1208858176.svg)](https://doi.org/10.5281/zenodo.19547230)
[![University: UMC](https://img.shields.io/badge/University-UMC-0D47A1.svg)](https://www.umc.br/)
[![Laboratory: LaBiOmicS](https://img.shields.io/badge/Laboratory-LaBiOmicS-7B1FA2.svg)](https://github.com/LaBiOmicS)
[![Bioinformatics](https://img.shields.io/badge/Bioinformatics-lncRNA-green.svg)](https://github.com/LaBiOmicS/metaLncRNA)

<!-- Open Science Badges -->
[![PyPI Version](https://img.shields.io/pypi/v/metalncrna.svg)](https://pypi.org/project/metalncrna/)
[![Open Source](https://img.shields.io/badge/Open-Source-brightgreen.svg)](https://github.com/LaBiOmicS/metaLncRNA)
[![Open Science](https://img.shields.io/badge/Open-Science-blue.svg)](https://github.com/LaBiOmicS/metaLncRNA)
[![Open Data](https://img.shields.io/badge/Open-Data-brightgreen.svg)](https://github.com/LaBiOmicS/metaLncRNA)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![JOSS Status](https://img.shields.io/badge/JOSS-Pre--submission-brightgreen.svg)](https://joss.theoj.org/)
[![CI Status](https://github.com/LaBiOmicS/metaLncRNA/actions/workflows/ci.yml/badge.svg)](https://github.com/LaBiOmicS/metaLncRNA/actions/workflows/ci.yml)

<!-- Tech & Method Badges -->
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Powered by Ollama](https://img.shields.io/badge/AI-Powered_by_Ollama-orange.svg)](https://ollama.com)
[![Ensemble Learning](https://img.shields.io/badge/Method-Ensemble_Learning-blueviolet.svg)](https://github.com/LaBiOmicS/metaLncRNA)

---

`metaLncRNA` is a modular, high-performance Python framework designed to identify Long Non-coding RNAs (lncRNAs) by orchestrating an ensemble of seven diverse computational tools. It resolves the "reproducibility gap" by automating environment management and providing a robust consensus prediction through weighted soft-voting.

---

## 📂 Repository Structure

- `src/metalncrna/`: Core package logic and adapters.
  - `data/`: Internal default configurations and pre-packaged models.
  - `third_party/`: Integrated source code for legacy predictors (LGC, CPPred, CNCI).
- `scripts/`: Production Bash utilities for HPC and long-running jobs.
- `tests/`: Automated unit and integration test suite.
- `docs/`: Technical guides and architecture details.
- `deploy/`: Docker and Singularity definitions.
- `INPI_Registration/`: Legal software registration assets.

---

## ⚙️ Configuration

`metaLncRNA` follows a robust configuration loading order:
1. **Internal Defaults:** Built-in weights and paths in `src/metalncrna/data/default_config.yaml`.
2. **Local Config:** `metaLncRNA_config.yaml` in your current working directory.
3. **User Home:** `~/.metalncrna/config.yaml`.
4. **Explicit Path:** Provided via the `-c` or `--config` flag.

---

## 🚀 Key Features

- **Ensemble Prediction:** Combines 7 tools (RNAsamba, CPAT, CPC2, PLEK, CNCI, CPPred, LGC).
- **Interactive AI Agent:** Integrated local LLM assistant (**Llama-3.2** or **OpenBioLLM**) to interpret results and explain classification decisions.
- **Reproducibility First:** Built-in environment isolation via **Mamba** and **Pixi**.
- **Scientific Dashboard:** Interactive HTML reports with tool congruence matrices.
- **Publication Ready:** Formatted according to JOSS standards for scientific software.

---

## 📖 Documentation

For detailed instructions, please refer to our **[Documentation Hub](docs/README.md)**:

- 🛠️ **[User Guide](docs/user_guide.md)**: Installation, common commands, and AI Chat usage.
- 🏗️ **[Technical Architecture](docs/technical_architecture.md)**: Ensemble methodology and AI-driven interpretation layer.
- 🔧 **[Troubleshooting](docs/troubleshooting.md)**: Common issues and hardware requirements.

---

## 🛠️ Quick Start

### 1. Installation

#### Option A: via `pip` (Fastest)
We recommend using a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install "metalncrna[agent]"
metalncrna setup
```

#### Option B: via `Conda` / `Mamba`
Perfect for bioinformaticians using Bioconda:

```bash
# Create environment from the provided file
mamba env create -f environment.yml
conda activate metalncrna

# Finalize setup
metalncrna setup
```

### 2. Run Integrated Pipeline
```bash
metalncrna predict -i transcripts.fasta -o ./results -p MyAnalysis
```

### 3. Ask the AI Agent
```bash
# Get a summary of your findings
metalncrna ask "Summarize the analysis results" -r ./results/MyAnalysis/metalncrna_results.tsv
```

---

## 🐳 Deployment
Pre-configured definitions are available for **Docker** and **Singularity/Apptainer** in the `deploy/` directory.

## 🤝 Contributing
Contributions are welcome! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
**Developed by [LaBiOmicS](https://github.com/LaBiOmicS)** - *Laboratory of Bioinformatics and Omics Sciences.*
**Institution:** [Universidade de Mogi das Cruzes (UMC)](https://www.umc.br/)
