import os
import requests
import shutil
import json
import re

#  given a url, save all captures we want into a directory of that site's name
def save_captures(url):
	all_dates = get_all_dates(url)

	#  make directory (strip out http prefix and ending slash)
	dir_name = re.match(r"^https?://(.*)/?", url).group(1)
	path = "./raw_data/" + dir_name
	os.makedirs(path)

	#  loop through all dates, get the capture, and save in new directory
	for d in all_dates:
		page = get_one_capture(url, d)
		name = path + "/" + d
		new_file = open(os.path.join(path, d), 'w')
		new_file.write(page.encode('ascii', 'ignore'))
		new_file.close()

#  given a url and timestamp, return the page content
def get_one_capture(url, timestamp):
	request_url = "http://web.archive.org/web/" + timestamp + "id_/" + url
	result = requests.get(request_url)
	return result.text

#  given a url, return a list of timestamps
def get_all_dates(url):
	request_url = "http://web.archive.org/cdx/search/cdx?url=" + url + "&matchType=exact&output=json"
	result = requests.get(request_url)
	json_result = json.loads(result.text)
	all_dates = []
	for r in json_result[1:]:
		all_dates.append(str(r[1]))  # have to use str() to get rid of unicode u
	return all_dates