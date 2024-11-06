# download srx xmls using eFetch

__author__ = "Henry Li"
__version__ = "0.0.2"
__status__ = "Development"


import os
import requests
import tarfile
import time


base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=sra&id='


def download_file(id, output_directory):
	print(f"Downloading file with PMID {id}")
	url = f"{base_url}{id}&rettype=xml&retmode=text"
	try:
		response = requests.get(url)
		if response.status_code == 200:
			with open(f"{output_directory}/{id}.xml", 'w') as file:
				file.write(response.text)
			return True
		else:
			raise Exception(f"HTTP Error: {response.status_code}")
	except Exception as e:
		print(f"--Download Failed: {e}--")
		with open('efetch_error_log.txt', 'a') as log_file:
			log_file.write(f"{id}\n")
		return False


def retry_failed_downloads(failed_ids, output_directory, retries=2, delay=300):
	for i in range(retries):
		print(f"----Retrying failed downloads, Round {i+1}----")
		new_failed_ids = []
		for id in failed_ids:
			if not download_file(id, output_directory):
				new_failed_ids.append(id)
			time.sleep(2)
		failed_ids = new_failed_ids
		if not failed_ids:
			break
		print(f"----Waiting {delay} seconds before next retry----")
		time.sleep(delay)
	return failed_ids


def append_to_tar_gz(source_dir, id_set, tar_filename):
	mode = "a:gz" if os.path.exists(tar_filename) else "w:gz"
	with tarfile.open(tar_filename, mode) as tar:
		for id in id_set:
			file_name = f'{id}.xml'
			file_path = os.path.join(source_dir, file_name)
			if os.path.exists(file_path):
				tar.add(file_path, arcname=file_name)
				print(f"File {file_name} added to {tar_filename}")


"""remove previous error log, if any"""
if os.path.exists('efetch_error_log.txt'):
	os.remove('efetch_error_log.txt')

"""create download directory"""
output_directory = './downloads'
if not os.path.exists(output_directory):
	os.makedirs(output_directory)

"""read PMID for download"""
with open('./pmid-additions.txt', 'r') as infile:
	todo_set = set([line.strip() for line in infile])
todo_count = len(todo_set)
print(f"----Read {todo_count} files to be downloaded----")

"""downloading"""
failed_ids = []
for id in todo_set:
	if not download_file(id, output_directory):
		failed_ids.append(id)
	time.sleep(2)

"""initial download status report"""
f_count = len(failed_ids)
s_count = todo_count - f_count
print("----Initial download complete----")
print(f"Successful downloads: {s_count}\nFailed downloads: {f_count}")

tar_filename = os.path.join(output_directory, '..', 'sraexppkg.tar.gz')

"""retrying failed attempts"""
if failed_ids:
	print(f"----{f_count} files failed to download----")
	failed_ids = retry_failed_downloads(failed_ids, output_directory)
	f_count = len(failed_ids)
	s_count = todo_count - f_count

	"""create logs"""
	log_directory = os.path.join(output_directory, 'log')
	if not os.path.exists(log_directory):
		os.makedirs(log_directory)
	with open(os.path.join(log_directory, 'efetch_error_log.txt'), 'w') as log_file:
		for id in failed_ids:
			log_file.write(id + '\n')
	success_set = todo_set - set(failed_ids)
	with open(os.path.join(log_directory, 'success.txt'), 'w') as success_file:
		for id in success_set:
			success_file.write(id + '\n')

	"""append newly downloaded files to the tar.gz file"""
	append_to_tar_gz(output_directory, success_set, tar_filename)

	"""additional download status report after retries"""
	print(f"----Download complete after retries----")
	print(f"Successful downloads: {s_count}\nFailed downloads: {f_count}")
	print("Check efetch_error_log.txt for details")
else:
	if os.path.exists('efetch_error_log.txt'):
		os.remove('efetch_error_log.txt')

	"""append newly downloaded files to the tar.gz file"""
	append_to_tar_gz(output_directory, todo_set, tar_filename)

	print("All files successfully downloaded")
