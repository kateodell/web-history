import os
import requests
import shutil
import json
import re
from datetime import datetime

RAW_DATA = "./raw_data/"


#  given a text file, read in list of sites and grab data for each
def process_sites_from_file(filename):
    lines = open(filename).read().splitlines()
    for line in lines:
        print "Getting all captures from", line
        get_and_save_captures(line)


#  given a url, save all captures we want into a directory of that site's name
#  TODO: should the timestamp/capture getting and creation be a method for Site?
def get_and_save_captures(url):
    dates = get_just_desired_dates(url)

    #  don't do anything if there are no dates results
    if not dates:
        print "\n\nTHERE ARE NO RESULTS FOR ", url, "\n\n"
        return

    #  make directory to store files and put into sites table (strip out http prefix and ending slash)
    dir_name = re.match(r"^(https?://)?(.*)/?", url).group(2)
    path = RAW_DATA + dir_name
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        answer = raw_input('There is already a directory for this site. Replace? (y or n)-->')
        if answer == "n":  # don't do anything else if n
            return
        else:               # if y, delete all capture files
            print "deleting existing captures and replacing with new ones."
            delete_files_in_dir(path)

    site = model.add_or_refresh_site(dir_name)

    #  loop through all dates, get the capture, and save in new directory
    for d in dates:
        page = get_one_capture(url, d)
        if page:
            new_file = open(os.path.join(path, d), 'w')
            new_file.write(page)  # TODO: IS this the right thing to do for encoding?!?!
            new_file.close()
            #  add capture to database
            site.add_capture(d, page)


def delete_files_in_dir(path):
    for f in os.listdir(path):
        os.remove(os.path.join(path, f))


#  given a url and timestamp, return the page content
#  TODO: should any of this be part of the Site class?
def get_one_capture(url, timestamp):
    print "Getting capture for timestamp:", timestamp
    request_url = build_request_url(timestamp, url)
    try:
        # print "REQUEST URL IS ", request_url
        result = requests.get(request_url, allow_redirects=False)
        while result.status_code == 301 or result.status_code == 302:  # follow the redirect
            redirect = result.headers.get('Location')
            # print "REDIRECT IS", redirect
            if re.search(r'^/web/', redirect):
                request_url = "http://web.archive.org" + redirect
            elif re.search(r'^http://(www.)?archive\.org/web/', redirect):
                request_url = request_url  # TODO look up proper way to jump to end of if/else
            elif re.search(r'^/.*', redirect):
                request_url = build_request_url(timestamp, url + redirect)
            else:
                request_url = build_request_url(timestamp, redirect)
            result = requests.get(request_url, allow_redirects=False)
        if result.status_code != 200:  # don't save anything except a 200 response
            print "STATUS CODE IS NOT 200. IT IS", result.status_code, "for", request_url, "\n\n"
            return None
        # print "CAPTURE WITH STATUS", result.status_code, "FOR", request_url
        return result.text.encode('ascii', 'ignore')
    except:  # requests.exceptions.ConnectionError:
        print "CONNECTION ERROR, DID NOT CAPTURE", request_url, "\n\n"
        return None


def build_request_url(timestamp, url):
    return "http://web.archive.org/web/" + timestamp + "id_/" + url


#  given a url, return a list of timestamps
def get_just_desired_dates(url):
    request_url = "http://web.archive.org/cdx/search/cdx?url=" + url + "&matchType=exact&output=json"
    result = requests.get(request_url)
    if result.text == "":
        return None
    json_result = json.loads(result.text)
    all_dates = []
    last_captured = "00000000000000"
    for r in json_result[1:]:  # skip first row, since it's the headers
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


## CLEAN-UP functions - below were used to clean up things in the database
##   NOTE: Will need to import model before running these.

def clean_url_no_http():
    for s in model.session.query(model.Site).all():
        new_url = re.match('^https?://(.*)/?$', s.url)
        if new_url:
            s.url = new_url.group(1)
    model.session.commit()


def convert_timestamp_to_datetime():
    for c in model.session.query(model.Capture).all():
        dt = datetime.strptime(c.timestamp, '%Y-%m-%d %H:%M:%S')
        c.captured_on = dt
        print "converted %r to %r" % (c.timestamp, dt)


#  go through queries table and update the site_id column
def update_queries_table_with_site_id():
    for q in model.session.query(model.Query).all():
        if not q.site_id:
            q.site_id = model.session.query(model.Capture).get(q.capture_id).site_id
