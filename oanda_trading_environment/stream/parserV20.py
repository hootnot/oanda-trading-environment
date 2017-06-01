import signal
from oandapyV20 import API
import oandapyV20.endpoints.pricing as pricing
from oandapyV20.exceptions import V20Error, StreamTerminated
from requests.exceptions import ConnectionError
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


def V1compat(t):
    """V1compat - create a V1 compatible tick record from a V20 tick."""
    T = t['time']
    T = T[0:len(T)-4]+"Z"
    rv = dict()

    if t['type'] == 'PRICE':
        rv = {"tick": {"instrument": t['instrument'],
                       "time": T,
                       "bid": float(t['bids'][0]['price']),
                       "ask": float(t['asks'][0]['price'])}
              }
    else:
        rv = {'heartbeat': {"time": T}}

    return rv


class DisconnectException(Exception):
    pass


class TimeoutException(Exception):
    pass


class V20Streamer(object):
    """
        class to parse the OANDA V20 stream written to be compatible
        with the Streamer class based on the V1-REST

        tick records are processed into candles of different timeframes
        candles that are ready are processed by the plugin manager
    """
    def __init__(self, *args, **kwargs):
        self.logFile = kwargs['streamLog']
        del kwargs['streamLog']
        self.ONsuccess = kwargs['on_success']
        del kwargs['on_success']
        self.access_token = kwargs['access_token']
        del kwargs['access_token']
        self.environment = kwargs['environment']
        del kwargs['environment']
        self.ticks = 0
        self.last_tick_stamp = None
        self.hb_interval_ticks = 0
        signal.signal(signal.SIGALRM, timeoutHandler)
        signal.alarm(HBTIME_OUT)

    def start(self, ignore_heartbeat=False, **kwargs):
        # We want the heartbeats by default
        client = API(access_token=self.access_token,
                     environment=self.environment)

        params = {"instruments": kwargs["instruments"]}
        r = pricing.PricingStream(accountID=kwargs['accountId'], params=params)
        logging.info("Request is: %s with instruments: %s",
                     r, params['instruments'])

        while True:
            try:
                for tick in client.request(r):
                    logging.info("TICK: %s", tick)
                    self.on_success(V1compat(tick))

            except V20Error as e:
                # catch API related errors that may occur
                logger.error("V20Error: %s", e)
                break

            except ConnectionError as e:
                logger.error("Connection Error: %s", e)
                break

            except StreamTerminated as e:
                logger.error("StreamTerminated exception: %s", e)
                break

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                logger.error("Unknown exception: %s | %s | %s",
                             exc_type, fname, exc_tb.tb_lineno)
                break

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

            tDiff = abs((r.dt - self.last_tick_stamp).total_seconds())
            if tDiff > TICKTIME_OUT:
                logger.warn("at %s NO TICKS FOR: %.5f seconds" %
                            (self.last_tick_stamp,
                             abs((r.dt -
                                  self.last_tick_stamp).total_seconds())))

        else:
            signal.alarm(HBTIME_OUT)
            logger.error("unknown record type %s" % (data,))
            raise TimeoutException()

        if self.logFile:
            self.logFile.write("%s\n" % r)
            self.logFile.flush()

    def on_error(self, data):
        if self.logFile:
            self.logFile.flush()
        self.disconnect()
        logger.error("disconnect %s" % (data,))
        raise DisconnectException()
