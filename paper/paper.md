---
title: 'metaLncRNA: A Sustainable and Reproducible Ensemble Predictor for Long Non-coding RNA Identification'
authors:
  - name: Pâmela Souza Corrêa
    orcid: 0000-0002-2889-3790
    affiliation: 1
    corresponding: true
  - name: Caio Martins Zampini
    orcid: 0009-0000-1173-2862
    affiliation: 1
    corresponding: true
  - name: David Aciole Barbosa
    orcid: 0000-0003-3875-2307
    affiliation: "1, 4"
  - name: Rubens Pasa
    orcid: 0000-0002-3513-4071
    affiliation: 2
  - name: Karine Frehner Kavalco
    orcid: 0000-0002-4955-2792
    affiliation: 2
  - name: Luiz Roberto Nunes
    orcid: 0000-0002-4633-196X
    affiliation: 3
  - name: Daniela Leite Jabes
    orcid: 0000-0001-7297-0784
    affiliation: 1
  - name: Robson Rodrigues da Silva
    orcid: 0000-0003-1082-0777
    affiliation: 1
  - name: Fabiano Bezerra Menegidio
    orcid: 0000-0002-4705-8352
    affiliation: 1
affiliations:
  - name: Universidade de Mogi das Cruzes, Mogi das Cruzes, SP, Brasil
    index: 1
  - name: Universidade Federal de Viçosa, Viçosa, MG, Brasil
    index: 2
  - name: Universidade Federal do ABC, Santo André, SP, Brasil
    index: 3
  - name: Universidade Estadual Paulista, Botucatu, SP, Brasil
    index: 4
date: 12 April 2026
year: 2026
bibliography: paper.bib
tags:
  - Python
  - bioinformatics
  - lncRNA
  - genomics
  - ensemble learning
  - software orchestration
  - reproducibility
---

# Summary

Long non-coding RNAs (lncRNAs) are fundamental regulators of gene expression, involved in processes ranging from epigenetic gene silencing to human disease [@Statello2021]. Despite their biological significance, the precise identification of lncRNAs in high-throughput transcriptomic data remains a significant challenge. Most lncRNAs lack strong sequence conservation and coding potential, making them difficult to distinguish from protein-coding transcripts (PCTs) or transcriptional noise.

`metaLncRNA` is a modular Python framework that addresses this problem through an automated ensemble strategy. It orchestrates seven established predictors that cover the three main computational pillars of lncRNA detection:
1. **Statistical Codon Bias:** CPAT [@CPAT2013] and LGC [@LGC2019].
2. **Machine Learning (SVM/K-mers):** CPC2 [@CPC22017], PLEK [@PLEK2014], and CNCI [@CNCI2013].
3. **Deep Learning:** RNAsamba [@RNAsamba2020].
4. **Integrative Feature Analysis:** CPPred [@CPPred2019].

By leveraging isolated Mamba environments [@Mamba2022], `metaLncRNA` provides a unified interface that manages disparate software dependencies transparently, delivering a robust consensus prediction through a standardized tabular report.

# Statement of Need

The accurate classification of transcripts is essential for annotating novel genomes and analyzing clinical transcriptomics. However, recent reviews on computational methods highlight two systemic barriers that hinder progress in the field: **methodological instability** and the **reproducibility gap** [@Zhao2023].

The target audience for metaLncRNA includes bioinformaticians, computational biologists, and genomics researchers working with novel transcriptomic assemblies.

### Methodological Instability and the Need for Ensembles
Individual lncRNA identification tools are often biased towards specific transcript features (e.g., k-mer frequency, ORF length). This leads to significant discrepancies between tools, with low concordance rates when applied to the same dataset [@Uszczynska2018]. Ensemble learning has been demonstrated to mitigate these biases and provide superior accuracy. However, previous ensemble tools such as `ezLncPred` [@ezLncPred2019], while pioneering, have largely been abandoned.

### Software Atrophy and the Reproducibility Gap
A critical challenge in modern life sciences is "software atrophy," where high-impact tools become unusable due to their reliance on deprecated software stacks. Many lncRNA predictors require legacy Python 2.7 environments and specific library versions that conflict with modern Python 3.x frameworks. This "dependency hell" creates a significant reproducibility barrier. `metaLncRNA` was developed to bridge this gap, leveraging the Bioconda ecosystem [@Gruning2018] and the Mamba package manager [@Mamba2022] to create a portable architecture that ensures long-term usability and scientific reproducibility.

# State of the field

Ensemble lncRNA prediction is not a new idea. `ezLncPred` [@ezLncPred2019] was the first framework to combine multiple classical predictors behind a single interface, and it demonstrated the value of the approach. However, its codebase has not been maintained, and its dependencies no longer resolve cleanly on current Linux distributions, precisely the failure mode `metaLncRNA` is designed to avoid.

Individual predictors (CPAT, CPC2, RNAsamba, and others) continue to be released and updated, but each returns only its own score and leaves orchestration to the user. General workflow engines such as Snakemake and Nextflow can in principle chain the tools together, but they do not solve the dependency-isolation problem. They still require the user to produce working environments for each predictor and provide no mechanism for probabilistic consensus over the outputs.

