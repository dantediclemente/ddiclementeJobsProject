# Dante DiClemente Jobs Project

## Description
- This project grabs data from the github jobs api and then stores the json objects in a text file. 
- This project now also stores that data into a sqlite3 database. 

## Requirements 
  `requests`
  `typing`
  
  You will also need pytest installed.

## Testing
- There are multiple automated tests. 
  - Check the job listing in the file
  - Check for a known result in the database
  - Check all the data in the database
  - Check to see if the db table exists
  - Check that good data **DOES NOT** throw an error
  - Check that bad data **DOES** throw an error
  
    #### Command to run tests
  - `python -m pytest`
