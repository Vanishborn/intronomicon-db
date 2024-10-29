# parse SraExperimentPackage XML for metadata

import json
import requests
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

	# Parse Pool Information
	metadata['Pool'] = []
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

	return metadata


def parse_sep_xml(xml_text):
	root = ET.fromstring(xml_text)
	return parse_experiment_package(root.find('EXPERIMENT_PACKAGE'))


"""components"""
db = 'sra'
id = '427'
base = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'

"""assemble the efetch URL"""
url = base + f"efetch.fcgi?db={db}&id={id}"
print(f"Retrieving SRA Experiment Package using Page ID {id} from URL:")
print(url)
response = requests.get(url)
response.encoding = 'utf-8'

'''parse XML'''
metadata = parse_sep_xml(response.text)
print(json.dumps(metadata, ensure_ascii=False, indent=4))

'''output to json file'''
with open(f'./metadata{id}.json', 'w', encoding="utf-8") as outfile:
	json.dump(metadata, outfile, ensure_ascii=False, indent=4)

