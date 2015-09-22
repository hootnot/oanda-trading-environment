import sys
import os
import logging
from oanda_trading_environment.daemon.config import Config

logger = logging.getLogger(__name__)


class PluginError(Exception):
    """ generic plugin error """


class Plugin(object):
    def __init__(self, config=None):
        self.config = config

    def execute(self):
        raise Exception("override this method with your own")


class PluginManager(object):
    def __init__(self, config):
        self.plugin_path = config['plugin_path']
        self.config_path = config['config_path']
        self.config = config
        self.enabled = []
        if config['enabled']:
            self.enabled = config['enabled']
        self.pm = PluginHandler()
        sys.path.append(self.plugin_path)

    def __len__(self):
        return len(self.pm)

    def execute(self, data):
        self.pm(data)

    def load(self):
        main = sys.modules['__main__']
        main_objs = set(dir(main))

        # create a list of plugins that are configured as 'enabled'
        plugins = []
        for f in os.listdir(self.plugin_path):
            if f.endswith('.py'):
                f = f.replace('.py', '')
                if f in self.enabled:
                    logger.info("plugin added to be setup: %s" % f )
                    plugins.append(f)
                else:
                    logger.info("skipping plugin: %s, not configured as enabled" % f )

        for plugin in plugins:
            package = __import__(plugin)
            package_objs = set(dir(package))

            for obj in (package_objs - main_objs):
                setattr(main, obj, getattr(package, obj))
                class_ = getattr(package, obj)
                if ".Plugin" in str(class_):
                    continue
                if type(class_) == type:
                    if not issubclass(class_, Plugin):
                        logger.warning("SKIPPING plugin: [%s] : "
                                       "not of type Plugin\n" % obj)
                        continue

                    # print "CONFIG: ", plugin
                    cfgForInst = Config(prefix=self.config.prefix)
                    cfgForInst.load(os.path.join(self.config_path, "%s.cfg" % plugin.lower()))

                    inst = class_(config=cfgForInst)
                    logger.info("plugin loaded and configured: %s" % f )
                    self.pm += inst


class PluginHandler(object):

    def __init__(self):
        self.handlers = set()

    def __iadd__(self, handler):
        # sys.stderr.write("%s ... adding handler: %s" % \
        #      ( self.__class__.__name__, handler.__class__ ))
        self.handlers.add(handler)
        return self

    def __call__(self, data):
        for handler in self.handlers:
            logger.info("plugin: %s execute ..." % handler.__class__.__name__)
            try:
                handler.execute(data)
            except:
                logger.error("plugin: %s execute failure %s" % (handle.__class__.__name__, sys.exc_info()[0]))

    def __len__(self):
        return len(self.handlers)
