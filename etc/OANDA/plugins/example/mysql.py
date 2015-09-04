import sys
import pymysql

from oanda_trading_environment.daemon.plugin import Plugin


class InsertRecord(Plugin):
    def __init__(self, config=None):
        # fetch config, establish handle
        super(InsertRecord, self).__init__(config=config)
        self.sql = "INSERT INTO itick values(%s) "

        mysqlParam = {}
        mysqlParam.update({"host": self.config['host']})
        try:
            mysqlParam.update({"port": self.config['port']})
        except:
            pass
        mysqlParam.update({"user": self.config['user']})
        mysqlParam.update({"password": self.config['password']})
        mysqlParam.update({"db": self.config['db']})
        self.connection = None
        self.connection = pymysql.connect(
                         cursorclass=pymysql.cursors.DictCursor,
                         **mysqlParam)

    def __del__(self):
        if self.connection:
            self.connection.close()

    def execute(self, data):
        with self.connection.cursor() as cursor:
            cursor.execute(self.sql, data)

        self.connection.commit()
