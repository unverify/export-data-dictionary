import MySQLdb


class MySQLConnector:
    def __init__(self, db_name, db_user, db_password, db_host):
        self.db_host = db_host
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name
        self.connection, self.cursor = self.connect_to_db()

    def connect_to_db(self):
        connection = MySQLdb.connect(host=self.db_host, user=self.db_user, passwd=self.db_password, db=self.db_name)
        cursor = connection.cursor()
        cursor.execute("select database();")
        db = cursor.fetchone()
        is_success = "Successfully" if bool(db) else "Failed"
        print(f"{is_success} connected to {db[0]}")
        return connection, cursor

    def query_schema(self, query_schema: str = None):
        connection = self.connection
        cursor = self.cursor
        if not query_schema:
            query_schema = """
            SELECT
                table_name,
                ordinal_position,
                column_name,
                column_type,
                character_maximum_length,
                is_nullable,
                extra,
                column_comment,
                column_default
            FROM
                information_schema.COLUMNS
            WHERE
                table_schema = %s
            ORDER BY
                table_name,
                ordinal_position ASC;
            """
        cursor.execute(query_schema, (self.db_name,))

        # Fetch a single row using fetchone() method.
        results = cursor.fetchall()

        # disconnect from server
        connection.close()
        return results

    def get_schema(self):
        result = self.query_schema()
        table_name = {}
        for row in result:
            (
                table,
                ordinal,
                column_name,
                column_type,
                max_length,
                is_nullable,
                extra,
                column_comment,
                column_default,
            ) = row
            table_schema = {
                "ordinal": ordinal,
                "column_name": column_name,
                "column_type": column_type,
                "max_length": max_length if max_length else "",
                "is_nullable": is_nullable,
                "extra": extra,
                "column_comment": column_comment,
                "column_default": column_default if column_default else "",
            }
            if table in table_name:
                table_name[table].append(table_schema)
            else:
                table_name[table] = [table_schema]
        return table_name
