"""
XC Track Library

contains methods to import Task from XcTrack .xctsk file

Use: import sources.xctrack

Antonio Golfari - 2024
"""

import json

from . import utils
from pathlib import Path


def read_xctsk_file(file) -> "dict | None":

    try:
        return json.load(file)
    except:
        print("xctsk file is not a valid JSON object")
        return None


def read_task(data: dict) -> dict:

    task_info = {}
    if data:
        try:
            # task_info['task_type'] = 'elapsed time' if data.get('taskType') == 'elapsed_time' else 'race'
            if data.get('sss'):
                # task type
                print(f"task type: {data['sss']['type'].lower()}")
                task_info['task_type'] =  'elapsed_time' if data['sss']['type'].lower() == 'elapsed_time' else 'race'
                # start gates
                print(f"len gates: {len(data['sss']['timeGates'])}")
                if len(data['sss']['timeGates']):
                    task_info['start_time'] = utils.get_time(data['sss']['timeGates'][0])
                    if len(data['sss']['timeGates']) > 1:
                        # we have multiple starts
                        second = utils.get_time(data['sss']['timeGates'][1])
                        task_info['SS_interval'] = second - task_info['start_time']
                        task_info['start_iteration'] = len(data['sss']['timeGates']) - 1
                    print(f"start: {task_info['start_time']}")
                    # xctrack file does not have launch window info
                    task_info['window_open_time'] = task_info['start_time'] - 3600
                    task_info['window_close_time'] = task_info['start_time']
                if data['sss'].get('timeClose'):
                    task_info['start_close_time'] = utils.get_time(data['sss']['timeClose'])
                elif task_info['start_time']:
                    task_info['start_close_time'] = task_info['start_time'] + 3600

            if data.get('goal') and data['goal'].get('deadline'):
                task_info['task_deadline'] = utils.get_time(data['goal']['deadline'])
            elif task_info['start_time']:
                task_info['task_deadline'] = task_info['start_time'] + 3600 * 4 # 4 hours from start by default

            if data.get('takeoff'):
                if data['takeoff'].get('timeOpen'):
                    task_info['window_open_time'] = utils.get_time(data['takeoff']['timeOpen'])
                if data['takeoff'].get('timeClose'):
                    task_info['window_close_time'] = utils.get_time(data['takeoff']['timeClose'])

            print(f"s close: {task_info['start_close_time']}")
            print(f"w open: {task_info['window_open_time']}")
            print(f"w close: {task_info['window_close_time']}")

            # task_info['task_deadline'] = utils.get_time(data['goal']['deadline'])
            task_info['route'] = []
            for idx, el in enumerate(data['turnpoints']):
                w = el['waypoint']
                wpt = dict(
                    num=idx,
                    name=w['name'],
                    description=w['description'],
                    lat=w['lat'], lon=w['lon'],
                    altitude=int(w['altSmoothed']),
                    radius=int(el['radius']),
                    shape='circle',
                    how='entry'
                )
                t = None if el.get('type') is None else el['type'].lower()
                if t == 'takeoff':
                    wpt['type'] = 'launch'
                    wpt['how'] = 'exit'
                elif t == 'sss':
                    wpt['type'] = 'speed'
                elif t == 'ess':
                    wpt['type'] = 'endspeed'
                elif idx == len(data['turnpoints']) - 1:
                    wpt['type'] = 'goal'
                    wpt['shape'] = 'circle'
                    if data.get('goal') and data['goal'].get('type') == 'line':
                            wpt['shape'] = 'line'
                else:
                    wpt['type'] = 'waypoint'

                task_info['route'].append(wpt)

        except TypeError as e:
            print(f"Some task data is missing: {e}")
            raise
        except Exception as e:
            print(f"Error reading task data: {e}")
            raise
    else:
        print("No task data provided")

    return task_info

