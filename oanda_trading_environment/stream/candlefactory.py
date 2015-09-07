import sys
import time
from datetime import datetime
import re
from streamrecord import HEARTBEAT
import logging

"""
{"tick": {"ask": 10901.4, "instrument": "DE30_EUR", "bid": 10898.9,
                                 "time": "2015-08-18T17:15:14.574448Z"}}
{"heartbeat": {"time": "2015-08-18T17:15:26.743512Z"}}
"""

atEndOfTimeFrame = 1
dancingBear = 2
dancingBearHighLowExtreme = 3

logger = logging.getLogger(__name__)


class UnknownGranularity(Exception):
    pass


def granularity_to_time(s):
    """
       get value in seconds for named granularities: M1, M5 ... H1 etc.
    """
    mfact = {
        'S': 1,
        'M': 60,
        'H': 3600,
        'D': 86400,
    }
    try:
        f, n = re.match("(?P<f>[SMHD])(?:(?P<n>\d+)|)", s).groups()
        n = n if n else 1
        return mfact[f] * int(n)
    except:
        raise UnknownGranularity(s)


class CandleFactory(object):

    def __init__(self, instrument, granularity, processingMode='atEndOfTimeFrame'):
        self.instrument = instrument
        self.frameTime = granularity_to_time(granularity)
        self.granularity = granularity
        self.data = None
        self.start = None
        self.end = None
        self.processing = None
        self.processingMode = processingMode
        try:
            self.processing = getattr(sys.modules[__name__], self.processingMode)
        except:
            logger.error("unknown processing mode: %s" % self.processingMode)

            self.processingMode = "atEndOfTimeFrame"
            self.processing = getattr(sys.modules[__name__], self.processingMode)
            logger.info("fallback to processing mode: %s" % self.processingMode)
        else:
            logger.info("processing mode: %s" % self.processingMode)

    def initData(self, tick):
        # init the frame
        # calculate the boundaries based on the tick timestamp
        self.start = tick.epoch - (tick.epoch % self.frameTime)
        self.end = tick.epoch - (tick.epoch % self.frameTime) + self.frameTime
        self.data = {
            "instrument": self.instrument,
            "start": "%s" % self.secs2time(self.start),
            "end": "%s" % self.secs2time(self.end),
            "granularity": self.granularity,
            "completed": False,
            "data": {
                "open": tick.data['value'],
                "high": tick.data['value'],
                "low": tick.data['value'],
                "last": tick.data['value'],
                "volume": 1
            }
        }

    def secs2time(self, e):
        w = time.gmtime(e)
        return datetime(*list(w)[0:6])

    def make_candle(self, completed=False):
        self.data['completed'] = completed
        return self.data.copy()

    def processTick(self, tick):
        if tick.recordtype() == HEARTBEAT:
            if self.data and tick.epoch > self.end:
                # this frame is completed based on the heartbeat timestamp
                candle = self.make_candle(completed=True)
                self.data = None     # clear it, reinitialized by the next tick
                logger.warn("infrequent ticks: %s, %s completed with "
                            "heartbeat (%d secs)" %
                            (self.instrument, self.granularity,
                             (tick.epoch - self.end)))
                return candle
            else:
                return

        # so it is TICK record
        if not tick['instrument'] == self.instrument:
            return

        if not self.data:
            # print "initData(...)"
            self.initData(tick)
            return None

        # ... we got data already
        # is this tick for this frame ? ... process it
        if tick.epoch >= self.start and tick.epoch < self.end:
            extremeChange = False
            lastChange = False
            if tick.data['value'] > self.data['data']['high']:
                self.data['data']['high'] = tick.data['value']
                extremeChange = True
            if tick.data['value'] < self.data['data']['low']:
                self.data['data']['low'] = tick.data['value']
                extremeChange = True
            if tick.data['value'] != self.data['data']['last']:
                self.data['data']['last'] = tick.data['value']
                lastChange = True
            self.data['data']['volume'] += 1
            if (self.processing == dancingBear and lastChange) or \
               (self.processing == dancingBearHighLowExtreme and extremeChange):
                logger.info("mode: %s change of extremes for %s, %s" %
                            (self.processingMode, self.instrument,
                             self.granularity))
                return self.make_candle()
            return None

        # this tick not within boundaries ?
        # the 'current' is completed
        candle = self.make_candle(completed=True)
        self.initData(tick)
        return candle
