from gtfparse import read_gtf
from building_tgs import Transcript_graph, Node
import sqlite3

from Bio import SeqIO

file = "/home/jack/sarscov2_processing/references/sarscov2.sqlite"
fasta_path = "/home/jack/sarscov2_processing/references/sarscov2_genome.fasta"
gtf_path = "/home/jack/sarscov2_processing/references/sarscov2.gtf"


def get_connection(file):
    conn = sqlite3.connect(file)
    conn.row_factory = sqlite3.Row
    return conn


def get_transcript_info(transcript, conn):
    result = conn.execute(
        "SELECT * FROM transcripts WHERE transcript = ?", (transcript,)
    ).fetchall()
    return list(result[0])


# kim et al is not suitable as gRNA is lumped into one cds
# df = read_gtf("/home/jack/Downloads/kim_et_al_sarscov2_mRNA_refseq.gtf")

# sarscov2.gtf is suitbale as ORF1ab is treated as the same ORF with different products


def import_fasta(file_path):
    """
    read fasta file and return a seq_dict.

    seq_dict key is seq id from fasta values are nested dicts with sequence and description as keys

    Params: Path to file
    """
    seq_dict = {}
    for seq_record in SeqIO.parse(open(file_path, "r"), "fasta"):
        if seq_record.id not in seq_dict:
            seq_dict[seq_record.id] = {
                "sequence": str(seq_record.seq),
                "description": seq_record.description,
            }
    return seq_dict


# NCBI Genes could also be used as the coding regions of orf1ab could be merged.
# df = read_gtf("/home/jack/Downloads/NCBI_genes.gtf")


def parse_gtf(file_path, feature):
    """
    Import the gtf as a pandas df and then subset based on the inputed feature

    file_path = string to file loc
    feature = string of gtf feature
    """

    df = read_gtf(file_path)
    subsetted_df = df[df["feature"] == feature]
    if len(subsetted_df) == 0:
        print("inputted feature is not found in the file")
        print("choose from ", list(df.feature))

    return subsetted_df


def get_orfs_from_file(file_path):
    gtf_feature = "CDS"
    CDS = parse_gtf(file_path, gtf_feature)
    ORF_dict = {}

    ORF_list = []
    # (start, stop, frame, type)
    for index, row in CDS.iterrows():
        ORF_list.append((row["start"], row["end"], row["start"] % 3, "CDS"))
        if row["gene_name"] not in ORF_dict:
            ORF_dict[row["gene_name"]] = {
                "start": [row["start"]],
                "stop": [row["end"]],
                "frame": [row["start"] % 3],
            }
        else:
            ORF_dict[row["gene_name"]]["start"].append(row["start"])
            ORF_dict[row["gene_name"]]["stop"].append(row["end"])
            ORF_dict[row["gene_name"]]["frame"].append(row["start"] % 3)

    return ORF_list, ORF_dict


def insert_orfs(graph, ORF_list):
    """
    This function takes a graph and inserts an orf into it adapting any impacted features to the new addition

    Params:
    graph = transcript graph object
    orflist = list of tuples with orf_info
    orf_info = tuple (start, stop, frame, type)
    """
    # new_node = Node(orf_info['key'], orf_info['type'], orf_info['frame'], (orf_info['start'], orf_info['stop']))
    for orf in ORF_list:
        graph.add_vertex(orf[3], orf[2], (orf[0], orf[1]))
        graph.statistics()


# print(seq_dict)


def construct_graph_from_file(gtf_path, fasta_path):
    """
    Take a gtf and fast and build a Transcript graph

    No failsafes included just trustung files match
    """
    seq_dict = import_fasta(fasta_path)
    for i in seq_dict:
        sequence_length = len(seq_dict[i]["sequence"])
    ORF_list, ORF_dict = get_orfs_from_file(gtf_path)
    # print(ORF_list)

    graph = Transcript_graph(sequence_length)

    insert_orfs(graph, ORF_list)
    script_string = graph.graph_to_js_plotly()
    # graph.describe()
    return script_string
