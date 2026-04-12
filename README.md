# metaLncRNA v1.1 🧬🤖

<!-- Institutional Badges -->
[![University: UMC](https://img.shields.io/badge/University-UMC-0D47A1.svg)](https://www.umc.br/)
[![Laboratory: LaBiOmicS](https://img.shields.io/badge/Laboratory-LaBiOmicS-7B1FA2.svg)](https://github.com/LaBiOmicS)
[![Bioinformatics](https://img.shields.io/badge/Bioinformatics-lncRNA-green.svg)](https://github.com/LaBiOmicS/metaLncRNA)

<!-- Open Science Badges -->
[![Open Source](https://img.shields.io/badge/Open-Source-brightgreen.svg)](https://github.com/LaBiOmicS/metaLncRNA)
[![Open Science](https://img.shields.io/badge/Open-Science-blue.svg)](https://github.com/LaBiOmicS/metaLncRNA)
[![Open Data](https://img.shields.io/badge/Open-Data-brightgreen.svg)](https://github.com/LaBiOmicS/metaLncRNA)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![JOSS Status](https://img.shields.io/badge/JOSS-Pre--submission-brightgreen.svg)](https://joss.theoj.org/)

<!-- Tech & Method Badges -->
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Powered by Ollama](https://img.shields.io/badge/AI-Powered_by_Ollama-orange.svg)](https://ollama.com)
[![Ensemble Learning](https://img.shields.io/badge/Method-Ensemble_Learning-blueviolet.svg)](https://github.com/LaBiOmicS/metaLncRNA)

---

`metaLncRNA` is a modular, high-performance Python framework designed to identify Long Non-coding RNAs (lncRNAs) by orchestrating an ensemble of seven diverse computational tools. It resolves the "reproducibility gap" by automating environment management and providing a robust consensus prediction through weighted soft-voting.

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

```bash
# Recommended: Install with AI Agent support
pip install "metalncrna[agent]"

# Pull the lightweight default model
ollama pull llama3.2
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
**Developed by [LaBiOmics](https://github.com/LaBiOmics)** - *Laboratory of Bioinformatics and Omics Sciences.*
**Institution:** [Universidade de Mogi das Cruzes (UMC)](https://www.umc.br/)
