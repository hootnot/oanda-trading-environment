import unittest
import yachain

import os
import sys

testcfg = None


def logit(f):
    def wijzig(*args):
        rv = f(*args)
        print >>sys.stderr, "LOG: ", rv
        print >>sys.stderr, retValue
        return rv
    return wijzig


class Test_Config(unittest.TestCase):
    def setUp(self):
        global testcfg
        testcfg = yachain.Config()
        testcfg.load("etc/OANDA/config/OANDAd.cfg")

    def test_openfailure(self):
        cfg = None
        with self.assertRaises(IOError) as cm:
            cfg = yachain.Config()
            cfg.load("etc/nonexistant.cfg")

    def test_NoDataError(self):
        cfg = None
        with self.assertRaises(yachain.NoDataError) as cm:
            cfg = yachain.Config()
            cfg["daemon::user"]

    def test__domain(self):
        """ TEST: get domain from config, should return domainname
        """
        self.assertEqual(testcfg['environment'], "practice")

    def test__schedule(self):
        """ TEST: get schedule from config, should return schedule
        """
        self.assertEqual({"schedule": testcfg['schedule'],
                          "token": testcfg['access_token'],
                          }, {
           "schedule": {'till': 'friday, 23:00', 'from': 'sunday, 23:00'},
           "token": "_token_from_oanda_here_",
        })

    def test__schedule_from(self):
        """ TEST: get schedule 'from' from config, should return day, time
        """
        self.assertEqual({"from": testcfg['schedule::from'],
                          }, {
           'from': 'sunday, 23:00',
        })

    def test__timeframes(self):
        """ TEST: get timeframes from config, should return dict of timeframes
        """
        self.assertEqual({"timeframes": testcfg['timeframes'],
                          }, {
           "timeframes": {'M1': '1 Minute', 'M5': '5 Minutes',
                          'M15': '15 Minutes'},
        })


if __name__ == "__main__":

    unittest.main()
