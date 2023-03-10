import MySQLdb


class MySQLConnector:

    def __init__(self,  db_name, db_user, db_password, db_host, connection=None, cursor=None,):
        self.DB_HOST = db_host
        self.DB_USER = db_user
        self.DB_PASSWORD = db_password
        self.DB_NAME = db_name
        self.connection, self.cursor = self.connect_to_db()

    def connect_to_db(self):
        connection = MySQLdb.connect(
            host=self.DB_HOST,
            user=self.DB_USER,
            passwd=self.DB_PASSWORD,
            db=self.DB_NAME)
        cursor = connection.cursor()
        cursor.execute("select database();")
        db = cursor.fetchone()
        is_success = 'Successfully' if bool(db) else 'Failed'
        print(f'{is_success} connected to {db[0]}')
        return connection, cursor

    def query_schema(self, query_schema: str = None):
        connection = self.connection
        cursor = self.cursor
        if not query_schema:
            query_schema = f'''
            SELECT
                table_name,
                column_name,
                column_type,
                is_nullable,
                extra,
                column_comment
            FROM
                information_schema.COLUMNS
            WHERE
                table_schema = '{self.DB_NAME}'
            ORDER BY
                table_name,
                ordinal_position ASC;
            '''

        # execute SQL query using execute() method.
        cursor.execute(query_schema)

        # Fetch a single row using fetchone() method.
        results = cursor.fetchall()

        # disconnect from server
        connection.close()
        return results

    def get_schema(self):
        result = self.query_schema()
        table_name = {}
        for row in result:
            table, column_name, column_type, is_nullable, extra, column_comment = row
            table_schema = {
                'column_name': column_name,
                'column_type': column_type,
                'is_nullable': is_nullable,
                'extra': extra,
                'column_comment': column_comment,
            }
            if table in table_name:
                table_name[table].append(table_schema)
            else:
                table_name[table] = [table_schema]
        return table_name
