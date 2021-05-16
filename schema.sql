DROP TABLE IF EXISTS study_info;

CREATE TABLE study_info (
    study_id VARCHAR PRIMARY KEY,
    known_as VARCHAR,
    title TEXT NOT NULL,
    journal VARCHAR,
    abstract TEXT NOT NULL,
    authors TEXT NOT NULL,
    doi VARCHAR,
    release_date VARCHAR
);

DROP TABLE IF EXISTS conditions;

CREATE TABLE conditions (
    sra_run VARCHAR PRIMARY KEY,
    seq_type VARCHAR,
    hpi VARCHAR,
    moi VARCHAR,
    host_cell VARCHAR,
    treatment VARCHAR,
    elongating BIT,
    initiating BIT,
    study VARCHAR,
    sars_vs_mock VARCHAR, 
    trips_id VARCHAR

);


DROP TABLE IF EXISTS condition_info;

CREATE TABLE condition_info (
    condition VARCHAR PRIMARY KEY,
    alias VARCHAR,
    class VARCHAR,
    info VARCHAR,
    order_by VARCHAR,
    value_suffix VARCHAR
);   
