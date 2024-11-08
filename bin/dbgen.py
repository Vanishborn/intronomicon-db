# generate initial intronomicon.db file and tables using sqlite3

__author__ = "Henry Li"
__version__ = "1.0.0"
__status__ = "Production"


import sqlite3


connection = sqlite3.connect("intronomicon.db")

cursor = connection.cursor()

"""create table commands"""
command_create_table_intron = '''CREATE TABLE IF NOT EXISTS intron(
	intron_ID TEXT PRIMARY KEY,
	exp_ID TEXT,
	tax_ID TEXT,
	chr_ID TEXT,
	strand_dir INTEGER CHECK (strand_dir IN (1, -1)),
	start_pos INTEGER,
	end_pos INTEGER,
	count INTEGER,
	tags TEXT,
	FOREIGN KEY (exp_ID) REFERENCES experiment (exp_ID),
	FOREIGN KEY (tax_ID) REFERENCES organism (tax_ID)
	)'''

command_create_table_experiment = '''CREATE TABLE IF NOT EXISTS experiment(
	exp_ID TEXT PRIMARY KEY,
	exp_title TEXT,
	study_title TEXT,
	attributes TEXT,
	full_info TEXT
	)'''

command_create_table_organism = '''CREATE TABLE IF NOT EXISTS organism(
	tax_ID INTEGER PRIMARY KEY,
	sci_name TEXT
	)'''

command_create_table_runs = '''CREATE TABLE IF NOT EXISTS runs(
	run_ID TEXT PRIMARY KEY,
	exp_ID TEXT,
	bases INTEGER,
	spots INTEGER,
	file_size INTEGER,
	FOREIGN KEY (exp_ID) REFERENCES experiment (exp_ID)
	)'''

"""command execution"""
cursor.execute(command_create_table_intron)
cursor.execute(command_create_table_experiment)
cursor.execute(command_create_table_organism)
cursor.execute(command_create_table_runs)

"""insert values"""
# TODO
# as general usage notes
# cursor.execute('''INSERT INTO {TABLE} VALUES ({COL1.VAL}, {COL2.VAL}, ... )''')

"""get values"""
# TODO
# as general usage notes
# cursor.execute('''SELECT * FROM {TABLE}''')
# query_results = cursor.fetchall()
# print(query_results)

"""commit and close"""
connection.commit()
connection.close()

"""summary"""
print("----DB Genereated----")
