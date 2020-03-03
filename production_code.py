import sqlite3
import requests
import json
from typing import Tuple
import feedparser
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import re
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from datetime import datetime as dt
import datetime as datet
import dateutil.parser
from bs4 import BeautifulSoup


def get_api_data():
    json_job_list = []
    more_data = True
    page_number = 1
    while more_data:
        response = requests.get("https://jobs.github.com/positions.json?&page=" + str(page_number))
        if response.status_code == 200:
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
        except (sqlite3.IntegrityError, KeyError) as error:
            print("Failed to insert data into sqlite table", error)

            return "failed"


def data_from_stack_overflow():
    json_job_list = []
    jobs = feedparser.parse("https://stackoverflow.com/jobs/feed")
    for each in jobs.entries:
        new_json_obj = {
            "id": str(each.id),
            "company": str(each.author),
            "company_logo": None,
            "company_url": None,
            "created_at": str(each.published),
            "description": str(each.summary),
            "how_to_apply": None,
            "location": str(each.location) if 'location' in each else None,
            "title": str(each.title),
            "type": None,
            "url": str(each.link)
        }
        json_job_list.append(new_json_obj)
    return json_job_list


def create_table_cache_for_job_locations(cursor: sqlite3.Cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS api_jobs_location_cache(
        location TEXT NOT NULL, 
         lat TEXT NOT NULL,
         long TEXT NOT NULL
         );''')


def grab_all_jobs_for_lat_long(cursor: sqlite3.Cursor):
    locations = cursor.execute("SELECT location FROM api_jobs WHERE location IS NOT NULL")
    list_of_cities_for_geo = []
    for location in locations:
        split_location = re.split(r', |; |-| \| |/|&| or ', location[0])
        final_location = split_location[0].lower()

        if final_location.split()[0] != 'remote':
            if final_location not in list_of_cities_for_geo:
                list_of_cities_for_geo.append(final_location)

    return list_of_cities_for_geo


def convert_city(location):
    split_location = re.split(r', |; |-| \| |/|&| or ', location)
    final_location = split_location[0].lower()

    return final_location


def geo_lat_and_long_for_location(cursor: sqlite3.Cursor, list_of_cities):
    geolocator = Nominatim(user_agent="https://nominatim.openstreetmap.org/search?")
    limiter = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    for location in list_of_cities:
        location_in_cache = cursor.execute(f'''SELECT location FROM api_jobs_location_cache WHERE location = ?''',
                                           (location,))

        if len(location_in_cache.fetchall()) == 0:
            geo_location = limiter(location)
            if geo_location is not None:
                print(geo_location.latitude, geo_location.longitude)
                cursor.execute(f'''INSERT INTO api_jobs_location_cache (location, lat, long) VALUES (?, ?, ?)''',
                               (location,
                                geo_location.latitude,
                                geo_location.longitude))


def fetch_all_jobs(cursor: sqlite3.Cursor):
    jobs_list = []
    actual_jobs = cursor.execute("SELECT * FROM api_jobs")

    for job in actual_jobs:
        new_job_object = {
            "job_id": job[0],
            "company": job[1],
            "company_logo": job[2],
            "company_url": job[3],
            "created_at": job[4],
            "description": job[5],
            "how_to_apply": job[6],
            "location": job[7] if job[7] in job else None,
            "title": job[8],
            "type": job[9],
            "url": job[10],
            "lat": None,
            "long": None
        }
        jobs_list.append(new_job_object)

    return jobs_list


def fetch_all_jobs_with_lat_long(cursor: sqlite3.Cursor, actual_jobs):
    jobs_list_with_updated_location = []

    for job in actual_jobs:
        if job['location'] is not None:
            converted_city = convert_city(job['location'])
            if converted_city.split()[0] != 'remote':
                cache_city = cursor.execute("SELECT * FROM api_jobs_location_cache WHERE location = ?",
                                            (converted_city,))
                lat_and_long = cache_city.fetchone()
                if lat_and_long is not None:
                    lat_from_cache = lat_and_long[1]
                    long_from_cache = lat_and_long[2]
                else:
                    lat_from_cache = None
                    long_from_cache = None

        job['lat'] = lat_from_cache
        job['long'] = long_from_cache

        jobs_list_with_updated_location.append(job)

    return jobs_list_with_updated_location


def filter_jobs_by_desc(filtered_input, list_of_job_objects):
    filtered_job_objects = []

    formatted_filtered_input = filtered_input.lower().strip().split(',')

    if formatted_filtered_input[0] == '':
        return list_of_job_objects
    else:
        for job in list_of_job_objects:
            if job not in filtered_job_objects:
                job_desc = job['description'].lower()
                for technology in formatted_filtered_input:
                    if technology in job_desc:
                        filtered_job_objects.append(job)

    return filtered_job_objects


def parse_time_from_db(text):
    for _ in ('%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y'):
        try:
            return dt.date(dateutil.parser.parse(text))
        except ValueError:
            pass


def filter_jobs_by_date(filtered_input, list_of_job_objects):
    filtered_job_objects = []

    if filtered_input == "":
        filtered_input = 1
        today = dt.now()
        weeks_ago = dt.date(today - datet.timedelta(days=int(filtered_input) * 7))
    else:
        today = dt.now()
        weeks_ago = dt.date(today - datet.timedelta(days=int(filtered_input) * 7))

    for job in list_of_job_objects:
        parsed_time = parse_time_from_db(job["created_at"])

        if weeks_ago < parsed_time:
            filtered_job_objects.append(job)

    return filtered_job_objects


def gui_setup(fig, list_of_job_objects):
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    app.layout = html.Div(children=[
        html.H1(children='API Jobs'),

        html.Div(children='''
            Jobs from the StackOverflow and Github job boards.
        '''),

        dcc.Graph(
            id='job-graph',
            figure=fig,
            style={
                'height': '75vh',
                'zoom': 0
            }
        ),

        html.Div([
            dcc.Input(id='technologies', placeholder='Enter three technologies', value="", type='text'),
            dcc.Input(id='company', placeholder='Enter company name', value="", type='text'),
            dcc.Input(id='date-time', placeholder='weeks ago', value=1, type='number', min=0, max=52, step=4),
            dcc.Dropdown(
                id='job-type',
                options=[
                    {'label': 'All', 'value': ''},
                    {'label': 'Full-Time', 'value': 'full time'},
                    {'label': 'Part-Time', 'value': 'part time'},
                    {'label': 'Remote', 'value': 'remote'},
                ],
                value="Any",
                searchable=False,
                clearable=False,
                style={
                    'width':'200px'
                }
            )
        ]),

        html.Div([
            html.Pre(id='individual-data'),
        ])
    ])

    @app.callback(
        Output(component_id='job-graph', component_property='figure'),
        [Input(component_id='technologies', component_property='value'),
         Input(component_id='company', component_property='value'),
         Input(component_id='date-time', component_property='value'),
         Input(component_id='job-type', component_property='value')]
    )
    def update_output_div(technologies, company, date_time, job_type):
        tech_filter = filter_jobs_by_desc(technologies, list_of_job_objects)
        company_filter = filter_jobs_by_desc(company, tech_filter)
        date_filter = filter_jobs_by_date(date_time, company_filter)
        job_type = filter_jobs_by_desc(job_type, date_filter)

        new_fig = map_for_jobs(job_type)

        return new_fig

    @app.callback(
        Output(component_id='individual-data', component_property='children'),
        [Input(component_id='job-graph', component_property='clickData')]
    )
    def show_data(graph_data):
        if graph_data is not None:
            job_lat = graph_data['points'][0]['lat']
            job_long = graph_data['points'][0]['lon']
            job_title = graph_data['points'][0]['text'].split(",")[0]

            for job in list_of_job_objects:
                if job['company'] == job_title and job['lat'] == job_lat and job['long'] == job_long:
                    current_job = job
                    soup = BeautifulSoup(current_job['description'])
                    current_job['description'] = soup.get_text(separator="\n")
                    print(soup.get_text(separator="\n"))
                    return html.Ul([html.Li(current_job[x]) for x in current_job])

    return app


def map_for_jobs(list_of_job_objects):
    mbx_access_token = "pk.eyJ1IjoiZGFudGVkaWNsZW1lbnRlIiwiYSI6ImNrNzB6dHE1cjAxeGczZ25zcWo1YW9mZWoifQ" \
                       ".AJDlCC171CRF1xDT9rEd0A "

    lat = []
    long = []
    company_name = []
    for job in list_of_job_objects:
        if job['lat'] is not None and job['long'] is not None:
            lat.append(job['lat'])
            long.append(job['long'])
            name_and_title = job['company'] + ", " + job['title']
            company_name.append(name_and_title)

    fig = go.Figure(go.Scattermapbox(
        lat=lat,
        lon=long,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=14
        ),
        text=company_name,
    ))

    fig.update_layout(
        hovermode='closest',
        mapbox=dict(
            accesstoken=mbx_access_token,
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=0,
                lon=0
            ),
            pitch=0,
            zoom=0
        )
    )

    return fig


def main():
    write_to_file(get_api_data())
    conn, cursor = open_db("jobs_db.sqlite")
    print(type(conn))
    drop_table_on_new_api_call(cursor)
    create_table(cursor)
    insert_data_into_db(cursor, get_api_data())
    insert_data_into_db(cursor, data_from_stack_overflow())
    create_table_cache_for_job_locations(cursor)
    all_jobs = grab_all_jobs_for_lat_long(cursor)
    geo_lat_and_long_for_location(cursor, all_jobs)
    all_jobs = fetch_all_jobs_with_lat_long(cursor, fetch_all_jobs(cursor))
    map_figure = map_for_jobs(all_jobs)
    close_db(conn)
    gui_setup(map_figure, all_jobs).run_server()


if __name__ == '__main__':
    main()
