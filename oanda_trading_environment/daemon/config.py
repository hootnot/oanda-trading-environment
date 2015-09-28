r""" Config related functionality.

This module provides access to configuration files in YAML markup

"""

import yaml
import re
from os import path


class NoDataError(Exception):
    """ No config data available """


class Config(object):

    def __init__(self, configdata=None, prefix=None, tokenseparator="::"):
        """
           Config - handle configfiles in yaml markup
           config data is accessible via overloaded __getitem__

           Config data can be loaded from a config file user the load(..) method or
           by passing it data as a dict when creating a Config instance.

           All attributes in the config having 'path' or 'file' in their name will be
           altered automatically by prepending the prefix if it concerns relative paths

           If no data is available, a NoDataError will be raised
        """
        self.data = None
        self.prefix = prefix
        self.tokenseparator = tokenseparator
        if configdata:
            self.data = configdata

    def load(self, filename):
        """
           read configdata from file :filename
        """
        self.filename = filename
        with open(filename) as CFG:
            self.data = yaml.load(CFG.read())

    def __getitem__(self, k):
        """
           return configuration item by key

           >>> from ... import Config
           >>> c = Config()
           >>> c.load(CONFIG_FILE)
           >>> print c["daemon::user"]
           oanda
           >>> print c["daemon::logfile"]
           var/log/OANDA/OANDAd.log
           >>> print c["daemon::pidfile"]
           /var/run/OANDA/OANDAd.pid

           The same, but now with a prefix passed:

           >>> c2 = Config(prefix="/somewhere/else")
           >>> c2.load(CONFIG_FILE)
           >>> print c["daemon::user"]
           oanda
           >>> print c["daemon::logfile"]
           /somewhere/else/var/log/OANDA/OANDAd.log
           >>> print c["daemon::pidfile"]
           /var/run/OANDA/OANDAd.pid

           the relative path has got the prefix prepended.
        """
        def _gv_(data, keywords):
            # recursively traverse the data structure untile the last key
            # if it is a file or path prepend the prefix if there is a prefix
            currentKey = keywords.pop(0)
            if keywords:
                return _gv_(data[currentKey], keywords)
            else:
                if self.prefix and re.match("^.*(file|path)$", currentKey):
                    return data[currentKey] if data[currentKey].startswith('/') else \
                           path.join(self.prefix, data[currentKey])
                else:
                    return data[currentKey]

        if not self.data:
            raise NoDataError("")

        return _gv_(self.data, k.split("::"))
