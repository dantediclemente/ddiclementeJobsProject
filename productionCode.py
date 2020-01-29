import requests
import json


def get_api_data():
    response = requests.get("https://jobs.github.com/positions.json")
    j_print(json.dumps(response.json(), sort_keys=True, indent=4))


def j_print(job_list):
    job_file = open('jobs.txt', 'w+')

    for each in job_list:
        job_file.write(each)


get_api_data()