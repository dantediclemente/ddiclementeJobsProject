import requests
import json


def get_api_data():
    job_file = open('jobs.txt', 'w+')
    job_list = []
    response_length = 1
    page_number = 1

    while response_length != 0:
        response = requests.get("https://jobs.github.com/positions.json?&page=" + str(page_number))
        page_number += 1
        response_length = len(response.json())
        jobs = response.json()
        for job in jobs:
            job_list.append(json.dumps(job, sort_keys=True, indent=4))
    for job in job_list:
        job_file.write(job)
        print(job)
    return job_list


get_api_data()
