import sqlite3
import pandas as pd
import sys

connection = sqlite3.connect('database.db')

info_df = pd.read_csv(sys.argv[1])

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

# df is constructed to have all relevant info ready so each row is used to populate a table entry
for i in range(len(info_df)):
    cur.execute("INSERT INTO conditions (sra_run, seq_type, hpi, moi, host_cell, treatment, elongating, initiating, study, sars_vs_mock) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
          (info_df['Run'][i], info_df['seq_type'][i], int(info_df['hpi'][i]), info_df['moi'][i], info_df['host_cell'][i], info_df['treatment'][i], bool(info_df['elongating'][i]), bool(info_df['initiating'][i]), info_df['study'][i], 'sars')
            )

# This input is a version of the sra run table with useless bits cut out and some columns manually supplemented with information from the study page
chavez = pd.read_csv('/home/jack/Downloads/condition_run_chavez.csv')


#Parse each row of the data frame before inserting into the conditions table
for i in range(len(chavez['filename']) -1):
    tokens = chavez['filename'][i].split("_")
    if tokens == ['/']:
        continue
    sra_run = chavez['run'][i]
    seq_type = tokens[5]
    hpi = int(tokens[4])
    moi = tokens[3]
    sars_mock = tokens[2]
    treatment = tokens[1]
    host_cell = tokens[0]
    study = "Puray-Chavez et al"
    if hpi == 0:
        hpi = None
    if host_cell == 'human':
        host_cell = 'Primary human bronchial epithelial cells'
    if host_cell == 'vero':
        host_cell = 'VeroE6'
    if seq_type == 'rna':
        treatment = None
    if seq_type in ['harr', 'ltm']:
        initiating = 1
        elongating = 0
    else:
        initiating = 0
        elongating = 1
    cur.execute("INSERT INTO conditions (sra_run, seq_type, hpi, moi, host_cell, treatment, elongating, initiating, study, sars_vs_mock) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
          (sra_run, seq_type, hpi, moi, host_cell, treatment, bool(elongating), bool(initiating), study, sars_mock)
            )


# Manually input data for chavez
cur.execute("INSERT INTO study_info (study_id, known_as, title, journal, abstract, authors, doi, release_date) VALUES ('SRP286182', 'Puray-Chavez et al', 'The translational landscape of SARS-CoV-2 and infected cells', 'bioRxiv', 'SARS-CoV-2, a betacoronavirus with a positive-sense RNA genome, has caused the ongoing COVID-19 pandemic. Although a large number of transcriptional profiling studies have been conducted in SARS-CoV-2 infected cells, little is known regarding the translational landscape of host and viral proteins. Here, using ribosome profiling in SARS-CoV-2-infected cells, we identify structural elements that regulate viral gene expression, alternative translation initiation events, as well as host responses regulated by mRNA translation. We found that the ribosome density was low within the SARS-CoV-2 frameshifting element but high immediately downstream, which suggests the utilization of a highly efficient ribosomal frameshifting strategy. In SARS-CoV-2-infected cells, although many chemokine, cytokine and interferon stimulated genes were upregulated at the mRNA level, they were not translated efficiently, suggesting a translational block that disarms host innate host responses. Together, these data reveal the key role of mRNA translation in SARS-CoV-2 replication and highlight unique mechanisms for therapeutic development.', 'Maritza Puray-Chavez, Kasyap Tenneti, Hung R. Vuong, Nakyung Lee, Yating Liu, Amjad Horani, Tao Huang, Sean P. Gunsten, James B. Case, Wei Yang, Michael S. Diamond, Steven L. Brody, Joseph Dougherty, and Sebla B. Kutluay', '10.1101/2020.11.03.367516', '2020-11-03')")

