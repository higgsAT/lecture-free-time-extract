#  lecture-free-time-extract
A program to extract lecture-free times (holidays, semester breaks, etc.) for the TU Wien (Vienna University of Technology) which are then to be stored in a database.

## Description
Starting from several websites, this (python) program fetches the source of the pages and extract desired informations. These informations are dates and descriptions of lecture free times (academic calendar and statutory holidays), which are stored in a SQL database).

## Folder Structure
This project has the following folder structure
```
.
├── logs
└── src
    └── sqlhandler.py
    ├── pylogs.py
    ├── extract_lecture_free_times.py
    └── config_example.py
```
The mainprogram, extracting and inserting the required information into the database (DB), is called **extract_lecture_free_times.py**. Operations regarding the DB (inserting, fetching remote data, etc.) is handled via **Sqlhandler.py**. Generated logs (fetched source files of webpages, runtime logs, etc.) are stored in */logs* and handled via **pylogs.py**. The last file (**config_example.py**) gives an example of the login credentials as well as the DB endpoints (DB name and table name where the data will be stored).

## Workflow of the Program *extract_lecture_free_times.py*
1. URLs of **statutory holidays** and **lecture free times** are stored in `statutory_holidays_URL` and `academic_calendar_URL`, respectively.
2. The function `fetch_page(URL_to_be_fetched)` retrieves the source code of the given URL.
3. Using this data, the functions `extract_statutory_holidays(source_of_URL)` and `extract_academic_calendar(source_of_URL)` extract the dates and descriptions of the lecture-free times. Both functions return (each) two lists containing the descriptions and dates. Both work similarly:
    1. Cut the (URL source) string at two unique locations (*cut_pos1* and *cut_pos2*). This will be for example stored in **/logs/*_cut.txt**.
    2. The dates and event descriptions in this pre-cut data will be then further processed. Using **search_string1** and **search_string2**, each date will be cut and extracted. These are, e.g., *<li>* elements in the soruce code.
    3. Until this (pre-cut) string has a certain length, it will be processed, i.e., dates and descriptions will be extracted from it.
    4. The information in the two lists (date format: YYYY-MM-DD) will be then returned from these two funtions.
4. Dates may overlap, i.e., these two lists may contain date-duplicates. Hence, the next step is **removing duplicates** (see comment `# remove duplicates and populate the (final) list` in the source file). Both lists will be merged into one, while duplicate dates are merged and the descriptions are preserved (both descriptions used for these cases).
5. All present dates and events are fetched from the SQL database.
6. In case where the events are not found in the DB they are inserted.

During runtime several logs are created and stored in **/logs**.

## Troubleshooting the Program
1. Are the URLs reachable (`statutory_holidays_URL` and `academic_calendar_URL`) and fetchable?
2. Was the pre-cutting of the source correct (see point 2. of the workflow and check **/logs/*_cut.txt**)?
3. Were the returned dates/events correct -> check the extracted dates (**search_string1** and **search_string2**!)
4. Debug the DB connection (general connection, fetching the DB information).
5. Check the logs in **/logs**.

## Running the Program
1. Setting up the DB/login-credentials (rename and configure  the file **config_example.py**)
2. Use the provided makefile or invoke `python3 src/extract_lecture_free_times.py`
