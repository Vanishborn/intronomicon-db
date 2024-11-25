# parse SraExperimentPackage XML for metadata

__author__ = "Henry Li"
__version__ = "1.0.0"
__status__ = "Production"


import json
import os
import sqlite3
import xml.etree.ElementTree as ET


def get_text(element):
	if element is None or element.text is None:
		return ''
	return element.text.strip()


def parse_experiment_package(root):
	metadata = {}

	# Parse Experiment
	experiment = root.find('EXPERIMENT')
	if experiment is not None:
		metadata['Experiment'] = {
			'Accession': experiment.attrib.get('accession', ''),
			'Alias': experiment.attrib.get('alias', ''),
			'Primary ID': get_text(experiment.find('IDENTIFIERS/PRIMARY_ID')),
			'Title': get_text(experiment.find('TITLE')).encode('latin1').decode('utf-8'),
			'Study Reference Accession': experiment.find('STUDY_REF').attrib.get('accession', ''),
			'Design Description': get_text(experiment.find('DESIGN/DESIGN_DESCRIPTION')),
			'Sample Descriptor Accession': experiment.find('DESIGN/SAMPLE_DESCRIPTOR').attrib.get('accession', ''),
			'Library Name': get_text(experiment.find('DESIGN/LIBRARY_DESCRIPTOR/LIBRARY_NAME')),
			'Library Strategy': get_text(experiment.find('DESIGN/LIBRARY_DESCRIPTOR/LIBRARY_STRATEGY')),
			'Library Source': get_text(experiment.find('DESIGN/LIBRARY_DESCRIPTOR/LIBRARY_SOURCE')),
			'Library Selection': get_text(experiment.find('DESIGN/LIBRARY_DESCRIPTOR/LIBRARY_SELECTION')),
			'Instrument Model': get_text(experiment.find('PLATFORM/ILLUMINA/INSTRUMENT_MODEL'))
		}
	else:
		return None

	# Parse Submission
	submission = root.find('SUBMISSION')
	if submission is not None:
		metadata['Submission'] = {
			'Accession': submission.attrib.get('accession', ''),
			'Alias': submission.attrib.get('alias', ''),
			'Center Name': submission.attrib.get('center_name', ''),
			'Lab Name': submission.attrib.get('lab_name', ''),
			'Primary ID': get_text(submission.find('IDENTIFIERS/PRIMARY_ID')),
			'Submitter ID': get_text(submission.find('IDENTIFIERS/SUBMITTER_ID'))
		}
	else:
		return None

	# Parse Study
	study = root.find('STUDY')
	if study is not None:
		metadata['Study'] = {
			'Accession': study.attrib.get('accession', ''),
			'Alias': study.attrib.get('alias', ''),
			'Center Name': study.attrib.get('center_name', ''),
			'Primary ID': get_text(study.find('IDENTIFIERS/PRIMARY_ID')),
			'External ID': get_text(study.find('IDENTIFIERS/EXTERNAL_ID')),
			'Title': get_text(study.find('DESCRIPTOR/STUDY_TITLE')),
			'Type': study.find('DESCRIPTOR/STUDY_TYPE').attrib.get('existing_study_type', ''),
			'Abstract': get_text(study.find('DESCRIPTOR/STUDY_ABSTRACT'))
		}
	else:
		return None

	# Parse Sample
	sample = root.find('SAMPLE')
	if sample is not None:
		metadata['Sample'] = {
			'Accession': sample.attrib.get('accession', ''),
			'Alias': sample.attrib.get('alias', ''),
			'Primary ID': get_text(sample.find('IDENTIFIERS/PRIMARY_ID')),
			'External ID': get_text(sample.find('IDENTIFIERS/EXTERNAL_ID')),
			'Scientific Name': get_text(sample.find('SAMPLE_NAME/SCIENTIFIC_NAME')),
			'Taxon ID': get_text(sample.find('SAMPLE_NAME/TAXON_ID')),
			'Description': get_text(sample.find('DESCRIPTION')),
			'Attributes': {}
		}
		attributes_dict = {}
		for attribute in sample.findall('SAMPLE_ATTRIBUTES/SAMPLE_ATTRIBUTE'):
			tag = get_text(attribute.find('TAG'))
			value = get_text(attribute.find('VALUE'))
			if tag:
				attributes_dict[tag] = value
		metadata['Sample']['Attributes'] = attributes_dict
	else:
		return None

	# Parse Pool Information
	metadata['Pool'] = []
	try:
		for member in root.findall('Pool/Member'):
			metadata['Pool'].append({
				'Member Name': member.attrib.get('member_name', ''),
				'Accession': member.attrib.get('accession', ''),
				'Sample Name': member.attrib.get('sample_name', ''),
				'Spots': member.attrib.get('spots', ''),
				'Bases': member.attrib.get('bases', ''),
				'Tax ID': member.attrib.get('tax_id', ''),
				'Organism': member.attrib.get('organism', '')
			})
	except:
		return None

	# Parse Run Set Information
	run_set = root.find('RUN_SET')
	if run_set is not None:
		metadata['Run Set'] = {
			'Runs': run_set.attrib.get('runs', ''),
			'Bases': run_set.attrib.get('bases', ''),
			'Total Spots': run_set.attrib.get('spots', ''),
			'Total Bytes': run_set.attrib.get('bytes', ''),
			'Run Details': []
		}
		for run in run_set.findall('RUN'):
			run_info = {
				'Run Accession Number': run.attrib.get('accession', ''),
				'Filename': run.attrib.get('alias', ''),
				'Spots': run.attrib.get('total_spots', ''),
				'Bases': run.attrib.get('total_bases', ''),
				'Size': run.attrib.get('size', '')
			}
			metadata['Run Set']['Run Details'].append(run_info)
	else:
		return None

	return metadata


