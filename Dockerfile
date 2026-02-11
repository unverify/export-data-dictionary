FROM python:3.13-slim AS base

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential pkg-config default-libmysqlclient-dev unixodbc unixodbc-dev tdsodbc freetds-common \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && printf '[global]\ntds version = 7.4\nclient charset = UTF-8\n' > /etc/freetds/freetds.conf \
    && TDSODBC=$(find /usr -name 'libtdsodbc.so' | head -1) \
    && printf "[FreeTDS]\nDescription = FreeTDS unixODBC Driver\nDriver = ${TDSODBC}\n" > /etc/odbcinst.ini

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY . .
RUN uv sync --frozen

FROM base AS test
CMD ["uv", "run", "pytest"]

FROM base AS prod
CMD ["uv", "run", "python", "export_mssql.py"]
