import urllib.request

# URL for the data which is to be crawled and processed
academic_calender_URL = 'https://www.tuwien.at/studium/akademischer-kalender'
statutory_holidays = 'https://www.wien.gv.at/amtshelfer/feiertage/'

#fetched_page = urllib.request.urlopen(statutory_holidays)
#print(fetched_page.read())



# crawl the data (fetch the source code of the URLs)

# extract the dates from the crawled pages

# insert the dates in the database (if they are not already in the DB)
