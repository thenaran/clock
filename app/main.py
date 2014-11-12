# -*- coding: utf-8 -*-
# Copyright 2012-2014 Narantech Inc.
#
# This program is a property of Narantech Inc. Any form of infringement is
# strictly prohibited. You may not, but not limited to, copy, steal, modify
# and/or redistribute without appropriate permissions under any circumstance.
#
#  __    _ _______ ______   _______ __    _ _______ _______ _______ __   __
# |  |  | |   _   |    _ | |   _   |  |  | |       |       |       |  | |  |
# |   |_| |  |_|  |   | || |  |_|  |   |_| |_     _|    ___|       |  |_|  |
# |       |       |   |_||_|       |       | |   | |   |___|       |       |
# |  _    |       |    __  |       |  _    | |   | |    ___|      _|       |
# | | |   |   _   |   |  | |   _   | | |   | |   | |   |___|     |_|   _   |
# |_|  |__|__| |__|___|  |_|__| |__|_|  |__| |___| |_______|_______|__| |__|

# default
import os
import time
import datetime
import logging

# clique
import clique
import clique.isc
import clique.runtime
import clique.web
import clique.event
from clique import Lazy
from clique.util import Timer

# ambiency
import ambiency
from ambiency import build_sensor
from ambiency import build_trigger
from ambiency import build_trigger_data_type
from ambiency import build_source
from ambiency import sensors

PUSH = None
DATA = Lazy()
MIN_ID = 'minute'
HOUR_ID = 'hour'
WEEK_ID = 'week'
DAY_ID = 'day'
MON_ID = 'month'
YEAR_ID = 'year'
DATA.OLD_TIME = [0, 0, 0, '', 0, 0]
id_types = [YEAR_ID, MON_ID, DAY_ID, WEEK_ID, HOUR_ID, MIN_ID]


@sensors
def get_sensors():
  sources = []
  sources.append(build_source('time', 'Timer',
                              desc='Notify current time in every minutes',
                              icon_uri='/ambiency/source.ico'))
  types = [['year', 'Year', 'int', 'year', 'Represent a year'],
           ['month', 'Month', 'int', 'month', 'Represent a month'],
           ['day', 'Day', 'int', 'day', 'Represent a day'],
           ['week', 'Week', 'string', 'week', 'Represent a week'],
           ['hour', 'Hour', 'int', 'hour', 'Represent a hour'],
           ['minute', 'Minute', 'int', 'minute', 'Represent a minute']]
  trigger_data_types = []
  for typ in types:
    trigger_data_types.append(build_trigger_data_type(*typ))
  triggers = []
  triggers.append(build_trigger('timeChangedTrigger',
                                'Current Time',
                                sources,
                                trigger_data_types,
                                "It's triggered when time is changed",
                                '/ambiency/trigger.ico'))
  sensors = []
  sensors.append(build_sensor('time',
                              'Time',
                              triggers,
                              "It's triggered when time is changed",
                              '/ambiency/sensor.ico'))
  return sensors


def tick():
  current_time = time.strftime('%Y %m %d %a %H %M')
  current_time = current_time.split()

  data = {}
  for id_type, old, current in zip(id_types, DATA.OLD_TIME, current_time):
    if (old != current):
      if id_type != WEEK_ID:
        data[id_type] = int(current)
      else:
        data[id_type] = current
  DATA.OLD_TIME = current_time

  if len(data) != 0 :
    ambiency.push('time', 'timeChangedTrigger', ['time'], data)


def start():
  try:
    logging.debug("Boot time app...")
    Timer(clique.ioloop(), 60, tick, repeat=True)
    ambiency_path = os.path.join(clique.runtime.res_dir(), 'ambiency')
    clique.web.set_static_path(os.path.join(clique.runtime.res_dir(), "web"),
                               sub_path=[{'url': '/ambiency',
                                          'path': ambiency_path}])
    logging.debug("Success start time app.")
  except:
    logging.exception("Failed to start the Test.")
    raise


if __name__ == "__main__":
  start()