`metaLncRNA` contributes three elements not offered by existing alternatives:

1. **Orchestration with dependency isolation.** Legacy Python 2.7 tools (CNCI, CPC2, CPPred, LGC) are driven from a modern Python 3.10 codebase without runtime conflicts, and their source code is vendored under `third_party/` so the pipeline remains functional if upstream repositories disappear.
2. **Weighted probabilistic consensus.** Rather than a simple majority vote, the framework aggregates each tool's coding probability through a benchmarked reliability weight.
3. **Local interpretation layer.** Consensus decisions can be explained through a locally hosted language model, so sequence data never leaves the user's machine.

# Architecture and Implementation

`metaLncRNA` is built on a modular architecture that prioritizes stability and performance. Its **Ensemble Engine** performs weighted soft-voting across tools to provide a single, robust confidence score. To accommodate large-scale transcriptomic datasets, the framework employs parallel dispatch and memory optimization techniques, ensuring scalability across both local workstations and high-performance computing (HPC) environments.

Furthermore, the framework introduces a novel **AI-driven interpretation layer**. By leveraging local Small Language Models (SLMs) such as Llama-3.2 or biomedical specialists like **OpenBioLLM-8B** [@saama2024] via Ollama, `metaLncRNA` provides researchers with natural language insights into prediction results. While general-purpose models run on minimal resources, specialist 8B models provide deeper biological context for transcript classification, requiring a minimum of **8GB of RAM**. This agent can explain complex consensus decisions (e.g., why a specific transcript was classified as non-coding despite tool disagreement) and generate executive summaries, bridging the gap between raw genomic data and biological interpretation without compromising user privacy or requiring high-performance computing resources.

### 1. The Ensemble: A Multi-Algorithm Approach
The software integrates seven tools carefully selected to cover the main computational strategies for lncRNA identification:
- **Deep Learning (RNAsamba [@RNAsamba2020]):** Utilizes convolutional neural networks to learn sequence patterns.
- **Support Vector Machines (CPPred [@CPPred2019], CPC2 [@CPC22017], PLEK [@PLEK2014]):** Use k-mer frequencies, ORF metrics, and other sequence features to build classification models.
- **Statistical & Heuristic Models (CPAT [@CPAT2013], CNCI [@CNCI2013], LGC [@LGC2019]):** Rely on logistic regression or codon bias statistics.

### 2. Environment Orchestration and Legacy Tool Management
The core innovation of `metaLncRNA` is its ability to manage conflicting software dependencies. The `metalncrna setup` command automatically builds isolated Mamba environments for each tool, allowing modern Python 3.10 libraries to coexist with the legacy Python 2.7 environments required by CNCI, CPC2, CPPred, and LGC. Furthermore, to ensure long-term stability and prevent issues from abandoned code repositories, the source code for these essential legacy tools is bundled directly within the `metaLncRNA` package in a `third_party` directory.

### 3. Weighted Soft-Voting Consensus
The software's `ConsensusEngine` implements a **Weighted Soft-Voting** algorithm. The final meta-score ($S$) is calculated as:

$$S = \frac{\sum_{i=1}^{n} w_i \cdot P_i}{\sum_{i=1}^{n} w_i}$$

where $w_i$ is a benchmarked reliability weight for each tool $i$, and $P_i$ is its predicted coding probability. A transcript is classified as an lncRNA if $S \le 0.5$.

# Key Features and Data Outputs

`metaLncRNA` produces high-confidence, standardized tabular results for every analysis. The pipeline output includes:
- **`metalncrna_results.tsv`**: A unified consensus table containing individual tool probabilities, the final meta-score ($S$), and consensus support metrics.
- **`predicted_lncrnas.fasta`**: A filtered FASTA file containing only transcripts classified as lncRNAs, facilitating downstream functional genomic analysis.
- **`metalncrna.log`**: A comprehensive execution log, ensuring auditability and traceability of the ensemble classification process.

### Extensibility and Custom Model Training
To support research on non-model organisms, `metaLncRNA` includes a dedicated **Training Module**. The `metalncrna train` command allows users to generate their own species-specific models for **RNAsamba** and **CPAT** by providing custom sets of coding and non-coding FASTA files. This feature transforms `metaLncRNA` from a simple predictor into an extensible research platform.

# Availability and Reproducibility
`metaLncRNA` is designed for maximum accessibility and is distributed across multiple platforms:
- **PyPI & Bioconda:** Available for easy installation and dependency management within the life sciences ecosystem [@Gruning2018].
- **Pixi:** A declarative package management tool providing a modern, reproducible development environment via `pixi.toml` [@Pixi2024].
- **Docker & Singularity:** Pre-configured container images ensure absolute reproducibility in cloud and shared High-Performance Computing (HPC) environments.
- **Galaxy:** A validated ToolShed wrapper makes `metaLncRNA` accessible to experimental biologists through a user-friendly, web-based platform [@Galaxy2018].

# Acknowledgements

We thank the original developers of the integrated tools.

# References
