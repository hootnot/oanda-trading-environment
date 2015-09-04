Plugin Modules
=================

Plugin modules need to be derived from the 

     oanda_trading_environment.daemon.plugin.Plugin

class. Otherwise the code will not be loaded as a plugin.


Blocking
---------

The daemon processes the modules sequentially. Depending on the type of plugin blocking issues may occur (such as unreachable database server).
