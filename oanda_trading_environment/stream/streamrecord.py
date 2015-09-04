import json
import calendar
from datetime import datetime

"""
{"tick": {"ask": 10901.4, "instrument": "DE30_EUR", "bid": 10898.9,
                                 "time": "2015-08-18T17:15:14.574448Z"}}
{"heartbeat": {"time": "2015-08-18T17:15:26.743512Z"}}
"""
mid_bid_ask = 4

TICK = 1
HEARTBEAT = 2


class UnknownStreamRecord(Exception):
    pass


class StreamRecord(object):
    """
       StreamRecord - convert OANDA streamrecord
    """
    def __init__(self, s, mode=mid_bid_ask):
        # accept JSON data aswell as stringdata to convert to JSON
        j = json.loads(s) if isinstance(s, str) else s
        # use calendar.timegm, this gives back the correct time without
        # timezone differences
        self.rtype = None
        self.data = {}
        if "tick" in j:
            j = j["tick"]
            self.dt = datetime.strptime(j['time'], '%Y-%m-%dT%H:%M:%S.%fZ')
            self.epoch = int(calendar.timegm(self.dt.timetuple()))
            self.rtype = TICK
            self.data['instrument'] = j["instrument"]
            self.data['time'] = j["time"]
            self.data['bid'] = j["bid"]
            self.data['ask'] = j["ask"]
            self.data['mid'] = (j['bid'] + j['ask'])/2.0
            self.data['value'] = self.data['mid']
        elif "heartbeat" in j:
            self.rtype = HEARTBEAT
            j = j["heartbeat"]
            self.dt = datetime.strptime(j['time'], '%Y-%m-%dT%H:%M:%S.%fZ')
            self.epoch = int(calendar.timegm(self.dt.timetuple()))
            self.data['time'] = j['time']
        else:
            raise UnknownStreamRecord(s)

    def recordtype(self):
        return self.rtype

    def __getitem__(self, k):
        return self.data[k]

    def __repr__(self):
        return json.dumps(self.data)
