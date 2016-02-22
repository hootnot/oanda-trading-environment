import unittest
from oanda_trading_environment.daemon import config

import os
import sys

testcfg = None
OAPREFIX = "/tmp"


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
        testcfg = config.Config(prefix=OAPREFIX)
        testcfg.load("etc/OANDA/config/OANDAd.cfg")

    def test_openfailure(self):
        cfg = None
        with self.assertRaises(IOError) as cm:
            cfg = config.Config()
            cfg.load("etc/nonexistant.cfg")

    def test_NoDataError(self):
        cfg = None
        with self.assertRaises(config.NoDataError) as cm:
            cfg = config.Config()
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

    def test__abspath(self):
        """ TEST: get parameter with absolute path"
        """
        self.assertEqual({"pidfile": testcfg['daemon::pidfile'],
                          }, {
           'pidfile': '/var/run/OANDA/OANDAd.pid'
        })

    def test__relpath(self):
        """ TEST: get parameter with relative path"
        """
        self.assertEqual({"logfile": testcfg['daemon::logfile'],
                          }, {
           'logfile': os.path.join(OAPREFIX, 'var/log/OANDA/OANDAd.log')
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
