# generate initial intronomicon.db file and tables using sqlite3

# dev v0.0.1
# table content subject to change
# TODO
# finally settle on the info to keep from exp. package xml

import sqlite3

connection = sqlite3.connect("intronomicon.db")

cursor = connection.cursor()

'''create table commands'''
command_create_table_intron = '''CREATE TABLE IF NOT EXISTS intron(
	intron_ID TEXT PRIMARY KEY,
	experiment_ID TEXT,
	organism_ID TEXT,
	chromosome_ID TEXT,
	strand_direction INTEGER NOT NULL CHECK (strand_direction IN (1, -1)),
	start_pos INTEGER,
	end_pos INTEGER,
	count INTEGER,
	tags TEXT,
	FOREIGN KEY (experiment_ID) REFERENCES experiment (experiment_ID),
	FOREIGN KEY (organism_ID) REFERENCES organism (organism_ID)
	)'''

command_create_table_experiment = '''CREATE TABLE IF NOT EXISTS experiment(
	experiment_ID TEXT PRIMARY KEY,
	experiment_name TEXT,
	experiment_type_ID TEXT,
	SRX_page_ID INTEGER,
	genotype TEXT,
	lifecycle TEXT,
	tissue TEXT,
	environment TEXT,
	FOREIGN KEY (experiment_type_ID) REFERENCES experiment_type (experiment_type_ID),
	FOREIGN KEY (tissue) REFERENCES tissues (tissue_ID),
	FOREIGN KEY (environment) REFERENCES environment (environment_ID)
	)'''

command_create_table_organism = '''CREATE TABLE IF NOT EXISTS organism(
	organism_ID INTEGER PRIMARY KEY,
	organism_name TEXT
	)'''

command_create_table_tissue = '''CREATE TABLE IF NOT EXISTS tissue(
	tissue_ID TEXT PRIMARY KEY,
	tissue_name TEXT
	)'''

command_create_table_environment = '''CREATE TABLE IF NOT EXISTS environment(
	environment_ID TEXT PRIMARY KEY,
	temp REAL,
	chemical TEXT,
	external TEXT
	)'''

command_create_table_experiment_type = '''CREATE TABLE IF NOT EXISTS experiment_type(
	experiment_type_ID TEXT PRIMARY KEY,
	experiment_type_desc TEXT
	)'''

'''command execution'''
cursor.execute(command_create_table_intron)
cursor.execute(command_create_table_experiment)
cursor.execute(command_create_table_organism)
cursor.execute(command_create_table_tissue)
cursor.execute(command_create_table_environment)
cursor.execute(command_create_table_experiment_type)

'''insert values'''
# TODO
# or just as general notes
# cursor.execute('''INSERT INTO {TABLE} VALUES ({COL1.VAL}, {COL2.VAL}, ... )''')

'''get values'''
# TODO
# or just as general notes
# cursor.execute('''SELECT * FROM {TABLE}''')
# query_results = cursor.fetchall()
# print(query_results)
