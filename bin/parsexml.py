# parse SraExperimentPackage XML for metadata and SRR

import xml.etree.ElementTree as ET
import json

# dev v0.0.1
# missing some parameters
# to be added
# TODO

'''function to get text from XML elements'''
def get_text(element, default=''):
	return element.text.strip() if element is not None else default


def print_metadata(metadata, indent=0, json_out=False):
	if json_out:
		print(json.dumps(metadata, indent=4))
		return
	spacing = ' ' * indent
	if isinstance(metadata, dict):
		for key, value in metadata.items():
			if isinstance(value, dict) or isinstance(value, list):
				print(f"{spacing}{key}:")
				print_metadata(value, indent + 2)
			else:
				print(f"{spacing}{key}: {value}")
	elif isinstance(metadata, list):
		for item in metadata:
			print_metadata(item, indent)


'''parse XML'''
exp_pkg_tree = ET.parse('SraExperimentPackage.xml')
root = exp_pkg_tree.getroot()


'''extracting all metadata'''
metadata = {}

# General Information
metadata['SRR Number'] = get_text(root.find('.//RUN/IDENTIFIERS/PRIMARY_ID'))
metadata['Study Title'] = get_text(
	root.find('.//STUDY/DESCRIPTOR/STUDY_TITLE'))
metadata['Organism'] = get_text(root.find('.//SAMPLE_NAME/SCIENTIFIC_NAME'))

# Experiment Information
experiment = root.find('.//EXPERIMENT')
metadata['Experiment Accession'] = experiment.attrib.get('accession', '')
metadata['Experiment Alias'] = experiment.attrib.get('alias', '')
metadata['Experiment Title'] = get_text(experiment.find('TITLE'))
metadata['Experiment Primary ID'] = get_text(
	experiment.find('.//IDENTIFIERS/PRIMARY_ID'))

# Study Reference Information
study_ref = root.find('.//STUDY_REF')
metadata['Study Reference Accession'] = study_ref.attrib.get('accession', '')
metadata['Study Reference Primary ID'] = get_text(
	study_ref.find('.//IDENTIFIERS/PRIMARY_ID'))

# Design Information
design = root.find('.//DESIGN')
metadata['Design Description'] = get_text(design.find('DESIGN_DESCRIPTION'))

# Sample Descriptor Information
sample_descriptor = design.find('SAMPLE_DESCRIPTOR')
metadata['Sample Descriptor Accession'] = sample_descriptor.attrib.get(
	'accession', '')
metadata['Sample Descriptor Primary ID'] = get_text(
	sample_descriptor.find('.//IDENTIFIERS/PRIMARY_ID'))

# Library Descriptor Information
library_descriptor = design.find('LIBRARY_DESCRIPTOR')
metadata['Library Name'] = get_text(library_descriptor.find('LIBRARY_NAME'))
metadata['Library Strategy'] = get_text(
	library_descriptor.find('LIBRARY_STRATEGY'))
metadata['Library Source'] = get_text(
	library_descriptor.find('LIBRARY_SOURCE'))
metadata['Library Selection'] = get_text(
	library_descriptor.find('LIBRARY_SELECTION'))

# Platform Information
platform = root.find('.//PLATFORM/ILLUMINA')
metadata['Instrument Model'] = get_text(platform.find('INSTRUMENT_MODEL'))

# Submission Information
submission = root.find('.//SUBMISSION')
metadata['Submission ID'] = get_text(
	submission.find('.//IDENTIFIERS/PRIMARY_ID'))
metadata['Submission Alias'] = submission.attrib.get('alias', '')
metadata['Center Name'] = submission.attrib.get('center_name', '')
metadata['Lab Name'] = submission.attrib.get('lab_name', '')

# Submitter Information
metadata['Submitter ID'] = get_text(submission.find('.//SUBMITTER_ID'))

# Organization Information
organization = root.find('.//Organization')
metadata['Organization Name'] = get_text(organization.find('Name'))
metadata['Organization URL'] = organization.attrib.get('url', '')
address = organization.find('Address')
metadata['Address'] = {
	'Postal Code': address.attrib.get('postal_code', ''),
	'Department': get_text(address.find('Department')),
	'Institution': get_text(address.find('Institution')),
	'Street': get_text(address.find('Street')),
	'City': get_text(address.find('City')),
	'State': get_text(address.find('Sub')),
	'Country': get_text(address.find('Country'))
}

# Contact Information
contact = organization.find('.//Contact')
metadata['Contact Name'] = f"{get_text(contact.find('Name/First'))} {get_text(
	contact.find('Name/Middle'))} {get_text(contact.find('Name/Last'))}".strip()
metadata['Email'] = contact.attrib.get('email', '')

# Study Metadata
study = root.find('.//STUDY')
metadata['Study Abstract'] = get_text(
	study.find('.//DESCRIPTOR/STUDY_ABSTRACT'))
metadata['Study Type'] = study.find(
	'.//DESCRIPTOR/STUDY_TYPE').attrib.get('existing_study_type', '')
metadata['Study Primary ID'] = get_text(
	study.find('.//IDENTIFIERS/PRIMARY_ID'))
metadata['Study External ID'] = get_text(
	study.find('.//IDENTIFIERS/EXTERNAL_ID'))

