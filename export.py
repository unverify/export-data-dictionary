from mysql_connector import MySQLConnector
from generate import ExportDataDictionary
from configs import mysql_config as config

DB_HOST = config['db_host']
DB_USER = config['db_user']
DB_NAME = config['db_name']
DB_PASSWORD = config['db_password']

db = MySQLConnector(db_host=DB_HOST, db_user=DB_USER, db_password=DB_PASSWORD, db_name=DB_NAME)
schema = db.get_schema()
ExportDataDictionary('data_dictionary.xlsx').generate_xlsx(schema)