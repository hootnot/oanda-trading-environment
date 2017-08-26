import unittest
from oanda_trading_environment.stream import CandleFactory, StreamRecord
from oanda_trading_environment.stream import granularity_to_time


# """  {"heartbeat": {"time": "2015-08-21T06:11:57.682301Z"}} """,
test_ticks = {}
test_ticks.update({"M1": [
  """ {"tick": {"ask": 10200.0, "instrument": "DE30_EUR", "bid": 10190.0,
       "time": "2015-08-21T06:11:38.682301Z"}} """,
  """  {"tick": {"ask": 10180.0, "instrument": "DE30_EUR", "bid": 10170.0,
        "time": "2015-08-21T06:11:50.682301Z"}} """,
  """  {"tick": {"ask": 10220.0, "instrument": "DE30_EUR", "bid": 10210.0,
        "time": "2015-08-21T06:11:55.682301Z"}} """,
  """  {"heartbeat": {"time": "2015-08-21T06:11:57.682301Z"}} """,
  """  {"tick": {"ask": 10205.0, "instrument": "DE30_EUR", "bid": 10195.0,
        "time": "2015-08-21T06:11:58.682301Z"}} """,
  """  {"tick": {"ask": 10230.0, "instrument": "DE30_EUR", "bid": 10220.0,
        "time": "2015-08-21T06:12:00.682301Z"}} """,
]})
test_ticks.update({"M5": [
  """ {"tick": {"ask": 10200.0, "instrument": "DE30_EUR", "bid": 10190.0,
       "time": "2015-08-21T06:10:01.682301Z"}} """,
  """  {"tick": {"ask": 10180.0, "instrument": "DE30_EUR", "bid": 10170.0,
        "time": "2015-08-21T06:11:50.682301Z"}} """,
  """  {"tick": {"ask": 10220.0, "instrument": "DE30_EUR", "bid": 10210.0,
        "time": "2015-08-21T06:13:55.682301Z"}} """,
  """  {"heartbeat": {"time": "2015-08-21T06:13:57.682301Z"}} """,
  """  {"tick": {"ask": 10205.0, "instrument": "DE30_EUR", "bid": 10195.0,
        "time": "2015-08-21T06:14:55.682301Z"}} """,
  """  {"tick": {"ask": 10230.0, "instrument": "DE30_EUR", "bid": 10220.0,
        "time": "2015-08-21T06:15:00.682301Z"}} """,
]})
test_ticks.update({"M15": [
  """  {"tick": {"ask": 10200.0, "instrument": "DE30_EUR", "bid": 10190.0,
        "time": "2015-08-21T06:00:01.682301Z"}} """,
  """  {"tick": {"ask": 10180.0, "instrument": "DE30_EUR", "bid": 10170.0,
        "time": "2015-08-21T06:11:50.682301Z"}} """,
  """  {"tick": {"ask": 10220.0, "instrument": "DE30_EUR", "bid": 10210.0,
        "time": "2015-08-21T06:13:55.682301Z"}} """,
  """  {"heartbeat": {"time": "2015-08-21T06:13:57.682301Z"}} """,
  """  {"tick": {"ask": 10205.0, "instrument": "DE30_EUR", "bid": 10195.0,
        "time": "2015-08-21T06:14:55.682301Z"}} """,
  """  {"tick": {"ask": 10230.0, "instrument": "DE30_EUR", "bid": 10220.0,
        "time": "2015-08-21T06:15:00.682301Z"}} """,
]})
test_ticks.update({"H1": [
  """  {"tick": {"ask": 10200.0, "instrument": "DE30_EUR", "bid": 10190.0,
        "time": "2015-08-21T06:00:01.682301Z"}} """,
  """  {"tick": {"ask": 10180.0, "instrument": "DE30_EUR", "bid": 10170.0,
        "time": "2015-08-21T06:11:50.682301Z"}} """,
  """  {"tick": {"ask": 10220.0, "instrument": "DE30_EUR", "bid": 10210.0,
        "time": "2015-08-21T06:13:55.682301Z"}} """,
  """  {"heartbeat": {"time": "2015-08-21T06:13:57.682301Z"}} """,
  """  {"tick": {"ask": 10205.0, "instrument": "DE30_EUR", "bid": 10195.0,
        "time": "2015-08-21T06:55:55.682301Z"}} """,
  """  {"tick": {"ask": 10230.0, "instrument": "DE30_EUR", "bid": 10220.0,
        "time": "2015-08-21T07:00:00.682301Z"}} """,
]})

