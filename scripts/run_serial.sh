#!/bin/bash
# Script de execucao serial forçada para garantir conclusão
DIR="/media/menegidio/Storage/Trabalho/UMC/LaBiOmics/Bioinformatics/Bioinfo/lncRNA/metaLncRNA"
INPUT="$DIR/examples/GDRF01.fasta"
OUT="$DIR/examples/analysis_results/RealDataValidation"

TOOLS=("rnasamba" "cpc2" "cpat" "plek" "cnci" "cppred" "lgc")

for TOOL in "${TOOLS[@]}"; do
    echo "[*] Rodando $TOOL..."
    mamba run -n metalnc_core python -m metalncrna.cli $TOOL -i "$INPUT" -o "$OUT" --config "$DIR/metaLncRNA_config.yaml"
    if [ $? -eq 0 ]; then
        echo "[+] $TOOL finalizado."
    else
        echo "[!] $TOOL falhou. Verifique o log."
    fi
done

echo "[*] Agregando resultados..."
mamba run -n metalnc_core python -m metalncrna.cli aggregate -d "$OUT" -o "$OUT/metalncrna_results.tsv" -f "$INPUT"
echo "[+] Pipeline finalizado com sucesso."
