from pymysql import *


class mysql_python(object):
    def __init__(self, host, port, db, user, passwd, charset="utf8"):
        self.host = host
        self.port = port
        self.db = db
        self.user = user
        self.passwd = passwd
        self.charset = charset

    def open(self):
        '''连接数据库，创建游标对象'''
        self.con = connect(host=self.host, port=self.port, db=self.db, user=self.user, passwd=self.passwd,
                           charset=self.charset)
        self.cursor = self.con.cursor()

    def close(self):
        '''关闭数据库，关闭游标对象'''
        self.cursor.close()
        self.con.close()

    def implement(self, sql):
        '''使用游标对象的方法和SQL语句操作数据库'''
        self.open()
        self.cursor.execute(sql)
        # 提交到数据库
        self.con.commit()
        self.close()

    def all(self, sql):
        try:
            self.open()
            self.cursor.execute(sql)
            data = self.cursor.fetchall()
            self.close()
            return data
        except Exception as e:
            print(e)
