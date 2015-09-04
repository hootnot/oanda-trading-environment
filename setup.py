import os
import sys

from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]

requirements = map(str.strip, open("requirements.txt").readlines())

# python 2.7 hack to figure out if we run in a virtualenv
# virtual_env = hasattr(sys, 'real_prefix')
virtual_env = os.getenv('VIRTUAL_ENV')


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
        ('/etc/OANDA/config/plugins', ['etc/OANDA/config/plugins/pubsub.cfg']),
        ('/etc/OANDA/config/plugins/example', ['etc/OANDA/config/plugins/example/mysql.cfg']),
        ('/etc/OANDA/plugins', ['etc/OANDA/plugins/pubsub.py', 'etc/OANDA/plugins/README.md']),
        ('/etc/OANDA/plugins/example', ['etc/OANDA/plugins/example/mysql.py']),
        ('/var/log/OANDA', []),
       ])

setup(
    name="oanda-trading-environment",
    version="0.0.1",
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
       "git+https://github.com/b1r3k/oandapy#egg=oandapy",
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
        "Intended Audience :: Traders",
        "Operating System :: Linux",
        "Programming Language :: Python",
        "Topic :: Trading :: Auto Trading :: Quoteserver :: OANDA",
    ],
    test_suite="tests",
)
