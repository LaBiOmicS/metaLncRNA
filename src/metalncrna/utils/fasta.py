from Bio import SeqIO
from Bio.SeqUtils import gc_fraction
import pandas as pd
from pathlib import Path

def get_sequence_stats(fasta_path):
    """
    Calculates length and GC content for each sequence in a FASTA file.
    Returns a dictionary mapping lowercase sequence ID to stats.
    """
    stats = {}
    for record in SeqIO.parse(fasta_path, "fasta"):
        seq_id = str(record.id).lower().split()[0]
        stats[seq_id] = {
            "length": len(record.seq),
            "gc_content": round(gc_fraction(record.seq) * 100, 2)
        }
    return stats

def extract_lncrnas(input_fasta, output_fasta, predicted_ids):
    """
    Writes a new FASTA containing only the sequences in predicted_ids.
    """
    # Normalize IDs to lowercase for comparison
    target_ids = {str(i).lower() for i in predicted_ids}
    
    lncrnas = []
    for record in SeqIO.parse(input_fasta, "fasta"):
        norm_id = str(record.id).lower().split()[0]
        if norm_id in target_ids:
            lncrnas.append(record)
            
    if lncrnas:
        SeqIO.write(lncrnas, output_fasta, "fasta")
        return len(lncrnas)
    return 0
