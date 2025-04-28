import pymysql
import pymysql.cursors
from pymysql import connect
import os
from dotenv import load_dotenv

import logging

import pymysql.cursors

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

load_dotenv()

db_user=os.getenv("DB_USER")
logging.info(f"Database user is {db_user}")
db_host=os.getenv("DB_HOST")
logging.info(f"Database host is {db_host}")
db_password=os.getenv("DB_PASSWORD")
logging.info(f"Database password is {db_password}")
db_port=int(os.getenv("DB_PORT"))
logging.info(f"Database port is {db_port}")
tenant_id = os.getenv("TENANT_ID")
logging.info(f"Tenant id is {tenant_id}")

def get_connection(database):
    try:
        conn = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            port=db_port,
            database=f"{tenant_id}_{database}"
        )
        logger.info(f"Successfully connected to {db_host}:{db_port} - Database: {tenant_id}_{database}")
        return conn
    except pymysql.MySQLError as e:
        logger.error(f"Something went wrong with the connection: {e}")
        return None
        
def execute_(database, query, params=None):
    conn = get_connection(database)
    if conn:
        try:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute(query, params)
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            logging.info(f"The result is {result}")
            return result
        except Exception as e:
            logging.error(f"Error occured with Exception {e}")
            return []
def update_query(database, query, params=None):
    conn = get_connection(database)
    if conn:
        try:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            result = cursor.execute(query, params)
            conn.commit()
            cursor.close()
            conn.close()
            return result
        except Exception as e:
            logging.error(f"Error occured with exception {e}")
            return []
    
def insert_query(database, query, params=None):
    conn = get_connection(database)
    if conn:
        try:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute(query, params)
            conn.commit()
            affected = cursor.rowcount
            cursor.close()
            conn.close()
            logging.info(f"The affected row count is {affected}")
            return affected
        except pymysql.MySQLError as e:
            logging.exception(f"Error occured with Exception {e}")
            return 0