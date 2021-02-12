from datetime import datetime, timedelta
from collections import OrderedDict


class Common:
    TYPE_CONVERSION = {}

    def __init__(self):
        self.TYPE_CONVERSION = {
            "INT": "Int64",
            "FLOAT": 'float64',
            "DISTRIB": 'object',
            "PERCENT": 'float64',
            "MILLISEC": 'float64',
            "DATA": 'object',
            "BOOL": 'bool',
            "STRING": 'object',
            "WORK_DUR": 'float64',
            "RATING": 'float64',
            "LEVEL": 'float64'
        }

        self.SONAR_MEASURES_TYPE = OrderedDict({
            'project': 'object',
            'analysis_key': 'object',
        })

    @staticmethod
    def process_datetime(time_str):
        if time_str is None:
            return None

        ts = datetime.strptime(time_str[:19], "%Y-%m-%dT%H:%M:%S")

        offset = timedelta(hours=int(time_str[20:22]), minutes=int(time_str[22:24]))

        if time_str[19] == '-':
            ts = ts + offset
        elif time_str[19] == '+':
            ts = ts - offset

        return ts
