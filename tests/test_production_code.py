from production_code import get_api_data
import os.path


def test_number_of_jobs():
    jobs = get_api_data()
    assert len(jobs) > 100


def test_first_job_listing():
    job_file = open(os.path.dirname(__file__) + '/../jobs.txt', 'r')
    name_found_in_line = False
    for line in job_file:
        if 'F. Hoffmann-La Roche AG' in line:
            name_found_in_line = True
    assert name_found_in_line
