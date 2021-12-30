#!/usr/bin/env python3

import urllib.request
import datetime

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
closed. The (desired DB-)date formatting is JJJJ-MM-DD, e.g., 2019-02-14.
Both functions are URL-sensitive, i.e., when the crawled URL
changes the corresponding function must be adapted.
"""

def extract_statutory_holidays(source_of_URL):
	"""Fetch the statutory holidays from an URL and return the extracted data.

	Whenever the URL (source_of_URL) changes, this function must be adapted.
	First the function fetches the source code of the URL and the resulting
	string is cut at certain spots (defined by cut_pos1 and cut_pos2). Then
	the statutory holidays (incl. its description) are extracted, stored and
	returned via a list (return_event_descr and return_event_date).
	"""

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

	# process the string until an arbitrary length (100) of it is reached
	while len(cut_string) > 100:
		cut_pos3 = cut_string.find(search_string1)
		cut_pos4 = cut_string.find(search_string2)

		if skip_pos >= skip_entries:
			# extract the event description and the date
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


def extract_academic_calendar(source_of_URL):
	"""Fetch the academic calendar from an URL and return the extracted data.

	Whenever the URL (source_of_URL) changes, this function must be adapted.
	First the function fetches the source code of the URL and the resulting
	string is cut at certain spots (defined by cut_pos1 and cut_pos2). Then
	the academic calendar (incl. its description) are extracted, stored and
	returned via a list (return_event_descr and return_event_date).
	"""

	def parse_single_date(event_string):
		"""Extract/Convert a single date event.

		This function parses a single event, e.g.,
		'Montag, 15. November 2021' and returns the data formatted
		to the user's desire (JJJJ-MM-DD).
		"""

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

		# remove the name of the day (monday, tuesday, etc.)
		event_string_clean = event_string[event_string.find(',') + 2:]

		# extract day/month/year from the string
		event_day = event_string_clean[0:2]
		event_year = event_string_clean[-4:]
		event_string_remove_year = event_string[:-5]
		event_month = event_string_remove_year[event_string_remove_year.find('.') + 2:]

		extracted_formatted_date = (
			event_year + '-' + dict_months[event_month] +
			'-' + '%02d' % (int(event_day),)
		)

		#print(event_string_remove_year + '||||' + extracted_formatted_date)
		return extracted_formatted_date

	# change the fetched data from byte to str
	encoding = 'utf-8'
	source_str_data = str(source_of_URL, encoding)

	"""
	Cut the string to contain only the relevant information.
	The two cut points depend on a (unique) subset of the source.
	The cut string containing the relevant source code is stored
	in the variable 'cut_string'.
	"""
	cut_pos1 = source_str_data.find('aria-labelledby="c15570Heading5793"')
	cut_pos2 = source_str_data.find('col-xl-3 ml-xl-auto')
	cut_string = source_str_data[cut_pos1:cut_pos2]

	"""
	extract the dates and information from the URL subset
	data. Each single extraction event is enclosed in between:
	'<li><strong>Osterferien: </strong>Montag, 11. April 2022
	bis Samstag, 23. April 2022</li>', which is used to extract
	the information.
	"""
	search_string1 = '<li>'
	search_string2 = '</li>'

	return_event_descr = []
	return_event_date = []

	# process the string until an arbitrary length (150) of it is reached
	while len(cut_string) > 150:
		cut_pos3 = cut_string.find(search_string1)
		cut_pos4 = cut_string.find(search_string2)

		# extract the event description and the date
		event_extract = cut_string[cut_pos3 + len(search_string1):cut_pos4]

		event_description_raw = event_extract[event_extract.find('<strong>') + 8:event_extract.find('</strong>')]
		event_description = event_description_raw.replace(':', '').rstrip()

		event_date_raw = event_extract[event_extract.find('</strong>') + 9:].strip()

		single_event = event_date_raw.find('bis')

		if single_event == -1:
			single_date_str_parsed = parse_single_date(event_date_raw)
			print('single event (' + event_description + '): ' + single_date_str_parsed)

			return_event_descr.append(event_description)
			return_event_date.append(single_date_str_parsed)
		else:
			print('range event (' + event_description + '): ' + event_date_raw)

			event_date_start = event_date_raw[:single_event - 1]
			event_date_end = event_date_raw[single_event + 4:]

			event_date_start_formatted = parse_single_date(event_date_start)
			event_date_end_formatted = parse_single_date(event_date_end)

			return_event_descr.append(event_description)
			return_event_date.append(event_date_start_formatted)

			#print('		|' + event_date_start + '|' + event_date_end + '|')
			#print('		|' + event_date_start_formatted + '|' + event_date_end_formatted + '|')

			# generate dates for this event between start and end of it
			year = event_date_start_formatted[0:4]
			month = event_date_start_formatted[5:7]
			day = event_date_start_formatted[8:]

			date = datetime.datetime(int(year), int(month), int(day))
			#print(' >' + year + '|' + month + '|' + day)

			end_reached = False

			for i in range(365): 
				date += datetime.timedelta(days = 1)
				extract_date = date.strftime("%Y-%m-%d")
				#print(extract_date)

				return_event_descr.append(event_description)
				return_event_date.append(extract_date)


				if (extract_date == event_date_end_formatted):
					end_reached = True
					break

			if (end_reached == False):
				raise RuntimeError('Error creating the ranged data set for the event: ' + event_description + '(start: ' + event_date_start_formatted + '; end: ' + event_date_end_formatted)

		# remove the found information (and redo the search)
		cut_string = cut_string[cut_pos4 + len(search_string2):]

	# return the data through the function
	return return_event_descr, return_event_date

	#print(source_str_data)

## crawl the data (fetch the source code of the URLs) ##

# URL for the data which is to be crawled and processed
academic_calendar_URL = 'https://www.tuwien.at/studium/akademischer-kalender'
statutory_holidays_URL = 'https://www.wien.gv.at/amtshelfer/feiertage/'

"""
## statutory holidays ##
# fetch the page source code (statutory holidays)
statutory_holidays_source = fetch_page(statutory_holidays_URL)

# extract the dates and descriptions from the crawled page
return_event_descr, return_event_date = extract_statutory_holidays(
	statutory_holidays_source
)

# print the fetched and extracted data
for i in range(len(return_event_descr)):
	print(return_event_descr[i] + ' | ' + return_event_date[i])
"""

## academic calendar ##
# fetch the page source code (academic calendar)
academic_calendar_source = fetch_page(academic_calendar_URL)

# extract the dates and descriptions from the crawled page
return_event_descr, return_event_date = extract_academic_calendar(academic_calendar_source)

# print the fetched and extracted data
print('\n')
for i in range(len(return_event_descr)):
	print(return_event_descr[i] + '|' + return_event_date[i])


## insert the dates in the database (if they are not already in the DB) ##
