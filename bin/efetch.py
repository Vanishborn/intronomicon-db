# download srx xmls using eFetch

__author__ = "Henry Li"
__version__ = "0.0.2"
__status__ = "Development"


import requests
import time
import os


base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=sra&id='


def download_file(id, output_directory):
	url = f"{base_url}{id}&rettype=xml&retmode=text"
	response = requests.get(url)
	if response.status_code == 200:
		with open(f"{output_directory}/{id}.xml", 'w') as file:
			file.write(response.text)
		return True
	else:
		with open('efetch_error_log.txt', 'a') as log_file:
			log_file.write(f"{id}\n")
		return False


with open('./pmid-additions.txt', 'r') as infile:
	ids = [line.strip() for line in infile]

output_directory = './downloads'

if not os.path.exists(output_directory):
	os.makedirs(output_directory)

s_count = 0
f_count = 0

for id in ids:
	if download_file(id, output_directory):
		s_count += 1
	else:
		f_count += 1
	time.sleep(2)

print("Download complete")
print(f"Successful downloads: {s_count}\nFailed downloads: {f_count}")
print("Check error log for failed PMID retrievals")
