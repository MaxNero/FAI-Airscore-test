"""
Task Planner Library

contains methods to import Task from Tonino Tarsi's TasK Creator .tsk file
https://www.vololiberomontecucco.it/taskcreator/

Use: from sources.taskplanner import TaskPlanner

Antonio Golfari - 2024
"""

from . import utils
from lxml import etree
from pathlib import Path


def read_tsk_file(file: Path) -> "etree | None":

    return utils.read_xml_file(file)


def read_task(root: etree) -> dict:
    """creates a dict file with all task information to be imported from Airscore"""

    task_info = {}

    if len(root):
        rte = root.find('rte')
        # task info
        task_info['task_type'] = rte.find('type').text  # 'race', 'elapsed_time'
        # gates info
        gates = int(rte.find('ngates').text)
        if gates > 1:
            task_info['start_iteration'] = gates - 1
            task_info['SS_interval'] = int(rte.find('gateint').text) * 60  # in seconds
        # comment
        if rte.find('info').text:
            task_info['comment'] = rte.find('info').text
        # wpt info
        task_info['route'] = []
        for node in rte.iter('rtept'):
            wpt = dict(
                num=int(node.find('index').text),
                name=node.find('id').text,
                description=node.find('name').text,
                lat=float(node.get('lat')), lon=float(node.get('lon')),
                altitude=None if node.find('z') is None else int(node.find('z').text),
                radius=int(node.find('radius').text),
                shape='circle',
                how='entry'
            )
            t = node.find('type').text.lower()
            if t == 'takeoff':
                wpt['type'] = 'launch'
                wpt['how'] = 'exit'
                task_info['window_open_time'] = utils.get_time(node.find('open').text)
                task_info['window_close_time'] = utils.get_time(node.find('close').text)
            elif t == 'start':
                wpt['type'] = 'speed'
                task_info['start_time'] = utils.get_time(node.find('open').text)
                task_info['start_close_time'] = (
                    task_info['start_time'] + 3600 if not node.find('close')
                    else utils.get_time(node.find('close').text)
                )
            elif t == 'end-of-speed-section':
                wpt['type'] = 'endspeed'
            elif t == 'goal':
                wpt['type'] = 'goal'
                if node.find('goalType').text == 'line':
                    wpt['shape'] = 'line'
                task_info['task_deadline'] = utils.get_time(node.find('close').text)
            else:
                wpt['type'] = 'waypoint'

            task_info['route'].append(wpt)

    return task_info