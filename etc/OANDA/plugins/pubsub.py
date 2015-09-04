from oanda_trading_environment.daemon.plugin import Plugin
import zmq
import json

import logging

logger = logging.getLogger(__name__)


class PubSub(Plugin):
    def __init__(self, config=None):
        super(PubSub, self).__init__(config=config)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        logger.info("ZMQ context PUB: %s:%d" %
                    (self.config['host'], self.config['port']))
        self.socket.bind("tcp://%s:%d" %
                         (self.config['host'], self.config['port']))
        self.socket.setsockopt(zmq.SNDBUF, 100)

    def execute(self, data):
        # logger.info("%s %s" % (self.__class__.__name__, json.dumps(data)))
        self.socket.send(json.dumps({"data": data}))

if __name__ == "__main__":
    import sys
    import time
    from oanda_trading_environment.daemon.config import Config
    config = Config(sys.argv[1])
    b = PubSub(config=config)
    data = {"a": "Aaa"}
    while True:
        b.execute(data)
        time.sleep(1)
