import pyodbc


class MSSQLConnector:
    def __init__(self, db_name, db_user, db_password, db_host, db_port=1433):
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name
        self.connection, self.cursor = self.connect_to_db()

    def connect_to_db(self):
        conn_str = (
            f"DRIVER={{FreeTDS}};"
            f"SERVER={self.db_host};"
            f"PORT={self.db_port};"
            f"DATABASE={self.db_name};"
            f"UID={self.db_user};"
            f"PWD={self.db_password};"
        )
        connection = pyodbc.connect(conn_str, timeout=10)
        cursor = connection.cursor()
        cursor.execute("SELECT DB_NAME()")
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
                c.TABLE_NAME,
                c.ORDINAL_POSITION,
                c.COLUMN_NAME,
                c.DATA_TYPE,
                c.CHARACTER_MAXIMUM_LENGTH,
                c.IS_NULLABLE,
                COALESCE(tc.CONSTRAINT_TYPE, '') AS EXTRA,
                COALESCE(CAST(ep.value AS NVARCHAR(MAX)), '') AS COLUMN_COMMENT,
                c.COLUMN_DEFAULT
            FROM
                INFORMATION_SCHEMA.COLUMNS c
            LEFT JOIN (
                SELECT
                    kcu.TABLE_NAME,
                    kcu.COLUMN_NAME,
                    tc.CONSTRAINT_TYPE
                FROM
                    INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
                INNER JOIN
                    INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
                    ON kcu.CONSTRAINT_NAME = tc.CONSTRAINT_NAME
                    AND kcu.TABLE_NAME = tc.TABLE_NAME
            ) tc ON c.TABLE_NAME = tc.TABLE_NAME AND c.COLUMN_NAME = tc.COLUMN_NAME
            LEFT JOIN
                sys.columns sc
                ON sc.name = c.COLUMN_NAME
                AND sc.object_id = OBJECT_ID(c.TABLE_SCHEMA + '.' + c.TABLE_NAME)
            LEFT JOIN
                sys.extended_properties ep
                ON ep.major_id = sc.object_id
                AND ep.minor_id = sc.column_id
                AND ep.name = 'MS_Description'
            WHERE
                c.TABLE_CATALOG = ?
                AND c.TABLE_SCHEMA = 'dbo'
            ORDER BY
                c.TABLE_NAME,
                c.ORDINAL_POSITION ASC
            """
        cursor.execute(query_schema, (self.db_name,))
        results = cursor.fetchall()
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
                "column_comment": column_comment if column_comment else "",
                "column_default": column_default if column_default else "",
            }
            if table in table_name:
                table_name[table].append(table_schema)
            else:
                table_name[table] = [table_schema]
        return table_name
