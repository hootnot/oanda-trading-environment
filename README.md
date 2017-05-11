OANDA Trading Environment
===================================

[![PyPI version](https://badge.fury.io/py/oanda-trading-environment.svg)](http://badge.fury.io/py/oanda-trading-environment)

The OANDA Trading Environment is built using the OANDA REST-API by making use of the [https://github.com/oanda/oandapy](https://github.com/oanda/oandapy) API-wrapper.

Streaming Candles
-----------------

Main part is the **OANDAd** daemon that parses the streaming quotes in 
configurable timeframes, by 1 minute, 5 minutes, 15 minutes etc. This makes it
produce streaming candles.

Candle data:
```python
      {"data": {"instrument": "EUR_JPY",
                "granularity" : "M1",
                "start": "2015-09-02 15:36:00"
                "end": "2015-09-02 15:37:00",
                "completed": True,
                "data": {"high": 134.967, 
                         "open": 134.962,
                         "last": 134.9565,
                          "low": 134.9475,
                       "volume": 19
                 },
               }
       }
```
The larger timeframes can be requested using the API.

Streaming data can be controlled by the 'fabricate' setting in the 'streamer:' 
config section. 

* atEndOfTimeFrame - the default mode is to fabricate completed timeframes
* dancingBear - generates _dancing bear_ records with the 'completed' : False, until the record is completed. At that moment the record gets the status 'completed' : True.
* dancingBearHighLowExtreme - generate _dancing bear_ records *only* when the high or the low changes

The _dancingBear_ setting generates as many records as ticks are received. This
can be a lot. A compromise is the _dancingBearHighLowExtreme_. In case of extreme
market moves the records will be generated also, but in a less volatile market
less records will be generated.

Actions
-------

When a timeframe is completed it can be handled by one or more plugins.
Plugins have a configfile based on the name of the plugin-file, but in lowercase.
The plugins can be found under _etc/OANDA/plugins_ and the plugin configs under _etc/OANDA/config/plugins_.

Plugins need to be enabled in the config file, see the 'plugins:' section in _etc/OANDA/config/OANDAd.cfg_.

The environment comes with a few plugins:

### Publish/Subscribe - plugin

This plugin can be configured to 'publish' the candle using a publisher/subscriber mechanism. This is achieved by using the [0MQ](http://zeromq.org)
library and the python binding for it: pyzmq

Other trading applications can easily subscribe to receive the candle data. See [here](#zmq_example) for a ZMQ subscription example.

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

Auto trading
-------------

### By using a ZMQ client

The desired approach is to create stand-alone applications that subscribe for quotes,
see, [example](#zmq_example) for a ZMQ subscription example.

### By using plugins

Though it is possible to use the plugin facility to perform auto-trading, the
way to go is to use ZMQ client and subscribe for quotes. This way you can
completely isolate your trading code from the OANDAd daemon.


Security
----------------

The enviroment makes use of a token that gives access to crucial information.

Please pay attention to where you install this software. **Never** use this on
a system that is not owned by you. 

Make sure to secure your system as much as possible:

* restrict network access
* make no use of, or limit other network services (NFS, SAMBA, printserver etc.)
* limit user access, preferable only you
* use encryption
* who about physical access ?


Specs and Prerequisites
------------------------

To access the OANDA services you will need a token, see [https://developer.oanda.com](https://developer.oanda.com) for details.

Install
-------

### Git

Install by using a virtual environment and git:
```bash
      $ cd <somewhere>
      $ mkdir OANDA
      $ cd OANDA
      $ virtualenv venv
```

Optionally use _--system-site-packages_ to use the standard available packages for the python modules available
on your system: _pyyaml_, _pyzmq_. Check for the packages on the distribution you use.

```bash
      $ . ./venv/bin/activate
      $ git clone https://github.com/hootnot/oanda-trading-environment.git
      $ cd oanda-trading-environment
      $ python setup.py install
```

OANDA has not made the oandapy module pip installable.
A hack to get oandapy installed as a standalone module:

```bash
      $ pip install git+https://github.com/hootnot/oandapy
```

This will install the latest oandapy using the setup.py from the oandapy fork.
```bash
      $ pip list | grep oanda
      oanda-trading-environment (0.0.1)
      oandapy (0.1)
```

### pip

Install from pypi:

using a virtual environment:

```bash
      $ cd <somewhere>
      $ mkdir OANDA
      $ cd OANDA
      $ virtualenv [--system-site-packages] venv
      $ . ./venv/bin/activate
      $ pip install oanda-trading-environment
      $ pip install git+https://github.com/hootnot/oandapy
```

using a system install:

```bash
      $ sudo pip install oanda-trading-environment
      $ sudo pip install git+https://github.com/hootnot/oandapy
```

Configure the OANDAd.cfg config file and start the daemon.

### Quick start

After installing you **need** to configure the environment by editing the
config file _etc/OANDA/config/OANDAd.cfg_. This is a YAML based configfile.

Configure the **environment**, default set to _practice_ and the **token**. Alter
 the list of instruments you want to follow.

Though accounts can be requested using the API, the environment uses the
**account** setting primarily to initialize the OANDAd for the streaming quotes.
Therefore you need to configure the **account_id** also.

The pubsub plugin publishes by default at localhost, port 5550. These can 
be altered in the 'pubsub' config: _etc/OANDA/config/plugins/pubsub.cfg_.

#### Controlling OANDAd

OANDAd is built using [daemoncle](https://github.com/jnrbsn/daemonocle). The 'start',
'status' and 'stop' commands are implemented. The daemon forks itself and the child
will process the stream. When there are issues, TIME-OUT for instance, the child will
exit and a new child will be spawned. 

```bash
      $ OANDAd start 
      Starting OANDAd ... OK

      $ OANDAd status
      OANDAd -- pid: 51931, status: sleeping, uptime: 0m, %cpu: 0.0, %mem: 1.8

      $ OANDAd stop
      Stopping OANDAd ... OK
```

The daemon will process streaming quotes now and process the timeframes
as configured. Timeframes are currently based on the midprice of bid/ask.

### Logging

The ticks received from the stream are written to a logfile:

     streamdata.<date>

The daemon itself logs to OANDAd.log

Loglevel and the streamdata logfile extension is configurable. Check the _OANDAd.cfg_ file
for details.


### <a name="zmq_example"></a>ZMQ - client


This simple piece of code acts as a subscriber to the daemon. All completed timeframes are written to stdout.
Using ZMQ make it easy to program different strategies completely independent from each other. By using 'topics' 
it is possible to subscribe for a certain time granularity like M1, M5 etc. Check the ZMQ for details.

```python
     import zmq

     context = zmq.Context()
     socket = context.socket( zmq.SUB)
     socket.connect("tcp://127.0.0.1:5550")
     socket.setsockopt(zmq.SUBSCRIBE, "")

     socket.setsockopt( zmq.RCVBUF, 1000)
     while True:
         msg = socket.recv()
         print "GOT: ", msg
```

This will show candle data like below, every time a timeframe is completed.

```python
     GOT:  {"data": {
                     "instrument": "EUR_GBP",
                     "granularity": "M1",
                     "start": "2015-09-04 17:45:00",
                     "end": "2015-09-04 17:46:00",
                     "completed": True,
                     "data": {
                              "high": 0.734445,
                              "open": 0.734399,
                              "last": 0.73437,
                              "low": 0.734345,
                              "volume": 16
                             }
                    }
           }

     GOT:  {"data": {
                     "instrument": "EUR_JPY",
                     "granularity": "M1",
                     "start": "2015-09-04 17:45:00",
                     "end": "2015-09-04 17:46:00",
                     "completed": True,
                     "data": {
                              "high": 132.629,
                              "open": 132.619,
                              "last": 132.6185,
                              "low": 132.608,
                              "volume": 15
                             }
                    }
            }

     GOT:  {"data": {
                     "instrument": "SPX500_USD",
                     "granularity": "M1",
                     "start": "2015-09-04 17:45:00",
                     "end": "2015-09-04 17:46:00",
                     "completed": True,
                     "data": {
                              "high": 1915.35,
                              "open": 1914.75,
                              "last": 1915.25,
                              "low": 1914.75,
                              "volume": 33
                             }
                    }
            }
```

About this software
-------------------
The *oanda-trading-environment* software is a personal project.
I have no prior or existing relationship with OANDA.

If you have any questions regarding this software, please take a look at
the documentation first.

If you still have questions/issues you can open an *issue* on Gitub: https://github.com/hootnot/oanda-trading-environment
