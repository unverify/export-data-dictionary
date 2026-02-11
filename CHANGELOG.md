# Changelog

## [0.2.0] - 2026-02-11

### Added

- MSSQL Server support (`export_mssql.py`, `mssql_connector.py`)
- Docker support with ODBC driver configuration
- Pre-commit hooks (trailing whitespace, end-of-file, YAML check, gitleaks, ruff)
- GitHub Actions security scanning (gitleaks, pip-audit, bandit)
- Dependabot for automated dependency updates
- Ruff linter/formatter configuration

### Changed

- Migrated to uv package manager with `pyproject.toml`
- Updated pylint CI to Python 3.11/3.12/3.13 and actions v4/v5
- Updated `.gitignore` with additional patterns

## [0.1.0] - Initial release

### Added

- MySQL schema export to XLSX data dictionary
- Auto-width columns in generated Excel files
- Sheet-per-prefix grouping for MySQL tables
