# metaLncRNA v1.1

`metaLncRNA` is a modular, high-performance Python framework designed to identify Long Non-coding RNAs (lncRNAs) by orchestrating an ensemble of seven diverse computational tools. It resolves the "reproducibility gap" by automating environment management and providing a robust consensus prediction through weighted soft-voting.

## 📊 Why use an Ensemble Predictor?
Single-tool predictions are often biased by the specific features they prioritize (e.g., codon bias vs. k-mer profile). `metaLncRNA` mitigates these biases by combining Deep Learning, Support Vector Machines (SVM), and statistical methodologies into a unified pipeline.

---

## 🛠️ Integrated Tools & Methodologies

| Tool | Approach | Core Logic |
| :--- | :--- | :--- |
| **RNAsamba** | Deep Learning | Uses a deep neural network to classify transcripts based on learned sequence patterns. |
| **CPAT** | Logistic Regression | Calculates the Coding-Potential Assessment score using hexamer frequency and ORF size. |
| **CPPred** | SVM | Integrates multiple features including CTD (Composition, Transition, Distribution) and ORF characteristics. |
| **CNCI** | Motif Analysis | Identifies non-coding sequences based on the frequency of adjoining nucleotide triplets. |
| **CPC2** | SVM | Evaluates coding potential based on sequence intrinsic features, specifically peptide length and Fickett score. |
| **LGC** | Feature Relation | Uses the relationship between ORF length and GC content to distinguish lncRNAs. |
| **PLEK** | SVM | Analyzes transcripts using an improved k-mer scheme to capture fine-grained sequence patterns. |

---

## 📖 Usage Guide

### 1. Installation (Recommended: Pixi)
Pixi provides a deterministic environment and manages all Python 2.7/3.x dependencies automatically.
```bash
# Install dependencies and setup environments
pixi run setup
```

### 2. Integrated Pipeline
Run the full ensemble on your dataset. The pipeline is **checkpoint-aware**; if an analysis is interrupted, simply re-run the command to resume from the last successful tool.
```bash
pixi run predict -i transcripts.fasta -o results/ --project MyAnalysis --config metaLncRNA_config.yaml
```

### 3. Training Custom Models
Train species-specific models for **RNAsamba** (Deep Learning) and **CPAT** (Logistic Regression) using your own coding/non-coding datasets:
```bash
pixi run train --coding coding.fa --noncoding noncoding.fa -o my_models/
```

### 4. Output Structure
The project folder (`results/MyAnalysis/`) includes:
- `metalncrna_results.tsv`: Unified consensus table with individual tool probabilities and final `meta_score`.
- `metalncrna_report.html`: Interactive scientific dashboard featuring congruence matrices and transcript landscapes.
- **predicted_lncrnas.fasta**: Filtered FASTA file containing only identified lncRNAs.

### 5. Interactive AI Insights (New! 🤖)
Interpret your genomic results using a local AI Agent. While the default is the lightweight `llama3.2`, we highly recommend using a **Specialist Biomedical Model** for scientific publications:

- **Recommended Specialist:** `saama/openbiollm-llama3-8b` (Fine-tuned on PubMed and biomedical data).
- **Hardware Requirement:** Minimum **8GB RAM** (16GB recommended for 8B models).

```bash
# Pull the specialist model
ollama pull saama/openbiollm-llama3-8b

# Ask a specific question using the specialist
pixi run metalncrna ask "Why was sequence X classified as noncoding?" -r results/MyAnalysis/metalncrna_results.tsv -m saama/openbiollm-llama3-8b

# Start an interactive chat session
pixi run metalncrna chat -r results/MyAnalysis/metalncrna_results.tsv -m saama/openbiollm-llama3-8b
```
*Note: Requires [Ollama](https://ollama.com) installed and running.*

---

## 🐳 Deployment (Docker & Singularity)

For cloud or HPC environments, we provide pre-configured definitions in the `deploy/` directory:

- **Docker:** `docker build -f deploy/Dockerfile .`
- **Singularity/Apptainer:** `singularity build metaLncRNA.sif deploy/Singularity.def`

*For detailed architectural documentation and API reference, see the `docs/` directory.*
