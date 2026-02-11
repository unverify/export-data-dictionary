from unittest.mock import MagicMock, patch

import pytest

from mysql_connector import MySQLConnector


def _mock_mysqldb():
    """Create a standard mock for MySQLdb.connect."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = ("testdb",)
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor


class TestMySQLConnectorConnectToDb:
    @patch("mysql_connector.MySQLdb")
    def test_connect_success(self, mock_mysqldb):
        mock_conn, mock_cursor = _mock_mysqldb()
        mock_mysqldb.connect.return_value = mock_conn

        connector = MySQLConnector("testdb", "user", "pass", "localhost")

        mock_mysqldb.connect.assert_called_once_with(host="localhost", user="user", passwd="pass", db="testdb")
        mock_cursor.execute.assert_called_once_with("select database();")
        assert connector.connection is mock_conn
        assert connector.cursor is mock_cursor

    @patch("mysql_connector.MySQLdb")
    def test_connect_prints_success_message(self, mock_mysqldb, capsys):
        mock_conn, _ = _mock_mysqldb()
        mock_mysqldb.connect.return_value = mock_conn

        MySQLConnector("mydb", "user", "pass", "localhost")
        captured = capsys.readouterr()
        assert "Successfully connected to testdb" in captured.out

    @patch("mysql_connector.MySQLdb")
    def test_connect_failure_raises(self, mock_mysqldb):
        mock_mysqldb.connect.side_effect = Exception("Connection refused")

        with pytest.raises(Exception, match="Connection refused"):
            MySQLConnector("testdb", "user", "pass", "badhost")


class TestMySQLConnectorGetSchema:
    @patch("mysql_connector.MySQLdb")
    def test_get_schema_groups_by_table(self, mock_mysqldb, mysql_raw_rows):
        mock_conn, mock_cursor = _mock_mysqldb()
        mock_cursor.fetchall.return_value = mysql_raw_rows
        mock_mysqldb.connect.return_value = mock_conn

        connector = MySQLConnector("testdb", "user", "pass", "localhost")
        schema = connector.get_schema()

        assert "users" in schema
        assert "orders" in schema
        assert len(schema["users"]) == 2
        assert len(schema["orders"]) == 1

    @patch("mysql_connector.MySQLdb")
    def test_get_schema_column_dict_keys(self, mock_mysqldb, mysql_raw_rows):
        mock_conn, mock_cursor = _mock_mysqldb()
        mock_cursor.fetchall.return_value = mysql_raw_rows
        mock_mysqldb.connect.return_value = mock_conn

        connector = MySQLConnector("testdb", "user", "pass", "localhost")
        schema = connector.get_schema()

        expected_keys = {
            "ordinal",
            "column_name",
            "column_type",
            "max_length",
            "is_nullable",
            "extra",
            "column_comment",
            "column_default",
        }
        assert set(schema["users"][0].keys()) == expected_keys

    @patch("mysql_connector.MySQLdb")
    def test_get_schema_none_max_length_becomes_empty_string(self, mock_mysqldb, mysql_raw_rows):
        mock_conn, mock_cursor = _mock_mysqldb()
        mock_cursor.fetchall.return_value = mysql_raw_rows
        mock_mysqldb.connect.return_value = mock_conn

        connector = MySQLConnector("testdb", "user", "pass", "localhost")
        schema = connector.get_schema()

        assert schema["users"][0]["max_length"] == ""

    @patch("mysql_connector.MySQLdb")
    def test_get_schema_present_max_length_preserved(self, mock_mysqldb, mysql_raw_rows):
        mock_conn, mock_cursor = _mock_mysqldb()
        mock_cursor.fetchall.return_value = mysql_raw_rows
        mock_mysqldb.connect.return_value = mock_conn

        connector = MySQLConnector("testdb", "user", "pass", "localhost")
        schema = connector.get_schema()

        assert schema["users"][1]["max_length"] == 255

    @patch("mysql_connector.MySQLdb")
    def test_get_schema_none_column_default_becomes_empty_string(self, mock_mysqldb, mysql_raw_rows):
        mock_conn, mock_cursor = _mock_mysqldb()
        mock_cursor.fetchall.return_value = mysql_raw_rows
        mock_mysqldb.connect.return_value = mock_conn

        connector = MySQLConnector("testdb", "user", "pass", "localhost")
        schema = connector.get_schema()

        assert schema["users"][0]["column_default"] == ""

    @patch("mysql_connector.MySQLdb")
    def test_get_schema_closes_connection(self, mock_mysqldb, mysql_raw_rows):
        mock_conn, mock_cursor = _mock_mysqldb()
        mock_cursor.fetchall.return_value = mysql_raw_rows
        mock_mysqldb.connect.return_value = mock_conn

        connector = MySQLConnector("testdb", "user", "pass", "localhost")
        connector.get_schema()

        mock_conn.close.assert_called_once()

    @patch("mysql_connector.MySQLdb")
    def test_get_schema_empty_result(self, mock_mysqldb):
        mock_conn, mock_cursor = _mock_mysqldb()
        mock_cursor.fetchall.return_value = []
        mock_mysqldb.connect.return_value = mock_conn

        connector = MySQLConnector("testdb", "user", "pass", "localhost")
        schema = connector.get_schema()

        assert schema == {}

    @patch("mysql_connector.MySQLdb")
    def test_query_schema_uses_default_query(self, mock_mysqldb):
        mock_conn, mock_cursor = _mock_mysqldb()
        mock_cursor.fetchall.return_value = []
        mock_mysqldb.connect.return_value = mock_conn

        connector = MySQLConnector("testdb", "user", "pass", "localhost")
        connector.query_schema()

        # The second call to execute (first is "select database()" in connect_to_db)
        calls = mock_cursor.execute.call_args_list
        assert len(calls) == 2
        query = calls[1][0][0]
        assert "information_schema.COLUMNS" in query
        params = calls[1][0][1]
        assert params == ("testdb",)

    @patch("mysql_connector.MySQLdb")
    def test_query_schema_uses_custom_query(self, mock_mysqldb):
        mock_conn, mock_cursor = _mock_mysqldb()
        mock_cursor.fetchall.return_value = []
        mock_mysqldb.connect.return_value = mock_conn

        connector = MySQLConnector("testdb", "user", "pass", "localhost")
        custom_query = "SELECT * FROM custom_table"
        connector.query_schema(custom_query)

        calls = mock_cursor.execute.call_args_list
        assert calls[1][0][0] == custom_query
