User Guide
==========

metaLncRNA provides a modular CLI interface for transcriptome analysis.

Installation
------------
The recommended way to install metaLncRNA is via PyPI:

.. code-block:: bash

    pip install metalncrna
    metalncrna setup

Common Commands
---------------

1. Setup Environments
~~~~~~~~~~~~~~~~~~~~~
Prepares all Mamba environments and downloads models.
.. code-block:: bash

    metalncrna setup [--tools tool1,tool2]

2. Integrated Prediction
~~~~~~~~~~~~~~~~~~~~~~~~
Runs the full ensemble on your transcript dataset.
.. code-block:: bash

    metalncrna predict -i transcripts.fasta -o ./results -p MyAnalysis --tools rnasamba,cpc2,cpat,plek,cnci,cppred,lgc

3. Manual Aggregation
~~~~~~~~~~~~~~~~~~~~~
If tools were run individually, you can aggregate results manually.
.. code-block:: bash

    metalncrna aggregate -d results_dir/ -o final_results.tsv -f transcripts.fasta

4. Custom Model Training
~~~~~~~~~~~~~~~~~~~~~~~~
Train species-specific models for supported tools.
.. code-block:: bash

    metalncrna train --coding coding.fa --noncoding noncoding.fa -o my_models/ --tools rnasamba,cpat

5. Interactive AI Insights (New! 🤖)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Interpret your genomic results using a local AI Agent. While the default is the lightweight `llama3.2`, we highly recommend using a **Specialist Biomedical Model** for scientific publications:

- **Recommended Specialist:** `saama/openbiollm-llama3-8b` (Fine-tuned on PubMed and biomedical data).
- **Hardware Requirement:** Minimum **8GB RAM** (16GB recommended for 8B models).

.. code-block:: bash

    # Ask a specific question using the specialist
    metalncrna ask "Why was sequence X classified as noncoding?" -r ./results/metalncrna_results.tsv -m saama/openbiollm-llama3-8b

    # Start an interactive chat session
    metalncrna chat -r ./results/metalncrna_results.tsv -m saama/openbiollm-llama3-8b

*Note: Requires Ollama (https://ollama.com) installed and running.*

Detailed Chat Usage
^^^^^^^^^^^^^^^^^^^
The ``chat`` command opens a persistent, interactive session where the AI Agent acts as a senior bioinformatician who "sees" your results.

**How to interact:**

1. **Start the session:** Run ``metalncrna chat -r <results_file>``.
2. **Context Awareness:** The agent automatically knows the total number of sequences, the count of lncRNAs found, and the consensus logic of the tool.
3. **Ask about specific sequences:**
   - *"Tell me more about transcript_042."*
   - *"Why did CPAT disagree with the consensus for sequence XYZ?"*
4. **General Analysis:**
   - *"Give me a summary of the most confident lncRNA candidates."*
   - *"How many sequences have a 7/7 tool agreement?"*
5. **Biological Context:**
   - *"What are the common functions of lncRNAs found in intergenic regions?"*
   - *"Based on these results, what would be the next step for validation?"*

**Exiting the chat:** Type ``exit``, ``quit``, or ``sair`` to return to the terminal.

Tool-Specific Execution
-----------------------
You can run tools individually if needed:

.. code-block:: bash

    metalncrna rnasamba -i transcripts.fasta -o output/
    metalncrna cpc2 -i transcripts.fasta -o output/
    metalncrna cpat -i transcripts.fasta -o output/ --species human
    metalncrna plek -i transcripts.fasta -o output/
    metalncrna cnci -i transcripts.fasta -o output/ --mode ve
    metalncrna cppred -i transcripts.fasta -o output/
    metalncrna lgc -i transcripts.fasta -o output/

API Reference
-------------
.. automodule:: metalncrna.engine.consensus
   :members:
   :undoc-members:
