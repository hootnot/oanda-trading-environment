import signal
import oandapy
import logging

import os
import sys

# from oanda_trading_environment.candlefactory import StreamRecord
# from .streamrecord import StreamRecord
import streamrecord

HBTIME_OUT = 10
TICKTIME_OUT = 30

logger = logging.getLogger(__name__)


def timeoutHandler(signum, frame):
    logger.warn("TIMEOUT ... exiting pid %d" % os.getpid())
    sys.exit(1)


class DisconnectException(Exception):
    pass


class TimeoutException(Exception):
    pass


class Streamer(oandapy.Streamer):
    """
        class to parse the OANDA stream

        tick records are processed into candles of different timeframes
        candles that are ready are processed by the plugin manager
    """
    def __init__(self, *args, **kwargs):
        self.logFile = kwargs['streamLog']
        del kwargs['streamLog']
        self.ONsuccess = kwargs['on_success']
        del kwargs['on_success']
        super(Streamer, self).__init__(*args, **kwargs)
        self.ticks = 0
        self.last_tick_stamp = None
        self.hb_interval_ticks = 0
        signal.signal(signal.SIGALRM, timeoutHandler)
        signal.alarm(HBTIME_OUT)

    def start(self, ignore_heartbeat=False, **params):
        # We want the heartbeats
        super(Streamer, self).start(ignore_heartbeat, **params)

    def on_success(self, data):

        r = streamrecord.StreamRecord(data)
        if r.recordtype() == streamrecord.TICK:
            self.ticks += 1
            self.hb_interval_ticks += 1
            self.last_tick_stamp = r.dt
            self.ONsuccess(r)

        elif r.recordtype() == streamrecord.HEARTBEAT:
            logger.info("heartbeat: %s" % (r['time'],))
            logger.info("processed # %d ticks" % (self.hb_interval_ticks,))
            self.hb_interval_ticks = 0
            self.ONsuccess(r)
            signal.alarm(HBTIME_OUT)

            if abs((r.dt - self.last_tick_stamp).total_seconds()) > TICKTIME_OUT:
                logger.warn("at %s NO TICKS FOR: %.5f seconds" %
                            (self.last_tick_stamp,
                             abs((r.dt -
                                  self.last_tick_stamp).total_seconds())))

        else:
            signal.alarm(HBTIME_OUT)
            logger.error("unknown record type %s\n" % (data,))
            raise TimeoutException()

        if self.logFile:
            self.logFile.write("%s\n" % r)
            self.logFile.flush()

    def on_error(self, data):
        if self.logFile:
            self.logFile.flush()
        self.disconnect()
        logger.error("disconnect %s\n" % (data,))
        raise DisconnectException()
