import os
import sys
import re
import pwd

from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...

import logging
from setuptools.command.install import install

perms = {
  "etc/OANDA": 0700,
  "etc/OANDA/config": 0700,
  "etc/OANDA/config/OANDAd.cfg": 0600,
  "etc/OANDA/config/plugins": 0700,
  "etc/OANDA/config/plugins/plainfile.cfg": 0600,
  "etc/OANDA/config/plugins/pubsub.cfg": 0600,
  "etc/OANDA/config/plugins/example/mysql.cfg": 0600,
  "etc/OANDA/plugins": 0700,
  "etc/OANDA/plugins/plainfile.py": 0600,
  "etc/OANDA/plugins/pubsub.py": 0600,
  "bin/OANDAd": 0711,
  "var/log/OANDA": 0700,
}


class CustomInstallCommand(install):

    def run(self):
        uid, gid = None, None
        mode = 0700
        try:
            pw_ent = pwd.getpwnam("oanda")
            uid = pw_ent.pw_uid
            gid = pw_ent.pw_gid
        except KeyError:
            sys.stderr.write("******************************************************\n")
            sys.stderr.write("*** Please add the OANDA-user first to your system ***\n")
            sys.stderr.write("*** missing: username: oanda, group: oanda         ***\n")
            sys.stderr.write("******************************************************\n")
            exit(0)

        install.run(self)
        # calling install.run(self) insures that everything that happened
        # previously still happens, so the installation does not break!

        # here we start with doing our overriding and private magic ...

        # determine prefix: depends on virtualenv of systeminstall
        PREF = "/" if not hasattr(sys, "real_prefix") else sys.prefix

        def alter_perms(F, filepath):
            if F not in perms:
                logging.info("No perms found for: " + F)
                return
            mode = perms[F]
            logging.info("Overriding setuptools mode of scripts ...")
            logging.info("Changing ownership of %s to uid:%s gid %s" %
                         (filepath, uid, gid))
            os.chown(filepath, uid, gid)
            logging.info("Changing permissions of %s to %s" %
                         (filepath, oct(mode)))
            os.chmod(filepath, mode)

        for filepath in self.get_outputs():
            F = filepath.replace(PREF, '').lstrip("/")
            if F in perms:
                # check the file
                alter_perms(F, filepath)
                # check the dir. of the file
                F = os.path.dirname(F)
                alter_perms(F, os.path.dirname(filepath))


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


requirements = map(str.strip, open("requirements.txt").readlines())

# python 2.7 hack to figure out if we run in a virtualenv
virtual_env = None if not hasattr(sys, "real_prefix") else sys.prefix


def prep_path(virtual_env, lot):
    # process list of tuples ONLY if we are in a virtual env
    if not virtual_env:
        return lot

    r = []
    # directory tuples ..
    for dt in lot:
        P1, P2 = dt[0], dt[1]
        r.append((virtual_env + "/" + P1.lstrip("/"), P2))

    return r


data_files = prep_path(virtual_env, [
        ('/etc/OANDA/config', ['etc/OANDA/config/OANDAd.cfg']),
        ('/etc/OANDA/config/plugins', ['etc/OANDA/config/plugins/pubsub.cfg', 'etc/OANDA/config/plugins/plainfile.cfg']),
        ('/etc/OANDA/config/plugins/example', ['etc/OANDA/config/plugins/example/mysql.cfg']),
        ('/etc/OANDA/plugins', ['etc/OANDA/plugins/pubsub.py', 'etc/OANDA/plugins/plainfile.py', 'etc/OANDA/plugins/README.md']),
        ('/etc/OANDA/plugins/example', ['etc/OANDA/plugins/example/mysql.py']),
        ('/var/log/OANDA', []),
       ])

version = get_version('oanda_trading_environment')

setup(
    cmdclass={'install': CustomInstallCommand},
    name="oanda-trading-environment",
    version=version,
    author="Feite Brekeveld",
    author_email="f.brekeveld@gmail.com",
    description=("OANDA REST-API based environment serving as a base for futher development of trading tools. Main part is the OANDAd daemon processing the streaming quotes"),
    license="MIT",
    keywords="Python OANDA oandapy REST API trading modules",
    url="https://github.com/hootnot/oanda-trading-environment",
    # packages=['oanda_trading_environment', 'tests'],
    packages=get_packages('oanda_trading_environment'),
    install_requires=requirements,
    # package_data = { }
    # include_package_data = True,
    # long_description=read('README'),
    scripts=["bin/OANDAd"],
    data_files=data_files,
    # oandapy is a dependency. Is is not on pypi and does not have a distutils compatible setup
    # therefore this fork is used
    dependency_links=[
       "git+https://github.com/hootnot/oandapy#egg=oandapy-0.1"
    ],
    # generate 'binaries' from the code
    entry_points={
      'console_scripts': [
         'testOANDAd = oanda_trading_environment.OANDAd:main_func',
      ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    test_suite="tests",
)
