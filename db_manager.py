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

    def get_user_records_balance(self, openid):
        # Get connection from the pool
        cnx = self.cnxpool.get_connection()

        cursor = cnx.cursor()

        # Create query statement for usage records
        query_records = ("SELECT usage_time, type, model, token_length "
                     "FROM usage_records "
                     "WHERE openid = %s "
                     "ORDER BY usage_time DESC")

        # Execute the query
        cursor.execute(query_records, (openid,))

        # Fetch the query result
        records = []
        for (usage_time, usage_type, model, token_length) in cursor:
            record = {
                    'usage_time': usage_time,
                    'type': usage_type,
                    'model': model,
                    'token_length': token_length
            }
            records.append(record)

        # Create query statement for user balance
        query_balance = ("SELECT balance "
                        "FROM user_balance "
                        "WHERE openid = %s")

        # Execute the query
        cursor.execute(query_balance, (openid,))

        # Fetch the query result
        result = cursor.fetchone()

        # Close the cursor and connection
        cursor.close()
        cnx.close()

        # Check if the query result is empty
        balance = None if result is None else result[0]  # Return balance value

        return records, balance

