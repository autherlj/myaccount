import mysql.connector
from mysql.connector import pooling
from datetime import datetime


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DatabaseManager(metaclass=Singleton):
    def __init__(self, host='127.0.0.1', database='myaccount', user='root', password='mysql@123', pool_size=5):
        dbconfig = {
            "host": host,
            "user": user,
            "passwd": password,
            "database": database,
        }
        self.cnxpool = mysql.connector.pooling.MySQLConnectionPool(pool_size=pool_size, **dbconfig)

    def get_usage_records(self, openid):
        # Get connection from the pool
        cnx = self.cnxpool.get_connection()

        cursor = cnx.cursor()

        # 创建查询语句
        query = ("SELECT usage_time, type, model, token_length "
                 "FROM usage_records "
                 "WHERE openid = %s"
                 "ORDER BY usage_time DESC")

        # 执行查询
        cursor.execute(query, (openid,))

        # 获取查询结果
        records = []
        for (usage_time, usage_type, model, token_length) in cursor:
            record = {
                'usage_time': usage_time,
                'type': usage_type,
                'model': model,
                'token_length': token_length
            }
            records.append(record)

        # 关闭游标和连接
        cursor.close()
        cnx.close()

        return records

    def get_user_balance(self, openid):
        # Get connection from the pool
        cnx = self.cnxpool.get_connection()

        cursor = cnx.cursor()

        # 创建查询语句
        query = ("SELECT balance "
                 "FROM user_balance "
                 "WHERE openid = %s")

        # 执行查询
        cursor.execute(query, (openid,))

        # 获取查询结果
        result = cursor.fetchone()

        # 关闭游标和连接
        cursor.close()
        cnx.close()

        # 检查查询结果是否为空
        if result is None:
            return None
        else:
            return result[0]  # 返回balance值
