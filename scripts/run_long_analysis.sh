#!/bin/bash
# Script de execucao protegida para o metaLncRNA
LOG_FILE="analysis_production_$(date +%Y%m%d_%H%M%S).log"

echo "Iniciando execucao do pipeline..." | tee -a "$LOG_FILE"

# Ativa o ambiente e roda o predict
# Usando --keep-intermediates para debug, se necessário
mamba run -n metalnc_core python -m metalncrna.cli predict \
    -i ../examples/GDRF01.fasta \
    -o ../examples/analysis_results \
    -p RealData_$(date +%Y%m%d) \
    --tools rnasamba,cpc2,cpat,plek,cnci,cppred,lgc \
    --n-jobs 4 >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "Sucesso! Pipeline finalizado. Log: $LOG_FILE" | tee -a "$LOG_FILE"
else
    echo "Erro na execucao! Verifique o log: $LOG_FILE" | tee -a "$LOG_FILE"
fi
