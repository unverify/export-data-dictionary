# Export Database Schema to XLSX Data Dictionary

Export database table and column metadata to a formatted Excel spreadsheet.

## Features

- MySQL and MSSQL Server support
- Auto-formatted Excel output with bold headers, borders, and auto-width columns
- Sheet-per-prefix grouping (MySQL) or single-sheet output (MSSQL)
- Docker support with ODBC driver configuration

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager

## Usage

1. Install dependencies:

   ```bash
   uv sync
   ```

2. Copy `configs.py.default` to `configs.py` and fill in your database credentials:

   ```bash
   cp configs.py.default configs.py
   ```

3. Run the export:

   ```bash
   # MySQL
   uv run python export.py

   # MSSQL
   uv run python export_mssql.py
   ```

The output file `data_dictionary.xlsx` will be generated in the project directory.

### Docker (MSSQL)

```bash
docker build -t export-data-dictionary .
docker run -v $(pwd):/app export-data-dictionary
```

## Development

Development and testing use Docker — no database drivers or system libraries needed on your machine.

### Running tests

```bash
docker build --target test -t export-data-dictionary-test .
docker run --rm export-data-dictionary-test
```

Tests use pytest with mocked database connections (no real database required). The test suite covers:
- `generate.py` — Excel generation, column width tracking, sheet grouping
- `mysql_connector.py` — MySQL connection and schema parsing
- `mssql_connector.py` — MSSQL connection and schema parsing

### Running linters

```bash
docker run --rm export-data-dictionary-test uv run pylint $(find . -name "*.py" -not -path "./.venv/*")
```

### Pre-commit hooks

```bash
pre-commit install
pre-commit run --all-files
```

### Project structure

| File | Description |
|------|-------------|
| `export.py` | MySQL export entry point |
| `export_mssql.py` | MSSQL export entry point |
| `generate.py` | Excel workbook generation and formatting |
| `mysql_connector.py` | MySQL database connector and schema extraction |
| `mssql_connector.py` | MSSQL database connector and schema extraction |
| `configs.py.default` | Configuration template (copy to `configs.py`) |
| `tests/` | pytest test suite |

## CI

- **Lint & Test** — pylint + pytest on every push (Python 3.11, 3.12, 3.13)
- **Security scanning** — gitleaks (secrets), pip-audit (dependencies), bandit (SAST)
- **Dependabot** — weekly PRs for dependency and GitHub Actions updates
