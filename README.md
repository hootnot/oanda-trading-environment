OANDA Trading Environment
===================================

The OANDA Trading Environment is built using the OANDA REST-API by making use of the [https://github.com/oanda/oandapy](https://github.com/oanda/oandapy) API-wrapper.

Streaming Candles
-----------------

Main part is the **OANDAd** daemon that parses the streaming quotes in 
configurable timeframes, by 1 minute, 5 minutes, 15 minutes etc. This makes it
produce streaming candles.

Candle data:

      {"data": {"instrument": "EUR_JPY",
                "granularity" : "M1",
                "start": "2015-09-02 15:36:00"
                "end": "2015-09-02 15:37:00",
                "data": {"high": 134.967, 
                         "open": 134.962,
                         "last": 134.9565,
                          "low": 134.9475,
                       "volume": 19
                 },
               }
       }

The larger timeframes can be requested using the API.

Actions
-------

When a timeframe is completed it can be handled by one or more plugins.
Plugins have a configfile based on the name of the plugin-file, but in lowercase.

The environment comes with a few plugins:

### Publish/Subscribe - plugin

This plugin can be configured to 'publish' the candle using a publisher/subscriber mechanism. This is achieved by using the [0MQ](http://zeromq.org)
library and the python binding for it: pyzmq

Other trading applications can easily subscribe to receive the quotes.

This plugin is enabled by default.

### Plainfile - plugin

This plugin can be configured to write candle records to a flatfile in a directory structure. 

Example:

     /tmp/oandadb
     |-- BCO_USD
     |   |-- M1
     |   |   `-- cache
     |   |-- M15
     |   |   `-- cache
     |   `-- M5
     |       `-- cache
     |-- DE30_EUR
     |   |-- M1
     |   |   `-- cache
     |   |-- M15
     |   |   `-- cache
     |   `-- M5
     |       `-- cache
     |-- EUR_CHF
     |   |-- M1
     |   |   `-- cache
     |   |-- M15
     |   |   `-- cache
     |   `-- M5
     |       `-- cache
     |-- EUR_GBP
     |   |-- M1
     |   |   `-- cache
     |   |-- M15
     |   |   `-- cache
     |   `-- M5
     |       `-- cache
     |-- EUR_JPY
     |   |-- M1
     |   |   `-- cache
     |   |-- M15
     |   |   `-- cache
     |   `-- M5
     |       `-- cache
     |-- EUR_USD
         |-- M1
         |   `-- cache
         |-- M15
         |   `-- cache
         `-- M5
             `-- cache


### MySQL - plugin

The MySQL plugin can be configured to insert records into a database. This plugin is provided as an example, since it needs details that depend on your
databasemodel.


Specs and Prerequisites
------------------------

To access the OANDA services you will need a token, see [https://developer.oanda.com](https://developer.oanda.com) for details.


### Quick start

After installing you **need** to configure the environment by editing the
config file 'etc/OANDA/config/OANDAd.cfg'. This is a YAML based configfile.

Configure the **environment** and the **token**. Alter the list of instruments 
you want to follow. 

The pubsub plugin publishes by default at localhost, port 5550. These can 
be altered in the 'pubsub' config: 'etc/OANDA/config/plugins/broadcast'.

#### Controlling OANDAd

OANDAd is built using [daemoncle](https://github.com/jnrbsn/daemonocle). The 'start',
'status' and 'stop' commands are implemented. The daemon forks itself and the child
will process the stream. When there are issues, TIME-OUT for instance, the child will
exit and a new child will be spawned. 

      $ OANDAd start 
      Starting OANDAd ... OK

      $ OANDAd status
      OANDAd -- pid: 51931, status: sleeping, uptime: 0m, %cpu: 0.0, %mem: 1.8

      $ OANDAd stop
      Stopping OANDAd ... OK


The daemon will process streaming quotes now and process the timeframes
as configured. Timeframes are currently based on the midprice of bid/ask.

### Logging

The ticks received from the stream are written to a logfile:

     quoteStream.log<date>


### ZMQ - client

This simple piece of code acts as a subscriber to the daemon. All completed timeframes are written to stdout.

     import zmq

     context = zmq.Context()
     socket = context.socket( zmq.SUB)
     socket.connect("tcp://127.0.0.1:5550")
     socket.setsockopt(zmq.SUBSCRIBE, "")

     socket.setsockopt( zmq.RCVBUF, 1000)
     while True:
       msg = socket.recv()
       print "GOT: ", msg

