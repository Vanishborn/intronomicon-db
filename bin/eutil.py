import requests

"""components"""
db = 'sra'
retmax = 'retmax=60000'
taxid = 'term=txid6239[Organism]'

"""assemble the esearch URL"""
base = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
url = base + f"esearch.fcgi?db={db}&{retmax}&{taxid}"
print("Retrieving SRA Page IDs from URL:")
print(url)

"""request results"""
response = requests.get(url)

"""check retmax value"""
# TODO
# Might need to use loop
# Update retmax

"""save the returned xml to file"""
with open('./esearch_out.xml', 'w') as file:
    file.write(response.text)

