from pathlib import Path

from metalncrna.engine.consensus import ConsensusEngine
from metalncrna.utils.fasta import extract_lncrnas, get_sequence_stats
from metalncrna.utils.reports import generate_html_report

# Carrega os resultados
res_dir = Path("../examples/analysis_results/RealDataGDRF01/")
files = list(res_dir.glob("*_standardized.tsv"))
files_dict = {f.name.replace("_standardized.tsv", ""): f for f in files}

# Gera consenso
data_dict = ConsensusEngine.from_files(files_dict)
final_df = ConsensusEngine.simple_voting(data_dict)
final_df.to_csv(res_dir / "metalncrna_results.tsv", sep="\t", index=False)

# Gera relatório e FASTA
stats = get_sequence_stats("../examples/GDRF01.fasta")
generate_html_report(final_df, data_dict, stats, res_dir / "metalncrna_report.html")
lncrna_ids = final_results = final_df[final_df["consensus_label"] == "noncoding"]["sequence_id"].tolist()
extract_lncrnas("../examples/GDRF01.fasta", res_dir / "predicted_lncrnas.fasta", lncrna_ids)
