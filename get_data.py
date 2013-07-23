import os
import requests
import shutil
import json
import re

RAW_DATA = "./raw_data/"


#  given a text file, read in list of sites and grab data for each
def process_sites_from_file(filename):
    lines = open(filename).read().splitlines()
    for line in lines:
        print "Getting all captures from", line
        save_captures(line)


#  given a url, save all captures we want into a directory of that site's name
def save_captures(url):
    dates = get_just_desired_dates(url)

    #  make directory (strip out http prefix and ending slash)
    dir_name = re.match(r"^(https?://)?(.*)/?", url).group(2)
    path = RAW_DATA + dir_name
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        print "There is already a directory for this site. Replace? (y or n)"
        answer = raw_input('-->')
        if answer == "n":  # don't do anything else if n
            return
        else:               # if y, delete all capture files
            print "deleting existing captures and replacing with new ones."
            delete_files_in_dir(path)

    #  loop through all dates, get the capture, and save in new directory
    for d in dates:
        page = get_one_capture(url, d)
        new_file = open(os.path.join(path, d), 'w')
        new_file.write(page.encode('ascii', 'ignore'))  # TODO: IS this the right thing to do for encoding?!?!
        new_file.close()


def delete_files_in_dir(path):
    for f in os.listdir(path):
        os.remove(os.path.join(path, f))


#  given a url and timestamp, return the page content
def get_one_capture(url, timestamp):
    print "Getting capture for timestamp:", timestamp
    request_url = "http://web.archive.org/web/" + timestamp + "id_/" + url
    result = requests.get(request_url)
    return result.text


#  given a url, return a list of timestamps
def get_just_desired_dates(url):
    request_url = "http://web.archive.org/cdx/search/cdx?url=" + url + "&matchType=exact&output=json"
    result = requests.get(request_url)
    json_result = json.loads(result.text)
    all_dates = []
    last_captured = "00000000000000"
    for r in json_result[1:]:
        if check_should_capture(r[1], last_captured):
            last_captured = r[1]
            all_dates.append(str(r[1]))  # have to use str() to get rid of unicode u
    return all_dates


def check_should_capture(new_date, last_date):
    new_year = int(new_date[0:4])
    new_month = int(new_date[4:6])
    last_year = int(last_date[0:4])
    last_month = int(last_date[4:6])

    diff_months = (new_year - last_year)*12 + new_month - last_month

    return diff_months >= 3


#  given a url, return a list of timestamps
def get_all_dates(url):
    request_url = "http://web.archive.org/cdx/search/cdx?url=" + url + "&matchType=exact&output=json"
    result = requests.get(request_url)
    json_result = json.loads(result.text)
    all_dates = []
    for r in json_result[1:]:
        all_dates.append(str(r[1]))  # have to use str() to get rid of unicode u
    return all_dates