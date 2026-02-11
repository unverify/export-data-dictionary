from unittest.mock import MagicMock, patch

import pytest

from mssql_connector import MSSQLConnector


def _mock_pyodbc():
    """Create a standard mock for pyodbc.connect."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = ("testdb",)
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor


class TestMSSQLConnectorConnectToDb:
    @patch("mssql_connector.pyodbc")
    def test_connect_success(self, mock_pyodbc):
        mock_conn, _ = _mock_pyodbc()
        mock_pyodbc.connect.return_value = mock_conn

        connector = MSSQLConnector("testdb", "user", "pass", "localhost", 1433)

        mock_pyodbc.connect.assert_called_once()
        conn_str = mock_pyodbc.connect.call_args[0][0]
        assert "FreeTDS" in conn_str
        assert "localhost" in conn_str
        assert "1433" in conn_str
        assert "testdb" in conn_str
        assert connector.connection is mock_conn

    @patch("mssql_connector.pyodbc")
    def test_connect_default_port(self, mock_pyodbc):
        mock_conn, _ = _mock_pyodbc()
        mock_pyodbc.connect.return_value = mock_conn

        connector = MSSQLConnector("testdb", "user", "pass", "localhost")
        assert connector.db_port == 1433

    @patch("mssql_connector.pyodbc")
    def test_connect_prints_success_message(self, mock_pyodbc, capsys):
        mock_conn, _ = _mock_pyodbc()
        mock_pyodbc.connect.return_value = mock_conn

        MSSQLConnector("mydb", "user", "pass", "localhost")
        captured = capsys.readouterr()
        assert "Successfully connected to testdb" in captured.out

    @patch("mssql_connector.pyodbc")
    def test_connect_timeout_passed(self, mock_pyodbc):
        mock_conn, _ = _mock_pyodbc()
        mock_pyodbc.connect.return_value = mock_conn

        MSSQLConnector("testdb", "user", "pass", "localhost")
        call_kwargs = mock_pyodbc.connect.call_args[1]
        assert call_kwargs["timeout"] == 10

    @patch("mssql_connector.pyodbc")
    def test_connect_failure_raises(self, mock_pyodbc):
        mock_pyodbc.connect.side_effect = Exception("Connection refused")

        with pytest.raises(Exception, match="Connection refused"):
            MSSQLConnector("testdb", "user", "pass", "badhost")


class TestMSSQLConnectorGetSchema:
    @patch("mssql_connector.pyodbc")
    def test_get_schema_groups_by_table(self, mock_pyodbc, mssql_raw_rows):
        mock_conn, mock_cursor = _mock_pyodbc()
        mock_cursor.fetchall.return_value = mssql_raw_rows
        mock_pyodbc.connect.return_value = mock_conn

        connector = MSSQLConnector("testdb", "user", "pass", "localhost")
        schema = connector.get_schema()

        assert "users" in schema
        assert len(schema["users"]) == 2

    @patch("mssql_connector.pyodbc")
    def test_get_schema_none_column_comment_becomes_empty_string(self, mock_pyodbc, mssql_raw_rows):
        mock_conn, mock_cursor = _mock_pyodbc()
        mock_cursor.fetchall.return_value = mssql_raw_rows
        mock_pyodbc.connect.return_value = mock_conn

        connector = MSSQLConnector("testdb", "user", "pass", "localhost")
        schema = connector.get_schema()

        # Second row has column_comment=None
        assert schema["users"][1]["column_comment"] == ""
        # First row has column_comment="Primary key"
        assert schema["users"][0]["column_comment"] == "Primary key"

    @patch("mssql_connector.pyodbc")
    def test_get_schema_empty_result(self, mock_pyodbc):
        mock_conn, mock_cursor = _mock_pyodbc()
        mock_cursor.fetchall.return_value = []
        mock_pyodbc.connect.return_value = mock_conn

        connector = MSSQLConnector("testdb", "user", "pass", "localhost")
        schema = connector.get_schema()

        assert schema == {}

    @patch("mssql_connector.pyodbc")
    def test_get_schema_closes_connection(self, mock_pyodbc, mssql_raw_rows):
        mock_conn, mock_cursor = _mock_pyodbc()
        mock_cursor.fetchall.return_value = mssql_raw_rows
        mock_pyodbc.connect.return_value = mock_conn

        connector = MSSQLConnector("testdb", "user", "pass", "localhost")
        connector.get_schema()

        mock_conn.close.assert_called_once()

    @patch("mssql_connector.pyodbc")
    def test_query_schema_uses_default_query(self, mock_pyodbc):
        mock_conn, mock_cursor = _mock_pyodbc()
        mock_cursor.fetchall.return_value = []
        mock_pyodbc.connect.return_value = mock_conn

        connector = MSSQLConnector("testdb", "user", "pass", "localhost")
        connector.query_schema()

        calls = mock_cursor.execute.call_args_list
        assert len(calls) == 2
        query = calls[1][0][0]
        assert "INFORMATION_SCHEMA.COLUMNS" in query
        params = calls[1][0][1]
        assert params == ("testdb",)

    @patch("mssql_connector.pyodbc")
    def test_query_schema_uses_custom_query(self, mock_pyodbc):
        mock_conn, mock_cursor = _mock_pyodbc()
        mock_cursor.fetchall.return_value = []
        mock_pyodbc.connect.return_value = mock_conn

        connector = MSSQLConnector("testdb", "user", "pass", "localhost")
        custom_query = "SELECT * FROM custom_table"
        connector.query_schema(custom_query)

        calls = mock_cursor.execute.call_args_list
        assert calls[1][0][0] == custom_query
