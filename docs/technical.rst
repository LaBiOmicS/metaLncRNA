Technical Architecture
======================

metaLncRNA employs a sophisticated orchestration layer to manage biological predictors, ensuring reproducibility across heterogeneous computational environments.

Scope
-----
The scope of metaLncRNA covers the identification of Long Non-coding RNAs (lncRNAs) from transcriptomic FASTA sequences. It provides an automated ensemble pipeline that integrates 7 state-of-the-art predictors, offering weighted consensus scores, interactive visualization, and species-specific model retraining.

Requirements
------------

Functional Requirements:
* **Ensemble Prediction:** Ability to run one or more of the 7 integrated tools.
* **Weighted Consensus:** Aggregation of coding probability scores using benchmarked weights.
* **Custom Training:** Ability to retrain RNAsamba and CPAT models with user-provided datasets.
* **Report Generation:** Automatic generation of standardized results (TSV) and filtered FASTA files.
* **Checkpointing:** Resumable pipelines that skip already processed tools.

Non-Functional Requirements:
* **Reproducibility:** All environments are isolated via Mamba/Conda to prevent dependency conflicts.
* **Portability:** The tool is deployable via PyPI, Docker, Singularity, and Galaxy.
* **Performance:** Supports multi-threaded parallel execution (`--n-jobs`) to optimize throughput on HPC clusters.
* **Modularity:** New tools can be added via the Adapter pattern without modifying the consensus engine.
* **AI Interpretation:** Local SLMs (Small Language Models) can provide natural language insights on the consensus decision without compromising user data privacy.

The Adapter Pattern
-------------------
To interface with legacy and modern tools, metaLncRNA uses the **Adapter Design Pattern**. Each tool is wrapped in a dedicated adapter that handles:
- **Environment Isolation:** Using Mamba environments to resolve version conflicts.
- **Path Sanitization:** Mapping absolute paths and ensuring execution in safe CWDs.
- **Normalization:** Standardizing heterogeneous tool outputs into a uniform Pandas DataFrame schema.

Consensus Methodology
---------------------
The consensus engine uses a **Weighted Soft-Voting** approach. Unlike simple majority voting, this method respects the varying accuracy of different predictors.

.. math::
    S = \\frac{\sum_{i=1}^{n} w_i \cdot P_i}{\sum_{i=1}^{n} w_i}

Weights are calibrated against verified benchmarks to maximize F1-scores.

AI-Driven Interpretation Layer
------------------------------
To bridge the gap between numerical prediction and biological interpretation, metaLncRNA includes an AI Agent based on local Large Language Models (LLMs).

- **LLM Engine:** Powered by Ollama, supporting models such as Llama-3.2 (general-purpose) and OpenBioLLM-8B (biomedical specialist).
- **Interpretability:** The agent analyzes conflicting tool probabilities to explain the consensus decision in natural language.
- **Data Privacy:** All LLM inference is performed locally, ensuring that genomic sequences and research results are never transmitted to external servers.
- **Hardware Requirements:** 
    - Standard (Llama-3.2): 4GB RAM.
    - Specialist (OpenBioLLM-8B): Minimum 8GB RAM (16GB recommended).

Scalability and HPC Performance
-------------------------------
metaLncRNA is optimized for High-Performance Computing (HPC) clusters:
- **Parallel Dispatch:** Utilizes concurrent.futures to maximize multi-core utilization.
- **Checkpointing:** Automatically detects existing _standardized.tsv files to resume interrupted analyses.
- **Memory Optimization:** Implements data type downcasting for consensus aggregation, reducing memory footprint for large-scale transcriptomic datasets.
- **Resource Management:** Designed to operate efficiently within Docker/Singularity containers, making it easy to deploy on shared cluster resources.
