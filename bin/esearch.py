import requests
import sys
import time
import xml.etree.ElementTree as ET


"""function to get text from XML elements"""
def get_text(element, default=''):
	return element.text.strip() if element is not None else default

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
	sys.exit("Server error, please try again later")
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

"""extract all IDs from the IdList"""
try:
	esearch_tree = ET.fromstring(response.text)
except:
	sys.exit("Server error, please try again later")
ids = esearch_tree.findall('./IdList/Id')
id_list = [get_text(id) for id in ids]

"""save the returned xml to file"""
with open('./esearch_out.xml', 'w') as file:
	file.write(response.text)

"""save the returned ids to a text file""" 
with open('./esearch_out.txt', 'w') as file: 
	for id in id_list: 
		file.write(id + '\n')

print("----eSearch complete, IDs saved----")