# Pool Information
metadata['Pool Members'] = []
for member in root.findall('.//Pool/Member'):
	info = {
		'Member Name': member.attrib.get('member_name', ''),
		'Accession': member.attrib.get('accession', ''),
		'Sample Name': member.attrib.get('sample_name', ''),
		'Spots': member.attrib.get('spots', ''),
		'Bases': member.attrib.get('bases', ''),
		'Tax ID': member.attrib.get('tax_id', ''),
		'Organism': member.attrib.get('organism', ''),
		'Primary ID': get_text(member.find('.//IDENTIFIERS/PRIMARY_ID')),
		'External ID': get_text(member.find('.//IDENTIFIERS/EXTERNAL_ID'))
	}
	if info in metadata['Pool Members']:
		continue
	metadata['Pool Members'].append(info)

# Run Set Information
run_set = root.find('.//RUN_SET')
metadata['Run Set'] = {
	'Runs': run_set.attrib.get('runs', ''),
	'Total Bases': run_set.attrib.get('bases', ''),
	'Total Spots': run_set.attrib.get('spots', ''),
	'Bytes': run_set.attrib.get('bytes', '')
}

# Run Information
run = run_set.find('.//RUN')
metadata['Run'] = {
	'Accession': run.attrib.get('accession', ''),
	'Alias': run.attrib.get('alias', ''),
	'Total Spots': run.attrib.get('total_spots', ''),
	'Total Bases': run.attrib.get('total_bases', ''),
	'Size': run.attrib.get('size', ''),
	'Load Done': run.attrib.get('load_done', ''),
	'Published Date': run.attrib.get('published', ''),
	'Is Public': run.attrib.get('is_public', ''),
	'Cluster Name': run.attrib.get('cluster_name', ''),
	'Has Tax Analysis': run.attrib.get('has_taxanalysis', ''),
	'Static Data Available': run.attrib.get('static_data_available', '')
}

# Experiment Reference Information
experiment_ref = run.find('.//EXPERIMENT_REF')
metadata['Experiment Reference'] = {
	'Accession': experiment_ref.attrib.get('accession', ''),
	'Submitter ID': get_text(experiment_ref.find('.//IDENTIFIERS/SUBMITTER_ID'))
}

# SRA Files Information
metadata['SRA Files'] = []
for sra_file in run.findall('.//SRAFile'):
	sra_file_info = {
		'Filename': sra_file.attrib.get('filename', ''),
		'Size': sra_file.attrib.get('size', ''),
		'Date': sra_file.attrib.get('date', ''),
		'MD5': sra_file.attrib.get('md5', ''),
		'Version': sra_file.attrib.get('version', ''),
		'Semantic Name': sra_file.attrib.get('semantic_name', ''),
		'Supertype': sra_file.attrib.get('supertype', ''),
		'SRAToolkit': sra_file.attrib.get('sratoolkit', '')
	}
	sra_file_info['Alternatives'] = []
	for alt in sra_file.findall('.//Alternatives'):
		sra_file_info['Alternatives'].append({
			'URL': alt.attrib.get('url', ''),
			'Free Egress': alt.attrib.get('free_egress', ''),
			'Access Type': alt.attrib.get('access_type', ''),
			'Organization': alt.attrib.get('org', '')
		})
	metadata['SRA Files'].append(sra_file_info)

# Cloud Files Information
metadata['Cloud Files'] = []
for cloud_file in run.findall('.//CloudFiles/CloudFile'):
	metadata['Cloud Files'].append({
		'File Type': cloud_file.attrib.get('filetype', ''),
		'Provider': cloud_file.attrib.get('provider', ''),
		'Location': cloud_file.attrib.get('location', '')
	})

# Read Statistics
read_stats = run.find('.//Statistics')
metadata['Read Statistics'] = {
	'Number of Reads': read_stats.attrib.get('nreads', ''),
	'Number of Spots': read_stats.attrib.get('nspots', '')
}
read = read_stats.find('Read')
metadata['Read Statistics']['Read'] = {
	'Index': read.attrib.get('index', ''),
	'Count': read.attrib.get('count', ''),
	'Average': read.attrib.get('average', ''),
	'Stdev': read.attrib.get('stdev', '')
}

# Database Information
metadata['Databases'] = []
for database in run.findall('.//Databases/Database'):
	db_info = {'Tables': []}
	for table in database.findall('.//Table'):
		table_stats = table.find('.//Statistics')
		db_info['Tables'].append({
			'Name': table.attrib.get('name', ''),
			'Rows': table_stats.find('.//Rows').attrib.get('count', ''),
			'Elements': table_stats.find('.//Elements').attrib.get('count', '')
		})
	metadata['Databases'].append(db_info)

# Base Information
bases = run.find('.//Bases')
metadata['Bases'] = {
	'CS Native': bases.attrib.get('cs_native', ''),
	'Count': bases.attrib.get('count', '')
}
metadata['Bases']['Base Counts'] = []
for base in bases.findall('Base'):
	metadata['Bases']['Base Counts'].append({
		'Value': base.attrib.get('value', ''),
		'Count': base.attrib.get('count', '')
	})

# Print the entire metadata dictionary
# In JSON
print_metadata(metadata, 0, json_out=True)

# TODO
# Instead of printing, pick and format relevant info
# 