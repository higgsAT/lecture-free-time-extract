#!/usr/bin/env python3

import urllib.request
import datetime
import sqlhandler
import numpy as np
import pylogs

# sql DB variables
from config import *


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

	general_log.append_to_log("starting extraction: statutory holidays")

	# change the fetched data from byte to str
	encoding = 'latin-1'
	source_str_data = str(source_of_URL, encoding)

	"""
	Cut the string to contain only the relevant information.
	The two cut points depend on a (unique) subset of the source.
	The cut string containing the relevant source code is stored
	in the variable 'cut_string'.
	"""

	cut_str_find1 = 'editableDocument'
	cut_str_find2 = 'bde-stx-wrapper'

	cut_pos1 = source_str_data.find(cut_str_find1)
	cut_pos2 = source_str_data.find(cut_str_find2)
	cut_string = source_str_data[cut_pos1:cut_pos2]

	general_log.append_to_log("cut position1: " + cut_str_find1)
	general_log.append_to_log("cut position2: " + cut_str_find2)

	"""
	extract the dates and information from the URL subset
	data. Each single extraction event is enclosed in between:
	'<li><span>Neujahr: Freitag, 1. J??nner 2021</span></li>',
	which is used to extract the information.
	"""
	search_string1 = '<li><span>'
	search_string2 = '</span>'

	general_log.append_to_log("search string1: " + search_string1)
	general_log.append_to_log("search string2: " + search_string2)

	statutory_source_cut.dump_to_log(cut_string, "extracted part of the page source from which the events (dates, descriptions) will be extracted")

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
				'J??nner': '01',
				'Februar': '02',
				'M??rz': '03',
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

	general_log.append_to_log("amount of events found (date): " + str(len(return_event_date)))
	general_log.append_to_log("amount of events found (description): " + str(len(return_event_descr)))

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

	general_log.append_to_log("starting extraction: academic calendar")

	def parse_single_date(event_string):
		"""Extract/Convert a single date event.

		This function parses a single event, e.g.,
		'Montag, 15. November 2021' and returns the data formatted
		to the user's desire (JJJJ-MM-DD).
		"""

		# use a dictionary to convert the months (Dezember -> 12, etc.)
		dict_months = {
			'J??nner': '01',
			'Februar': '02',
			'M??rz': '03',
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

	cut_str_find1 = 'aria-labelledby="c426624Heading140154">'
	cut_str_find2 = 'wpGeneralContentElement wpContentElementText wpGeneralTextStyling'

	cut_pos1 = source_str_data.find(cut_str_find1)
	cut_pos2 = source_str_data.find(cut_str_find2)
	cut_string = source_str_data[cut_pos1:cut_pos2]

	# remove whitespaces from the string (&nbsp;)
	cut_string = cut_string.replace('&nbsp; ', '')
	cut_string = cut_string.replace('&nbsp;', '')

	academic_cal_source_cut.dump_to_log(cut_string, "extracted part of the page source from which the events (dates, descriptions) will be extracted")

	general_log.append_to_log("cut position1: " + cut_str_find1)
	general_log.append_to_log("cut position2: " + cut_str_find2)

	"""
	extract the dates and information from the URL subset
	data. Each single extraction event (incl. removed whitespaces)
	is enclosed in between: '<li>Allerseelen:&nbsp; &nbsp; &nbsp; 
	&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;
	Mittwoch, 02. November 2022</li>', which is used to extract the
	information.
	"""
	search_string1 = '<li>'
	search_string2 = '</li>'

	general_log.append_to_log("search string1: " + search_string1)
	general_log.append_to_log("search string2: " + search_string2)

	return_event_descr = []
	return_event_date = []

	# process the string until an arbitrary length (150) of it is reached
	while len(cut_string) > 150:
		cut_pos3 = cut_string.find(search_string1)
		cut_pos4 = cut_string.find(search_string2)

		# extract the event description and the date
		event_extract = cut_string[cut_pos3 + len(search_string1):cut_pos4]

		# get the event description
		event_description = event_extract[0:event_extract.find(':')]

		# extract the event date(s)
		event_date_raw = event_extract[len(event_description) + 1:].strip()

		# determine: single or range event
		single_event = event_date_raw.find('bis')

		# single event means a single day event, else, i.e., not minus one indicates
		# an event ranging over multiple days
		if single_event == -1:
			single_date_str_parsed = parse_single_date(event_date_raw)

			return_event_descr.append(event_description)
			return_event_date.append(single_date_str_parsed)
		else:
			event_date_start = event_date_raw[:single_event - 1]
			event_date_end = event_date_raw[single_event + 4:]

			event_date_start_formatted = parse_single_date(event_date_start)
			event_date_end_formatted = parse_single_date(event_date_end)

			return_event_descr.append(event_description)
			return_event_date.append(event_date_start_formatted)

			# generate dates for this event between start and end of it
			year = event_date_start_formatted[0:4]
			month = event_date_start_formatted[5:7]
			day = event_date_start_formatted[8:]

			date = datetime.datetime(int(year), int(month), int(day))
			end_reached = False

			# populate ranged events, e.g., semester breaks
			# which spans over months. If this range exceeds
			# one year, something with the end date gone wrong!
			for i in range(365): 
				date += datetime.timedelta(days = 1)
				extract_date = date.strftime("%Y-%m-%d")

				return_event_descr.append(event_description)
				return_event_date.append(extract_date)

				if (extract_date == event_date_end_formatted):
					end_reached = True
					break

			if (end_reached == False):
				# check the end date
				raise RuntimeError('Error creating the ranged data set for the event: ' +
				event_description + '(start: ' + event_date_start_formatted + '; end: ' +
				event_date_end_formatted + ". Eventlength exceeded 365 days")

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

	general_log.append_to_log("amount of events found (date): " + str(len(return_event_date)))
	general_log.append_to_log("amount of events found (description): " + str(len(return_event_descr)))

	# return the data through the function
	return return_event_descr, return_event_date

## initiate log files
general_log = pylogs.logs("logs/", "general_log")
statutory_source = pylogs.logs("logs/", "statutory_source")
academic_cal_source = pylogs.logs("logs/", "academic_calendar_source")
statutory_source_cut = pylogs.logs("logs/", "statutory_source_cut")
academic_cal_source_cut = pylogs.logs("logs/", "academic_calendar_source_cut")

general_log.append_to_log("program start")

## crawl the data (fetch the source code of the URLs) ##

# URL for the data which is to be crawled and processed
#academic_calendar_URL = 'https://www.tuwien.at/studium/akademischer-kalender/studienjahr-2021-22'
academic_calendar_URL = 'https://www.tuwien.at/studium/zulassung/akademischer-kalender/studienjahr-2022-23'
general_log.append_to_log("academic_calendar_URL: " + academic_calendar_URL)
statutory_holidays_URL = 'https://www.wien.gv.at/amtshelfer/feiertage/'
general_log.append_to_log("statutory_holidays_URL: " + statutory_holidays_URL)

## statutory holidays ##
# fetch the page source code (statutory holidays)
statutory_holidays_source = fetch_page(statutory_holidays_URL)
statutory_source.dump_to_log(str(statutory_holidays_source), "raw fetched page for the statutory holidays which will be processed")

# extract the dates and descriptions from the crawled page
return_event_descr_stat_hol, return_event_date_stat_hol = extract_statutory_holidays(
	statutory_holidays_source
)

# print the fetched and extracted data (statutory holidays)
general_log.append_to_log("extracted statutory holidays (event_description | event_date):")
for i in range(len(return_event_descr_stat_hol)):
	print('stat hol: ' + return_event_descr_stat_hol[i] + ' | ' + return_event_date_stat_hol[i])
	general_log.append_to_log("   " + return_event_descr_stat_hol[i] + ' | ' + return_event_date_stat_hol[i])


## academic calendar ##
# fetch the page source code (academic calendar)
academic_calendar_source = fetch_page(academic_calendar_URL)
academic_cal_source.dump_to_log(str(academic_calendar_source), "raw fetched page for the statutory holidays which will be processed")

# extract the dates and descriptions from the crawled page
return_event_descr_ac_cal, return_event_date_ac_cal = extract_academic_calendar(academic_calendar_source)
print('\n')
general_log.append_to_log("extracted academic calendar (event_description | event_date):")
for i in range(len(return_event_descr_ac_cal)):
	print('ac cal: ' + return_event_descr_ac_cal[i] + '|' + return_event_date_ac_cal[i])
	general_log.append_to_log("   " + return_event_descr_ac_cal[i] + ' | ' + return_event_date_ac_cal[i])

## check for duplicates ##

#Both extracted data sets (statutory holidays and academic calendar) are going to be
#inserted into a database (DB). If any date coincides, i.e., when a date is both a statutory
#holiday as well a free day in the academic calendar, the former date may be overwritten
#in the DB. Therefore, check for duplicate dates and merge the description (of the event) in
#that case.

general_log.append_to_log("removing/merging duplicates (overlaps in the statutory holidays and academic calendar)")

print('len (dates) stat holiday:  ' + str(len(return_event_date_stat_hol)))
print('len (dates) acad calendar: ' + str(len(return_event_date_ac_cal)))

# merge the two lists into one with unique (date) entries
insert_DB_event_descr = return_event_descr_ac_cal
insert_DB_event_date = return_event_date_ac_cal

amount_duplicates_found = 0

# remove duplicates and populate the (final) list
for i in range(len(return_event_date_stat_hol)):
	found_duplicate = False
	for j in range(len(insert_DB_event_date)):
		if(return_event_date_stat_hol[i] == insert_DB_event_date[j]):
			insert_DB_event_descr[j] = insert_DB_event_descr[j] + ', ' + return_event_descr_stat_hol[i]
			found_duplicate = True
			amount_duplicates_found += 1
			print('found duplicate: ' + str(amount_duplicates_found))
			general_log.append_to_log("found and merged duplicates: " + insert_DB_event_descr[j])
	if (found_duplicate == False):
		insert_DB_event_date.append(return_event_date_stat_hol[i])
		insert_DB_event_descr.append(return_event_descr_stat_hol[i])

print('\n\nlen (descr) final insert:  ' + str(len(insert_DB_event_descr)))
print('len (dates) final insert: ' + str(len(insert_DB_event_date)))

general_log.append_to_log("amount of found and merged duplicates: " + str(amount_duplicates_found))
general_log.append_to_log("final length of list (dates): " + str(len(insert_DB_event_date)))
general_log.append_to_log("final length of list (descriptions): " + str(len(insert_DB_event_descr)))

## insert the dates in the database (if they are not already in the DB) ##
general_log.append_to_log("adding extracted events into the database")

# sql handler initialisation
sqlhandlerObj = sqlhandler.SqlHandler()

# fetch the information about the dates/events present (pre insert) in the database
getTableData = sqlhandlerObj.fetch_table_content(dbDatabase, dbCalendarTable)

# convert the table data into a numpy array
arr = np.array(getTableData[0], dtype = object)

# remove the header information (stored in getTableData[1]) and
# slice the array (to contain only dates)
DB_fetch_dates_slice = arr[:, 0:1]
count_position = 1

for k in range(len(insert_DB_event_date)):
	# cut the date str for checking against the DB
	check_year = insert_DB_event_date[k][0:4]
	check_month = insert_DB_event_date[k][5:7]
	check_day = insert_DB_event_date[k][8:]

	# search the fetched DB data whether the date to be inserted
	# is already in the DB
	rows = np.where(DB_fetch_dates_slice == datetime.date(int(check_year),
		int(check_month), int(check_day)))

	# check if the date to be inserted is already in the DB
	if (len(DB_fetch_dates_slice[rows]) == 0):
		print("CHECK|", check_year, "|", check_month, "|", check_day)
		print(str(k) + '|' + insert_DB_event_date[k] + '|' + insert_DB_event_descr[k])
		print(" -> OO: ", insert_DB_event_date[k], " || ", len(DB_fetch_dates_slice[rows]), " | ", rows)
		print()
		general_log.append_to_log("event " + str(count_position) + " added to the database: " + insert_DB_event_date[k] + " | " + insert_DB_event_descr[k])

		# insert the data into the DB
		insertStatement = (
			"INSERT INTO " + dbCalendarTable + " (date, vorlesungsfrei, shortinfo, longinfo, location, piclink, event) "
			"VALUES (%s, %s, %s, %s, %s, %s, %s)"
		)
		insertData = (insert_DB_event_date[k], 1, insert_DB_event_descr[k], '', '', '', 0)

		sqlhandlerObj.insert_into_table(dbDatabase, insertStatement, insertData, 0)
	else:
		print(str(k) + '| alread in DB: ' + insert_DB_event_date[k] + '|' + insert_DB_event_descr[k])
		general_log.append_to_log("event " + str(count_position) + " already in database: " + insert_DB_event_date[k] + " | " + insert_DB_event_descr[k])

	count_position += 1

general_log.append_to_log("stopping program (finished)")
