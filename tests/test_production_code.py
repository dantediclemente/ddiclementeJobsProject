#Dante DiClemente

import pytest
import requests
from production_code import get_api_data
import os.path


def test_number_of_jobs():
    jobs = get_api_data()
    assert len(jobs) > 100


def test_first_job_listing():
    file = open(os.path.dirname(__file__) + '/../jobs.txt', 'r')
    assert file.read(43) == '{\n    "company": "F. Hoffmann-La Roche AG",'
