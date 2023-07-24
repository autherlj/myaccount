import mysql.connector
from mysql.connector import pooling
import logging

# Create a custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create handlers
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

# Create formatters and add it to handlers
stream_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(stream_format)

# Add handlers to the logger
logger.addHandler(stream_handler)


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

        # Create query statement for usage records
        query_recharge_records = ("SELECT order_id, recharge_time, recharge_tokens, recharge_amount "
                                  "FROM recharge_records "
                                  "WHERE openid = %s "
                                  "ORDER BY recharge_time DESC")
        logger.info("Executing query: %s", query_recharge_records)
        logger.info("With parameters: %s", (openid,))
        # Execute the query
        cursor.execute(query_recharge_records, (openid,))

        # Fetch the query result
        recharge_records = []
        for (order_id, recharge_time, recharge_tokens, recharge_amount) in cursor:
            record = {
                'order_id': order_id,
                'recharge_time': recharge_time,
                'recharge_tokens': recharge_tokens,
                'recharge_amount': recharge_amount
            }
            recharge_records.append(record)

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

        return records, recharge_records, balance

    def insert_record_and_update_balance_and_status(self, trade_order_id, time, tokens, price, openid):
        # 从连接池获取连接
        cnx = self.cnxpool.get_connection()

        cursor = cnx.cursor()


        try:
            # 创建插入语句
            insert_query = ("INSERT INTO recharge_records "
                            "(order_id, recharge_time, recharge_tokens, recharge_amount, openid) "
                            "VALUES (%s, %s, %s, %s, %s)")

            # 执行插入
            cursor.execute(insert_query, (trade_order_id, time, tokens, price, openid))

            # 创建更新语句
            update_query = ("UPDATE user_balance "
                            "SET balance = balance + %s "
                            "WHERE openid = %s")

            # 执行更新
            cursor.execute(update_query, (tokens, openid))

            # 创建更新语句
            update_usage_status = ("UPDATE user_status "
                                   "SET usage_status = 1 "
                                   "WHERE openid = %s AND usage_status = 0")

            # 执行更新
            cursor.execute(update_usage_status, (openid,))
            # 提交事务
            cnx.commit()
        except Exception as e:
            # 如果在执行插入或更新操作时发生错误，回滚事务
            cnx.rollback()
            logger.error(f"Database operation failed: {str(e)}")
            raise e  # re-throw the exception to let the caller handle the error
        finally:
            # 关闭游标和连接
            cursor.close()
            cnx.close()
