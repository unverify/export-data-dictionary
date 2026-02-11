from configs import mssql_config as config
from generate import ExportDataDictionary
from mssql_connector import MSSQLConnector

DB_HOST = config["db_host"]
DB_PORT = config["db_port"]
DB_USER = config["db_user"]
DB_NAME = config["db_name"]
DB_PASSWORD = config["db_password"]

db = MSSQLConnector(db_host=DB_HOST, db_port=DB_PORT, db_user=DB_USER, db_password=DB_PASSWORD, db_name=DB_NAME)
schema = db.get_schema()
ExportDataDictionary("data_dictionary.xlsx").generate_xlsx_simple(schema)
