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

## Robustness & Legacy Support (v2.0.0 Updates)
Working with legacy bioinformatics tools requires active mitigation of technical debt in third-party code. In version 2.0.0, metaLncRNA introduced critical stability patches:

### CNCI Stability Patch
- **Non-Canonical Filtering:** CNCI (Python 2.7 legacy) originally lacked robust handling of IUPAC ambiguous nucleotides beyond 'N'. metaLncRNA now implements a strict pre-filtering layer in the adapter that excludes sequences containing characters outside the [A, T, C, G, U] set, preventing `KeyError` crashes in the di-nucleotide hash table.
- **Multiprocessing Deadlock:** Fixed a synchronization bug in the original `CNCI.py` where a flawed `join()` loop caused the parent process to hang indefinitely if a child process crashed. The logic was replaced with a robust process-tracking loop.
- **Busy-Wait Mitigation:** Replaced the infinite busy-wait loop in CNCI's file aggregation stage with a time-limited polling mechanism and proper process status checks.

### Dispatcher Optimizations
- **Thread Capping:** The `Dispatcher` now caps CNCI parallelism to 4 threads. This reduces disk I/O contention and prevents the legacy multiprocessing logic from overwhelming the system, especially when processing many small transcriptomic files.
- **Failure-Resilient Cleanup:** To facilitate debugging, the cleanup of intermediate files is now conditional. If any tool in the ensemble fails, metaLncRNA preserves the `intermediates/` directory for that sample, regardless of the global `keep_intermediates` setting.

## Scalability and HPC Performance
- **Parallel Dispatch:** Utilizes `concurrent.futures`.
- **Memory Optimization:** Implements data type downcasting for consensus aggregation.
- **Resource Management:** Designed to operate efficiently within Docker/Singularity containers.
