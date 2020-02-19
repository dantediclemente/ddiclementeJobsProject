# Dante DiClemente Jobs Project

## Description
- This project grabs data from the github jobs api and the stackoverflow jobs feed, then stores the json objects in a sqlite3 database. 

## Requirements 
  `requests`
  `typing`
  `feedparser`
  
  You will also need pytest installed.

## Testing
- There are multiple automated tests. 
  - Check the job listing in the file
  - Check for a known result in the database from github and stackoverflow 
  - Check all the data in the database
  - Check to see if the db table exists
  - Check that good data **DOES NOT** throw an error
  - Check that bad data **DOES** throw an error
  
    #### Command to run tests
  - `python -m pytest`
