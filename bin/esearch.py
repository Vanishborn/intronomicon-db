import requests
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

"""parse the initial response for Count"""
esearch_tree = ET.fromstring(response.text)
count = get_text(esearch_tree.find('Count'))
print(f"There are {count} total results available")

"""full request using the count as retmax"""
url = base + f"esearch.fcgi?db={db}&retmax={count}&{taxid}"
print(f"Retrieving {count} SRA Page IDs from URL:")
print(url)
response = requests.get(url)

"""save the returned xml to file"""
with open('./esearch_out.xml', 'w') as file:
	file.write(response.text)
