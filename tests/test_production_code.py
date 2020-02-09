import production_code
import os.path

conn, cursor = production_code.open_db("jobs_db.sqlite")


def test_first_job_listing_in_file():
    job_file = open(os.path.dirname(__file__) + '/../jobs.txt', 'r')
    name_found_in_line = False
    for line in job_file:
        if 'F. Hoffmann-La Roche AG' in line:
            name_found_in_line = True
    assert name_found_in_line


def test_length_of_result():
    result = production_code.get_api_data()
    assert len(result) > 100


def test_known_result_in_db():
    result = cursor.execute('SELECT company FROM api_jobs WHERE company = "DevsData"')
    assert result.fetchone()[0] == "DevsData"


# Extra Test, tests that ALL the data in the db is correct after each pull from the API.
def test_all_data_in_db():
    result = cursor.execute('SELECT * FROM api_jobs')
    jobs = production_code.get_api_data()
    for (job, row) in zip(jobs, result):
        assert job['id'] == row[0]
        assert job['company'] == row[1]
        assert job['company_logo'] == row[2]
        assert job['company_url'] == row[3]
        assert job['created_at'] == row[4]
        assert job['description'] == row[5]
        assert job['how_to_apply'] == row[6]
        assert job['location'] == row[7]
        assert job['title'] == row[8]
        assert job['type'] == row[9]
        assert job['url'] == row[10]


def test_if_db_table_exists():
    result = cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='api_jobs';''')
    assert result.fetchone()[0] == 'api_jobs'


def test_good_data_input():
    job_list = [{
        "company": "test",
        "company_logo": "test",
        "company_url": "test",
        "created_at": "test",
        "description": "test",
        "how_to_apply": "test",
        "id": "test",
        "location": "test",
        "title": "test",
        "type": "test",
        "url": "test"
    }]
    result = production_code.insert_data_into_db(cursor, job_list)
    assert result is None


# Missing company name which is not allowed.
def test_bad_data_input():
    job_list = [{
        "company_logo": 'test',
        "company_url": "test",
        "created_at": "test",
        "description": "test",
        "how_to_apply": "test",
        "id": "test",
        "location": "test",
        "title": "test",
        "type": "test",
        "url": "test"
    }]
    result = production_code.insert_data_into_db(cursor, job_list)
    assert result == "failed"
