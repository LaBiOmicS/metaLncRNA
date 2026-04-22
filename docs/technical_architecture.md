# Technical Architecture

metaLncRNA employs a sophisticated orchestration layer to manage biological predictors, ensuring reproducibility across heterogeneous computational environments.

## Scope
The scope of `metaLncRNA` covers the identification of Long Non-coding RNAs (lncRNAs) from transcriptomic FASTA sequences. It integrates 7 state-of-the-art predictors, offering weighted consensus scores and species-specific model retraining.

## Requirements

### Functional Requirements:
- **Ensemble Prediction:** Ability to run one or more of the 7 integrated tools.
- **Weighted Consensus:** Aggregation of coding probability scores using benchmarked weights.
- **Custom Training:** Ability to retrain RNAsamba and CPAT models with user-provided datasets.
- **Report Generation:** Automatic generation of standardized results (TSV) and filtered FASTA files.
- **Checkpointing:** Resumable pipelines that skip already processed tools.

### Non-Functional Requirements:
- **Reproducibility:** All environments are isolated via Mamba/Conda.
- **Portability:** Deployable via PyPI, Docker, Singularity, and Galaxy.
- **AI Interpretation:** Local SLMs provide natural language insights on the consensus decision without compromising user data privacy.

## The Adapter Pattern
To interface with legacy and modern tools, metaLncRNA uses the **Adapter Design Pattern**. Each tool is wrapped in a dedicated adapter that handles:
1. **Environment Isolation:** Using Mamba environments to resolve version conflicts.
2. **Path Sanitization:** Mapping absolute paths and ensuring execution in safe CWDs.
3. **Normalization:** Standardizing heterogeneous tool outputs into a uniform schema.

## Consensus Methodology
The consensus engine uses a **Weighted Soft-Voting** approach. This method respects the varying accuracy of different predictors.

$$S = \frac{\sum_{i=1}^{n} w_i \cdot P_i}{\sum_{i=1}^{n} w_i}$$

Weights are calibrated against verified benchmarks to maximize F1-scores.

## AI-Driven Interpretation Layer
To bridge the gap between numerical prediction and biological interpretation, `metaLncRNA` includes an AI Agent based on local Large Language Models (LLMs).

- **LLM Engine:** Powered by Ollama.
- **Interpretability:** Analyzes conflicting tool probabilities to explain the consensus decision in natural language.
- **Data Privacy:** All LLM inference is performed locally.
- **Hardware Requirements:** 
    - Standard (Llama-3.2): 4GB RAM.
    - Specialist (OpenBioLLM-8B): Minimum 8GB RAM (16GB recommended).

## Scalability and HPC Performance
- **Parallel Dispatch:** Utilizes `concurrent.futures`.
- **Memory Optimization:** Implements data type downcasting for consensus aggregation.
- **Resource Management:** Designed to operate efficiently within Docker/Singularity containers.
