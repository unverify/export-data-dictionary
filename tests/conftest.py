import pytest


@pytest.fixture
def single_table_schema():
    """Minimal schema data: one table with two columns."""
    return {
        "users": [
            {
                "ordinal": 1,
                "column_name": "id",
                "column_type": "int",
                "max_length": "",
                "is_nullable": "NO",
                "extra": "PRI",
                "column_comment": "Primary key",
                "column_default": "",
            },
            {
                "ordinal": 2,
                "column_name": "email",
                "column_type": "varchar",
                "max_length": "255",
                "is_nullable": "YES",
                "extra": "",
                "column_comment": "User email",
                "column_default": "",
            },
        ]
    }


@pytest.fixture
def multi_prefix_schema():
    """Schema data with multiple table-name prefixes for generate_xlsx grouping."""
    col = {
        "ordinal": 1,
        "column_name": "id",
        "column_type": "int",
        "max_length": "",
        "is_nullable": "NO",
        "extra": "PRI",
        "column_comment": "",
        "column_default": "",
    }
    return {
        "app_users": [col],
        "app_roles": [col],
        "blog_posts": [col],
        "blog_comments": [col],
    }


@pytest.fixture
def mysql_raw_rows():
    """Simulated return value from MySQLConnector.query_schema().
    Each row is a 9-tuple matching the SELECT column order."""
    return [
        ("users", 1, "id", "int", None, "NO", "auto_increment", "Primary key", None),
        ("users", 2, "email", "varchar(255)", 255, "YES", "", "User email", None),
        ("orders", 1, "id", "int", None, "NO", "auto_increment", "", None),
    ]


@pytest.fixture
def mssql_raw_rows():
    """Simulated return value from MSSQLConnector.query_schema().
    Same 9-tuple structure, but column_comment may be None."""
    return [
        ("users", 1, "id", "int", None, "NO", "PRIMARY KEY", "Primary key", None),
        ("users", 2, "name", "nvarchar", 100, "YES", "", None, None),
    ]
