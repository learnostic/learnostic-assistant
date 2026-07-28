from contextlib import contextmanager

import pymysql
import pymysql.cursors

from app.config import db_credentials, settings

MAX_EXECUTION_TIME_MS = 10_000


@contextmanager
def replica_connection(tenant_schema: str):
    conn = pymysql.connect(
        host=db_credentials.endpoint,
        port=settings.db_port,
        user=db_credentials.username,
        password=db_credentials.password,
        database=tenant_schema,
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5,
        autocommit=True,
    )
    try:
        with conn.cursor() as cur:
            cur.execute("SET SESSION TRANSACTION READ ONLY")
            cur.execute(f"SET SESSION MAX_EXECUTION_TIME = {MAX_EXECUTION_TIME_MS}")
        yield conn
    finally:
        conn.close()


def run_query(tenant_schema: str, validated_sql: str) -> list[dict]:
    with replica_connection(tenant_schema) as conn:
        with conn.cursor() as cur:
            cur.execute(validated_sql)
            return cur.fetchall()
