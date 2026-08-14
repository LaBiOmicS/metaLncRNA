
import re
from Bio import SeqIO
from Bio.SeqUtils import gc_fraction


def clean_sequence_key(seq_id) -> str:
    """
    Internal helper to create a normalized key for matching tool outputs back to original sequence IDs:
    - Converts to string
    - Strips leading '>'
    - Takes first token
    - Lowercase
    - Strips tool-added ORF/coordinate suffixes like _orf_1, _ORF_1, or :100-200
    """
    s = str(seq_id).strip().lstrip(">").split()[0].lower()
    s = re.sub(r"(_orf_\d+|:\d+-\d+|:.*)$", "", s, flags=re.IGNORECASE)
    return s


def build_id_mapping(fasta_path):
    """
    Parses input FASTA and returns:
    - original_ids: list of original sequence IDs in their original FASTA order
    - norm_to_orig: dict mapping normalized key -> exact original sequence ID
    """
    original_ids = []
    norm_to_orig = {}
    for record in SeqIO.parse(fasta_path, "fasta"):
        raw_id = str(record.id).strip().lstrip(">").split()[0]
        original_ids.append(raw_id)
        norm_key = clean_sequence_key(raw_id)
        if norm_key not in norm_to_orig:
            norm_to_orig[norm_key] = raw_id
    return original_ids, norm_to_orig


def map_df_sequence_ids(df, norm_to_orig):
    """
    Maps sequence_id column in df to exact original sequence IDs using norm_to_orig dictionary.
    """
    if df is None or df.empty or "sequence_id" not in df.columns:
        return df

    def get_orig(id_val):
        key = clean_sequence_key(id_val)
        return norm_to_orig.get(key, str(id_val).strip().lstrip(">").split()[0])

    df = df.copy()
    df["sequence_id"] = df["sequence_id"].apply(get_orig)
    return df


def get_sequence_stats(fasta_path):
    """
    Calculates length and GC content for each sequence in a FASTA file.
    Returns a dictionary mapping EXACT original sequence ID to stats.
    """
    stats = {}
    for record in SeqIO.parse(fasta_path, "fasta"):
        seq_id = str(record.id).strip().lstrip(">").split()[0]
        stats[seq_id] = {
            "length": len(record.seq),
            "gc_content": round(gc_fraction(record.seq) * 100, 2)
        }
    return stats


def extract_lncrnas(input_fasta, output_fasta, predicted_ids):
    """
    Writes a new FASTA containing only the sequences in predicted_ids.
    Preserves exact original FASTA headers.
    """
    target_ids = {str(i).strip().lstrip(">").split()[0] for i in predicted_ids}
    norm_target_ids = {clean_sequence_key(i) for i in predicted_ids}

    lncrnas = []
    for record in SeqIO.parse(input_fasta, "fasta"):
        raw_id = str(record.id).strip().lstrip(">").split()[0]
        if raw_id in target_ids or clean_sequence_key(raw_id) in norm_target_ids:
            lncrnas.append(record)

    if lncrnas:
        SeqIO.write(lncrnas, output_fasta, "fasta")
        return len(lncrnas)
    return 0


