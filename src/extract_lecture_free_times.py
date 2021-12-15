#!/usr/bin/env python3

import urllib.request

# URL for the data which is to be crawled and processed
academic_calender_URL = 'https://www.tuwien.at/studium/akademischer-kalender'
statutory_holidays = 'https://www.wien.gv.at/amtshelfer/feiertage/'

def fetch_page(URL_to_be_fetched):
	"""Fetch the source code of a single page.

	This function crawls the page and returns (upon sucessful
	crawl) the source code of the given URL.
	"""

	fetched_page = urllib.request.urlopen(URL_to_be_fetched)
	if (fetched_page.status != 200):
		raise ConnectionError('Cannot fetch source of URL: ' + URL_to_be_fetched)
	else:
		return fetched_page.read()

# crawl the data (fetch the source code of the URLs)
source_of_URL = fetch_page(academic_calender_URL)
print(source_of_URL)

# extract the dates from the crawled pages

# insert the dates in the database (if they are not already in the DB)
