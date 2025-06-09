"""
needs to be run with python3.
i.e.
from flymaster.py import get_tracks

By Stuart Mackintosh, Antonio Golfari, 2019
"""
# TODO probably better add all sources to a sources folder? Create a sources package?
import logging
import time
from pathlib import Path

import requests

# in Flymaster format is:
# LiveTrack Antoine Saraf.361951.20190717-113625.5836.47.igc = 'other name name.live.other-other.other.id'
# Other name surname.live_id.YYYYmmdd-hhmmss.ID.igc
filename_formats = ['other name name.live.other-other.other.id']


def get_pilot_from_list(filename, pilots):
    """check filename against a list of Pilot Obj.
    Looks for different information in filename

    filename:   STR file name
    pilots:     LIST Participants Obj.
    """
    # in Flymaster Livetrack format is:
    # LiveTrack Gerd Doenhuber.845196.20190717-110908.11448.56.igc
    # LiveTrack name.LiveID.YYYYmmdd-hhmmss.????.ID.igc
    # Participant.ID is the last number
    # The first number is pilot LIVE id, which we could get from pilot list excel file
    # TODO we should make AirScore format similar to this one

    print(f'Flymaster get pilot function')
    string = Path(filename).stem
    fields = string.split('.')
    ID = int(fields[-1])
    live = int(fields[1])
    name = fields[0].lower()
    for idx, pilot in enumerate(pilots):
        # using live_id
        if pilot.live_id == live:
            '''found a pilot'''
            # pilot.track_file = filename
            if not pilot.name.lower() in name:
                print(f'WARNING: Name {pilot.name.lower()} does not match with filename {string}')
            return pilot, idx


def get_xc_parameters(task_id):
    """Get site info and date from database """
    # TODO I suspect the logic on xc_site will be broken if we use waypoint file instead of table
    # Should we use TblTaskWaypoint instead or manually or by adding xc_to id to launch name or description?


def get_zip(date, login_name, password, zip_file):
    """Get the zip of igc files from flymaster."""
    import lxml.html

    try:
        zfile = requests.get()
        # save the file
        with open(zip_file, 'wb') as f:
            f.write(zfile.content)
    except requests.exceptions.MissingSchema:
        print(f'Error: Seems like there are no tracks yet on {date}')


def send_task(task_id: int) -> int:
    from livetracking import LiveTask
    import datetime
    import jsonpickle
    t = LiveTask.read(task_id)
    wpts = []
    midnight = datetime.datetime.min
    time_after_seconds = midnight + datetime.timedelta(seconds=t.start_time) + datetime.timedelta(seconds=t.time_offset)
    hours = time_after_seconds.hour
    minutes = time_after_seconds.minute
    time = f'{hours:02d}{minutes:02d}'
    interval = '' if not t.SS_interval else int(t.SS_interval / 60)
    start_number = '' if not t.SS_interval else t.start_iteration + 1
    FM = 'https://wlb.flymaster.net/createTask.php'
    grp = t.ext_server_id
    token = t.ext_server_token
    # headers = {"Content-Type": "application/json"} # Add this if sending JSON
    for pt in t.turnpoints:
        wpt = {
            'Name': pt.name,
            'Lat': pt.lat,
            'Lon': pt.lon,
            'Size': pt.radius / 1000,  # Flymaster needs radius in Km
            'Type': 0 if pt.type == 'launch' else 1 if pt.type == 'speed' else 3 if pt.type == 'waypoint' 
                else 5 if pt.type == 'endspeed' else 4 if (pt.type == 'goal' and pt.shape == 'circle') else 6,
            'Time': time if pt.type == 'speed' else '',
            'NumStarts': start_number if pt.type == 'speed' else '',
            'StartIntervals': interval if pt.type == 'speed' else '',
        }
        wpts.append(wpt)
    url = FM
    payload = {'grpid': grp, 'token': token, 'task': jsonpickle.encode(wpts)}
    try:
        response = requests.post(url, data=payload)  # or, for JSON: , headers=headers, json=payload)
        # 4. Check the response
        if response.status_code == 200:  # Or another success code (e.g., 201 for created)
            print("POST request successful!")
            print("Response content:", response.text)  # Or response.json() if the response is JSON
        else:
            print(f"POST request failed. Status code: {response.status_code}")
            print("Response content:", response.text)
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    return 0


def get_zipfile(task, temp_folder):
    """"""
    from os import path

    import Defines

    result = ''
    task_id = task.task_id

    """get zipfile from Flymaster server"""

    zip_name = 'igc_from_fm.zip'
    zipfile = path.join(temp_folder, zip_name)

    get_zip(zipfile)
    return zipfile
