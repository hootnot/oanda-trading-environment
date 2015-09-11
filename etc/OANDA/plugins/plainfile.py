from oanda_trading_environment.daemon.plugin import Plugin
import os
import json

import logging

logger = logging.getLogger(__name__)


class PlainFile(Plugin):
    """
    PlainFile plugin - write price records to a flatfile directory structure
    /<databasepath>/<instrument>/<granularity>/<cache>
    """

    def __init__(self, config=None):
        super(PlainFile, self).__init__(config=config)
        self.database = config['database']

    def execute(self, data):
        # logger.info("%s %s" % (self.__class__.__name__, json.dumps(data)))

        # write only completed records
        if not data['completed']:
            logger.info("skipping record: not state 'completed'")
            return

        fileName = os.path.join(self.database,
                                data['instrument'], data['granularity'],
                                "cache")
        if not os.path.isfile(fileName):
            dirName = os.path.dirname(fileName)
            os.makedirs(dirName) if not os.path.isdir(dirName) else False
            logger.info("created path: " + dirName)

        with open(fileName, "a") as O:
            O.write("%s,%.5f,%.5f,%.5f,%.5f,%d\n" %
                    (data['start'].replace("-", "").replace(" ", "-"),
                     data['data']['open'],
                     data['data']['high'],
                     data['data']['low'],
                     data['data']['last'],
                     data['data']['volume']))


if __name__ == "__main__":
    import sys
    import time
    from oanda_trading_environment.daemon.config import Config
    # config = Config(sys.argv[1])
    b = PlainFile(config={"database": "/tmp/db/"})
    data = {"instrument": "EUR_CHF",
            "granularity": "M1",
            "end": "2015-09-04 09:46:00",
            "start": "2015-09-04 09:45:00",
            "completed": True,
            "data": {"high": 1.08529,
                     "open": 1.085265,
                     "last": 1.08522,
                     "low": 1.0852,
                     "volume": 8},
            }
    b.execute(data)