# mid prices of records above
# 10195
# 10175
# 10215
# 10200

# 10225 -> makes M1 rec.: Open, High, Low, Last, Vol = 195, 215, 175, 200, 4
#          initialize next M1
# 10245 ->
candles = {
  "M1": {'instrument': 'DE30_EUR',
         'start': '2015-08-21 06:11:00',
         'end': '2015-08-21 06:12:00',
         'granularity': 'M1',
         'completed': True,
         'data': {'high': 10215.0,
                  'open': 10195.0,
                  'last': 10200.0,
                  'low': 10175.0,
                  'volume': 4},
         },
  "M5": {'instrument': 'DE30_EUR',
         'start': '2015-08-21 06:10:00',
         'end': '2015-08-21 06:15:00',
         'granularity': 'M5',
         'completed': True,
         'data': {'high': 10215.0,
                  'open': 10195.0,
                  'last': 10200.0,
                  'low': 10175.0,
                  'volume': 4},
         },
  "M15": {'instrument': 'DE30_EUR',
          'start': '2015-08-21 06:00:00',
          'end': '2015-08-21 06:15:00',
          'granularity': 'M15',
          'completed': True,
          'data': {'high': 10215.0,
                   'open': 10195.0,
                   'last': 10200.0,
                   'low': 10175.0,
                   'volume': 4},
          },
  "H1": {'instrument': 'DE30_EUR',
         'start': '2015-08-21 06:00:00',
         'end': '2015-08-21 07:00:00',
         'granularity': 'H1',
         'completed': True,
         'data': {'high': 10215.0,
                  'open': 10195.0,
                  'last': 10200.0,
                  'low': 10175.0,
                  'volume': 4},
         },
}

candle_factory = None
testdata = None
TICKDATA = ""


class Test_candlefactory(unittest.TestCase):
    def setUp(self):
        global candle_factory
        global testdata
        candle_factory = CandleFactory("DE30_EUR", "M1")
        # testdata = [T for T in test_ticks.split("\n") if T]

    def test_addtick1(self):
        """ initialize with 1st tick, frame is not completed,
            None should be returned
        """
        testdata = test_ticks["M1"]
        r = candle_factory.processTick(StreamRecord(testdata[0]))
        self.assertEqual(r, None)

    def test_frames(self):
        """ ticks that make a timeframe : atEndOfTimeFrame
            candle data should be returned
            perform this for given granularities
        """
        self.maxDiff = None
        for F in ["M1", "M5", "M15", "H1"]:
            testdata = test_ticks[F]
            candle_factory = CandleFactory("DE30_EUR", F,
                                           processingMode='atEndOfTimeFrame')
            res = []
            for T in testdata:
                r = candle_factory.processTick(StreamRecord(T))
                res.append(r)
            self.assertEqual(res, [None, None, None, None, None, candles[F]])

    def test_numerical_granularity(self):
        """ initialize a timeframe, diff between end - start should
            correspond with the numerical equivalent of the granularity
        """
        cft = 0
        grt = 0
        for G in ["M1", "M5", "M15", "H1"]:
            testdata = test_ticks[G]
            cf = CandleFactory("DE30_EUR", G)
            r = cf.processTick(StreamRecord(testdata[0]))
            cft += (cf.end - cf.start)
            grt += granularity_to_time(G)

        self.assertEqual(cft, grt)

    @unittest.skipIf(TICKDATA == "", "Tickdata not set")
    def test_addtick4(self):
        """ simulate the processing of a large period of ticks
            the corresponding number of candles for each timeframe should
            be generated
        """
        # candleCountKnown = {"M1": 6, "M5": 1,
        #                     "M15": 1, "H1": 1, "H4": 1, "D": 1}

        candleCountKnown = {"M1": 927, "M5": 187,
                            "M15": 63, "H1": 16, "H4": 5, "D": 2}

        candleCountReal = {}
        for G in candleCountKnown.keys():
            cf = CandleFactory("DE30_EUR", G)
            n = 0
            with open(TICKDATA) as I:
                for tick in I:
                    if tick[0] == '#':
                        continue
                    r = cf.processTick(StreamRecord(tick))
                    if r:
                        n += 1

            candleCountReal.update({G: n})

        self.assertEqual(candleCountKnown, candleCountReal)


if __name__ == "__main__":

    unittest.main()
