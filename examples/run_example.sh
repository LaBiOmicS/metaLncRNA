#!/bin/bash
# metaLncRNA v1.1.2 Quick Start Script

echo "[*] Starting metaLncRNA ensemble analysis..."

# Run the ensemble prediction on the sample dataset
python -m metalncrna.cli predict \
    -i sample.fasta \
    -o results/ \
    --project ExampleAnalysis \
    --tools rnasamba,cpc2,cpat,plek,cnci,cppred,lgc \
    --n-jobs 4

echo "[+] Analysis complete. Check 'results/ExampleAnalysis/' for report and results."
