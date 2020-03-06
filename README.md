# Dante DiClemente Jobs Project

## Description
- This project grabs data from the github jobs api and the stackoverflow jobs feed, then stores the json objects in a sqlite3 database. 
- This project now has a DASH gui for viewing all jobs.

  ### Filters
  - There are four filters
    - Technology
    - company
    - age of job posting
    - type of job (full-time, part-time, remote)
    
  ### Map
  - All job postings are located on a plotly map.
  - If you click on one of these postings, you will find additional data about that job located below the filters.

## Requirements 
  `requests`
  `typing`
  `feedparser`
  `plotly`
  `geopy`
  `dash`
  `datetime`
  `python-dateutil`
  `bs4`
  
  You will also need pytest installed.

## Testing
- There are multiple automated tests. 
  - Check the job listing in the file
  - Check for a known result in the database from github and stackoverflow 
  - Check all the data in the database
  - Check to see if the db table exists
  - Check that good data **DOES NOT** throw an error
  - Check that bad data **DOES** throw an error
  - Checks that the filters return the right data
  - Checks that the right data is returned when clicking on a specific job.
  
    #### Command to run tests
  - `python -m pytest`
