# get a list of PMIDs filtered by keys using eSearch

__author__ = "Henry Li"
__version__ = "0.0.3"
__status__ = "Development"


import os
import requests
import sys
import time
import xml.etree.ElementTree as ET


"""function to get text from XML elements"""
def get_text(element, default=''):
	return element.text.strip() if element is not None else default


"""function to load IDs from file"""
def load_ids(filename):
	if os.path.exists(filename):
		with open(filename, 'r') as file:
			return set(line.strip() for line in file)
	return set()


"""components"""
db = 'sra'
taxid = 'term=txid6239[Organism]'
base = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'

"""assemble the esearch URL"""
url = base + f"esearch.fcgi?db={db}&{taxid}"
print("Retrieving temporary SRA Page IDs from URL:")
print(url)
response = requests.get(url)
response.encoding = 'utf-8'

"""parse the initial response for Count"""
try:
	esearch_tree = ET.fromstring(response.text)
except:
	sys.exit("NIH server error, please try again later")
count = get_text(esearch_tree.find('Count'))
print(f"There are {count} total results available")

"""wait to avoid ip ban"""
sleep_time = 1
print(f"Delaying {sleep_time} seconds to avoid IP ban")
time.sleep(sleep_time)

"""full request using the count as retmax"""
url = base + f"esearch.fcgi?db={db}&retmax={count}&{taxid}"
print(f"Retrieving {count} SRA Page IDs from URL:")
print(url)
response = requests.get(url)
response.encoding = 'utf-8'

"""save the returned xml to file""" 
xml_file = './pmid-esearch-returns.xml'
with open(xml_file, 'w') as file: 
	file.write(response.text)

"""extract all IDs from the IdList"""
try:
	esearch_tree = ET.fromstring(response.text)
except:
	sys.exit("NIH server error, please try again later")
ids = esearch_tree.findall('./IdList/Id')
new_id_list = [get_text(id) for id in ids]
new_ids_set = set(new_id_list)

"""load IDs from last search"""
ids_file = './pmid-new.txt'
ids_set = load_ids(ids_file)

"""identify new IDs"""
added_ids_set = new_ids_set - ids_set

if added_ids_set:
	print(f"Found {len(added_ids_set)} new IDs")

	"""save added IDs to pmid-additions.txt"""
	additions_file = './pmid-additions.txt'
	with open(additions_file, 'w') as file:
		for id in added_ids_set:
			file.write(id + '\n')

	"""backup old pmid-new.txt to pmid-last.txt"""
	"""if not first time running"""
	if os.path.exists(ids_file):
		old_ids_file = './pmid-last.txt'
		with open(ids_file, 'r') as src_file:
			with open(old_ids_file, 'w') as dest_file:
					for line in src_file:
						dest_file.write(line)

	"""overwrite all IDs to pmid-new.txt"""
	with open(ids_file, 'w') as file:
		for id in new_id_list:
			file.write(id + '\n')
	print("----eSearch complete, PMIDs saved----")
else:
	sys.exit("No new PMID found, exiting")
