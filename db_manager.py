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
                "WHERE openid = %s")

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
            # 将查询结果封装成字典
            record = {
                'balance': result[0]
            }
            return record
    def insert_user_status(self, openid):
        # Get connection from the pool
        cnx = self.cnxpool.get_connection()

        cursor = cnx.cursor()

        # Create insert statement
        add_openid = "INSERT IGNORE  INTO user_status (openid, usage_status) VALUES (%s, 1)"

        # Insert new openid
        data_openid = (openid,)
        cursor.execute(add_openid, data_openid)

        # Commit the changes
        cnx.commit()

        # Close cursor and connection
        cursor.close()
        cnx.close()

    def check_usage_status(self, session_id):
        # Get connection from the pool
        cnx = self.cnxpool.get_connection()

        cursor = cnx.cursor()

        # SQL query to retrieve the value from the user_status table
        sql = "SELECT usage_status FROM user_status WHERE openid = %s"
        cursor.execute(sql, (session_id,))

        # Fetch the result
        result = cursor.fetchone()

        # Close cursor and connection
        cursor.close()
        cnx.close()

        # If result is None, that means the session_id does not exist in the database
        if result is None:
            raise ValueError("Invalid session_id")

        # Convert the result to bool and return
        return bool(result[0])
