import sqlite3
import requests
import json
from typing import Tuple
import sys


def get_api_data():
    json_job_list = []
    more_data = True
    page_number = 1
    while more_data:
        response = requests.get("https://jobs.github.com/positions.json?&page=" + str(page_number))
        if response.status_code == 200:
            print('hit')
            page_number += 1
            jobs = response.json()
            for job in jobs:
                json_job_list.append(job)
            if len(jobs) < 50:
                more_data = False
    return json_job_list


def write_to_file(job_list):
    job_file = open('jobs.txt', 'w+')
    dumped_job_list = []
    for job in job_list:
        dumped_job_list.append(json.dumps(job, sort_keys=True, indent=4))
    for job in dumped_job_list:
        job_file.write(job)


def open_db(filename: str) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    db_connection = sqlite3.connect(filename)  # connect to existing DB or create new one
    cursor = db_connection.cursor()  # get ready to read/write data
    return db_connection, cursor


def close_db(connection: sqlite3.Connection):
    connection.commit()  # make sure any changes get saved
    connection.close()


def create_table(cursor: sqlite3.Cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS api_jobs(
        job_id TEXT PRIMARY KEY,
        company TEXT NOT NULL,
        company_logo TEXT,
        company_url TEXT,
        created_at TEXT,
        description TEXT,
        how_to_apply TEXT,
        location TEXT,
        title TEXT,
        type_of_job TEXT,
        url TEXT
        );''')


def drop_table_on_new_api_call(cursor: sqlite3.Cursor):
    cursor.execute('DROP TABLE IF EXISTS api_jobs')


def insert_data_into_db(cursor: sqlite3.Cursor, job_list):
    for job in job_list:
        try:
            cursor.execute(f'''INSERT or REPLACE INTO api_jobs (job_id, company, company_logo, company_url, created_at,
                            description, how_to_apply, location, title, type_of_job, url)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (job['id'], job['company'], job['company_logo'],
                            job['company_url'], job['created_at'],
                            job['description'], job['how_to_apply'],
                            job['location'], job['title'],
                            job['type'], job['url']))
        except KeyError as error:
            print("Failed to insert data into sqlite table", error)

            return "failed"


def main():
    write_to_file(get_api_data())
    conn, cursor = open_db("jobs_db.sqlite")
    print(type(conn))
    drop_table_on_new_api_call(cursor)
    create_table(cursor)
    insert_data_into_db(cursor, get_api_data())
    close_db(conn)


if __name__ == '__main__':
    main()
