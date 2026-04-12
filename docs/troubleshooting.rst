Troubleshooting
===============

Common issues and their resolutions.

Environments & Mamba
--------------------
**Error: Mamba command not found**
Ensure Mambaforge or Conda is installed and added to your PATH. Verify with ``mamba --version``.

**Error: Tool failed to train**
Training requires a minimum number of sequences and sufficient diversity in FASTA input to converge. Ensure your dummy training files contain at least 100 sequences and valid ORF structures.

Pipeline Interruption
---------------------
**Can I resume an analysis?**
Yes. metaLncRNA is checkpoint-aware. Simply re-run the same command, and the tool will detect existing ``_standardized.tsv`` files, skipping tools that have already finished successfully.

Docker & HPC
------------
**Permission denied errors in Singularity**
Ensure your working directory is correctly bound using the ``--bind`` flag if running on an HPC cluster:
``singularity run --bind /my/data:/data metaLncRNA.sif predict -i /data/input.fa -o /data/results``

AI Agent & Ollama
-----------------
**Error: 'ollama' package not found**
The AI features are optional. Install them with:
``pip install "metalncrna[agent]"``

**Error: Connection refused to Ollama**
Ensure the Ollama server is running on your machine. You can start it with the command ``ollama serve``.

**Error: Model not found**
You must download the model before using it. For the default model, run:
``ollama pull llama3.2``
For the biomedical specialist, run:
``ollama pull saama/openbiollm-llama3-8b``

**System slowness or crash during AI analysis**
Running large models (like 8B specialists) requires significant RAM. Ensure you have at least **8GB of free RAM**. If you have less than 8GB, stick to the lightweight ``llama3.2`` model.