def parse_sep_xml(xml_text):
	root = ET.fromstring(xml_text)
	return parse_experiment_package(root.find('EXPERIMENT_PACKAGE'))


def insert_metadata_to_db(db_directory, metadata):
	connection = sqlite3.connect(db_directory)
	cursor = connection.cursor()

	'''insert into experiment table'''
	exp_data = metadata['Experiment']
	exp_id = exp_data['Accession']
	exp_title = exp_data['Title']
	study_title = metadata['Study']['Title']
	attributes = json.dumps(metadata['Sample']['Attributes']) if metadata['Sample']['Attributes'] else ''
	full_info = json.dumps(metadata)
	cursor.execute('''INSERT OR IGNORE INTO experiment (exp_ID, exp_title, study_title, attributes, full_info) VALUES (?, ?, ?, ?, ?)''', (exp_id, exp_title, study_title, attributes, full_info))

	'''insert into organism table'''
	tax_id = metadata['Sample']['Taxon ID']
	sci_name = metadata['Sample']['Scientific Name']
	cursor.execute('''INSERT OR IGNORE INTO organism (tax_ID, sci_name) VALUES (?, ?)''', (tax_id, sci_name))

	'''insert into runs table'''
	for run in metadata['Run Set']['Run Details']:
		run_id = run['Run Accession Number']
		bases = int(run['Bases']) if run['Bases'] else 0
		spots = int(run['Spots']) if run['Spots'] else 0
		file_size = int(run['Size']) if run['Size'] else 0
		cursor.execute('''INSERT OR IGNORE INTO runs (run_ID, exp_ID, bases, spots, file_size) VALUES (?, ?, ?, ?, ?)''', (run_id, exp_id, bases, spots, file_size))

	connection.commit()
	connection.close()


"""path configs"""
# TODO
output_directory = '/PATH/TO/XML/DOWNLOADS'
additions_directory = './pmid-additions.txt'
db_directory = './intronomicon.db'

"""get pmids"""
with open(additions_directory, 'r') as infile:
	pmids = [line.strip() for line in infile]

f_count = 0

"""parse xml and insert to db"""
for pmid in pmids:
	xml_path = os.path.join(output_directory, f"{pmid}.xml")
	if os.path.exists(xml_path):
		print(f"Parsing XML file: {xml_path}")
		with open(xml_path, 'r', encoding='utf-8') as xml_file:
			xml_text = xml_file.read()
		metadata = parse_sep_xml(xml_text)
		if metadata is None:
			with open('./error_log_populate_db.txt', 'a') as error_log_file:
				error_log_file.write(f"{pmid}.xml\n")
			f_count += 1
			continue

		# Print json to stdout
		"""print(json.dumps(metadata, ensure_ascii=False, indent=4))"""

		# Output to json file
		"""
		json_directory = f'./metadata{pmid}.json'
		with open(json_directory, 'w', encoding="utf-8") as json_outfile:
			json.dump(metadata, json_outfile, ensure_ascii=False, indent=4)
		"""

		# Insert metadata to db
		insert_metadata_to_db(db_directory, metadata)
	else:
		print(f"File not found: {xml_path}")

"""summary"""
print("----Processing complete----")
print(f"Successful entries: {len(pmids)-f_count}\nFailed entries: {f_count}")
print("Please check error_log_populate_db.txt for details")
