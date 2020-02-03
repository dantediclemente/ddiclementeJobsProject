import requests
import json


def get_api_data():
    job_file = open('jobs.txt', 'w+')
    job_list = []
    page_number = 1

    while page_number < 6:
        response = requests.get("https://jobs.github.com/positions.json?&page=" + str(page_number))
        print(response.status_code)
        if response.status_code == 200:
            page_number += 1
            jobs = response.json()
            for job in jobs:
                job_list.append(json.dumps(job, sort_keys=True, indent=4))
    for job in job_list:
        job_file.write(job)
    return job_list


get_api_data()
