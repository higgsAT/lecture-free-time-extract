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

	# get the source of the page using urllib
	fetched_page = urllib.request.urlopen(URL_to_be_fetched)

	# check if the crawl was successful (via the HTTP response)
	if (fetched_page.status != 200):
		raise ConnectionError('Cannot fetch source of URL: ' + URL_to_be_fetched)
	else:
		return fetched_page.read()

"""
Below are the two function which extract a list of dates
corresponding to the dates at which the university is
closed. The date formatting is JJJJ.MM.DD, e.g., 2019-02-14.
Both functions are URL-sensitive, i.e., when the crawled URL
changes the corresponding function must be adapted.
"""

def extract_statutory_holidays(source_of_URL):
	# change the fetched data from byte to str
	encoding = 'latin-1'
	source_str_data = str(source_of_URL, encoding)

	"""
	Cut the string to contain only the relevant information.
	The two cut points depend on a (unique) subset of the source.
	The cut string containing the relevant source code is stored
	in the variable 'cut_string'.
	"""
	cut_pos1 = source_str_data.find('editableDocument')
	cut_pos2 = source_str_data.find('bde-stx-wrapper')
	cut_string = source_str_data[cut_pos1:cut_pos2]

	"""
	extract the dates and information from the URL subset
	data. Each single extraction event is enclosed in between:
	'<li><span>Neujahr: Freitag, 1. Jänner 2021</span></li>',
	which is used to extract the information.
	"""
	search_string1 = '<li><span>'
	search_string2 = '</span>'

	"""
	Skip a certain amount of elements from the extractions as
	defined by the variable 'skip_entries'. This depends on the
	crawled data.
	"""
	skip_entries = 3
	skip_pos = 0

	return_event_descr = []
	return_event_date = []

	while len(cut_string) > 100:
		cut_pos3 = cut_string.find(search_string1)
		cut_pos4 = cut_string.find(search_string2)

		if skip_pos >= skip_entries:
			event_extract = cut_string[cut_pos3 + len(search_string1):cut_pos4]
			event_divider = ': '
			pos_event_divider = event_extract.find(event_divider)
			event_description = event_extract[:pos_event_divider]
			event_date = event_extract[pos_event_divider + len(event_divider):]

			"""
			Convert the event_date (e.g. 'Donnerstag, 26. Oktober 2023')
			into a DB format like '2023-10-04'.
			"""
			day = event_date[event_date.find(',') + 2:event_date.find('.')]
			month = event_date[event_date.find('.') + 2:-5]
			year = event_date[-4:]

			# use a dictionary to convert the months (Dezember -> 12, etc.)
			dict_months = {
				'Jänner': '01',
				'Februar': '02',
				'März': '03',
				'April': '04',
				'Mai': '05',
				'Juni': '06',
				'Juli': '07',
				'August': '08',
				'September': '09',
				'Oktober': '10',
				'November': '11',
				'Dezember': '12'
			}

			extracted_formatted_date = (
				year + '-' + dict_months[month] +
				'-' + '%02d' % (int(day),)
			)

			# append the found data to the arrays
			return_event_descr.append(event_description)
			return_event_date.append(extracted_formatted_date)

		skip_pos += 1

		# remove the found information (and redo the search)
		cut_string = cut_string[cut_pos4 + len(search_string2):]

		"""
		raise an error in case the number of events does not match
		the number of extracted dates
		"""
		if len(return_event_descr) != len(return_event_date):
			raise IndexError('Number of extracted event descriptions (' +
				str(len(return_event_descr)) + ') != number of event dates (' +
				str(len(return_event_date)) + ')'
			)

	# return the data through the function
	return return_event_descr, return_event_date



## crawl the data (fetch the source code of the URLs) ##
statutory_holidays_source = fetch_page(statutory_holidays)

## extract the dates from the crawled pages ##
return_event_descr, return_event_date = extract_statutory_holidays(
	statutory_holidays_source
)

# print the fetched and extracted data
for i in range(len(return_event_descr)):
	print(return_event_descr[i] + ' | ' + return_event_date[i])

## insert the dates in the database (if they are not already in the DB) ##
