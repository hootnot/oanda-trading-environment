r""" Config related functionality.

This module provides access to configuration files in YAML markup

"""

import yaml
import re
from os import path


class Config(object):

    def __init__(self, configdata=None, prefix=None, tokenseparator="::"):
        """
           Config - handle configfiles in yaml markup
           config data is accessible via overloaded __getitem__

           To support configcontent relative to some directory a <prefix> can be passed
           acting as the <root>-directory for paths configured in the config file.

           All attributes in the config having 'path' or 'file' in their name will be
           altered automatically by prepending the prefix.
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
        with open(filename) as CFG:
            self.data = yaml.load(CFG.read())

    def __getitem__(self, k):
        """
           return configuration item by key

           >>> from ... import Config
           >>> c = Config(CONFIG_FILE)
           >>> print c["daemon::user"]
           oanda
           >>> print c["daemon::logfile"]
           /var/log/OANDA/OANDAd.log

           >>> c2 = Config(CONFIG_FILE, "/somewhere/else")
           >>> print c["daemon::user"]
           oanda
           >>> print c["daemon::logfile"]
           /somewhere/else/var/log/OANDA/OANDAd.log
        """
        def _gv_(data, keywords):
            # recursively traverse the data structure untile the last key
            # it it is a file or path prepend the prefix if there is a prefix
            currentKey = keywords.pop(0)
            if keywords:
                return _gv_(data[currentKey], keywords)
            else:
                if self.prefix and re.match("^.*(file|path)$", currentKey):
                    return path.join(self.prefix, data[currentKey].lstrip("/"))
                else:
                    return data[currentKey]

        return _gv_(self.data, k.split("::"))