#manually input data for finkel. All from the publication
cur.execute("INSERT INTO study_info (study_id, known_as, title, journal, abstract, authors, doi, release_date) VALUES ('SRP260279', 'Finkel et al', 'The coding capacity of SARS-CoV-2', 'Nature', 'Severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2) is the cause of the ongoing coronavirus disease 2019 (COVID-19) pandemic1. To understand the pathogenicity and antigenic potential of SARS-CoV-2 and to develop therapeutic tools, it is essential to profile the full repertoire of its expressed proteins. The current map of SARS-CoV-2 coding capacity is based on computational predictions and relies on homology with other coronaviruses. As the protein complement varies among coronaviruses, especially in regard to the variety of accessory proteins, it is crucial to characterize the specific range of SARS-CoV-2 proteins in an unbiased and open-ended manner. Here, using a suite of ribosome-profiling techniques2,3,4, we present a high-resolution map of coding regions in the SARS-CoV-2 genome, which enables us to accurately quantify the expression of canonical viral open reading frames (ORFs) and to identify 23 unannotated viral ORFs. These ORFs include upstream ORFs that are likely to have a regulatory role, several in-frame internal ORFs within existing ORFs, resulting in N-terminally truncated products, as well as internal out-of-frame ORFs, which generate novel polypeptides. We further show that viral mRNAs are not translated more efficiently than host mRNAs; instead, virus translation dominates host translation because of the high levels of viral transcripts. Our work provides a resource that will form the basis of future functional studies.', 'Yaara Finkel, Orel Mizrahi, Aharon Nachshon, Shira Weingarten-Gabbay, David Morgenstern, Yfat Yahalom-Ronen, Hadas Tamir, Hagit Achdout, Dana Stein, Ofir Israeli, Adi Beth-Din, Sharon Melamed, Shay Weiss, Tomer Israely, Nir Paran, Michal Schwartz & Noam Stern-Ginossar', '10.1038/s41586-020-2739-1', '2020-09-09')")

# populate conditions info

cur.execute("INSERT INTO condition_info (condition, alias, class, info, order_by) VALUES ('sra_run', 'SRA Run', '1', 'Sequence Read Archive Run ID', '10');")
cur.execute("INSERT INTO condition_info (condition, alias, class, info, order_by, value_suffix) VALUES ('seq_type', 'Sequencing Type','1', 'Type of Sequencing Experiment Used to Produce Data', '3', '-Seq');")
cur.execute("INSERT INTO condition_info (condition, alias, class, info, order_by, value_suffix) VALUES ('hpi', 'HPI', '1', 'Hours Post Infection', '5', ' Hours');")
cur.execute("INSERT INTO condition_info (condition, alias, class, info, order_by, value_suffix) VALUES ('moi', 'MOI', '1', 'Multiplicity of Infection', '7', ' MOI');")
cur.execute("INSERT INTO condition_info (condition, alias, class, info, order_by) VALUES ('host_cell', 'Host Cell Type', '1', 'The Cell line that the Study Was Carried Out In', '6');")
cur.execute("INSERT INTO condition_info (condition, alias, class, info, order_by) VALUES ('treatment', 'Ribo-Seq Treatment Type', '1', 'Treatment used to Immobilize Ribosomes', '4');")
cur.execute("INSERT INTO condition_info (condition, alias, class, info, order_by) VALUES ('elongating', 'Elongating Ribosomes', '1', 'Ribosomes Captured During Elongation Phase', '8');")
cur.execute("INSERT INTO condition_info (condition, alias, class, info, order_by) VALUES ('initiating', 'Initiating Ribosomes', '1', 'Ribosomes Captured During Initiation Phase', '9');")
cur.execute("INSERT INTO condition_info (condition, alias, class, info, order_by) VALUES ('study', 'Study', '1', 'The Study From Which the File Came From', '1');")
cur.execute("INSERT INTO condition_info (condition, alias, class, info, order_by) VALUES ('sars_vs_mock', 'SARS Infected vs Mock', '1', 'Whether the Sample Was Control or SARS-CoV2 Infected', '2');")



connection.commit()
connection.close()


    # sra_run VARCHAR PRIMARY KEY,
    # seq_type VARCHAR,
    # hpi VARCHAR,
    # moi VARCHAR,
    # host_cell VARCHAR,
    # treatment VARCHAR,
    # elongating BIT,
    # initiating BIT,
    # study VARCHAR,
    # sars_vs_mock VARCHAR
