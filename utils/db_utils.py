import os
from pathlib import Path
from loguru import logger
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from config.config import config

BASE_DIR = Path(__file__).resolve().parent.parent


class DBUtils:

    def __init__(self, db_url: str = None):
        if db_url:
            self.db_url = db_url
        elif config.DB_URL:
            self.db_url = config.DB_URL
        else:
            db_path     = BASE_DIR / "data" / "test_database.db"
            self.db_url = f"sqlite:///{db_path}"

        self.engine  = create_engine(self.db_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        logger.info(f"DBUtils connected: {self.db_url}")

    def setup_test_db(self):
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id      INTEGER PRIMARY KEY AUTOINCREMENT,
                    name    TEXT    NOT NULL,
                    email   TEXT    UNIQUE NOT NULL,
                    role    TEXT    DEFAULT 'customer',
                    active  INTEGER DEFAULT 1,
                    created TEXT    DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS products (
                    id       INTEGER PRIMARY KEY AUTOINCREMENT,
                    name     TEXT NOT NULL,
                    price    REAL NOT NULL,
                    stock    INTEGER DEFAULT 0,
                    category TEXT DEFAULT 'general'
                )
            """))
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS orders (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id    INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity   INTEGER DEFAULT 1,
                    status     TEXT DEFAULT 'pending',
                    created    TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
        logger.success("Test DB tables created!")

    def insert(self, table: str, data: dict) -> int:
        cols   = ", ".join(data.keys())
        vals   = ", ".join(f":{k}" for k in data.keys())
        sql    = f"INSERT INTO {table} ({cols}) VALUES ({vals})"
        with self.engine.connect() as conn:
            result = conn.execute(text(sql), data)
            conn.commit()
            return result.lastrowid

    def fetch_one(self, sql: str, params: dict = None) -> dict | None:
        with self.engine.connect() as conn:
            result = conn.execute(text(sql), params or {})
            row    = result.mappings().first()
            return dict(row) if row else None

    def fetch_all(self, sql: str, params: dict = None) -> list:
        with self.engine.connect() as conn:
            result = conn.execute(text(sql), params or {})
            return [dict(r) for r in result.mappings().all()]

    def execute(self, sql: str, params: dict = None) -> int:
        with self.engine.connect() as conn:
            result = conn.execute(text(sql), params or {})
            conn.commit()
            return result.rowcount

    def delete_where(self, table: str, conditions: dict) -> int:
        where = " AND ".join(f"{k} = :{k}" for k in conditions)
        sql   = f"DELETE FROM {table} WHERE {where}"
        return self.execute(sql, conditions)

    def count_rows(self, table: str, conditions: dict = None) -> int:
        where  = ""
        params = {}
        if conditions:
            where  = "WHERE " + " AND ".join(
                f"{k} = :{k}" for k in conditions
            )
            params = conditions
        row = self.fetch_one(
            f"SELECT COUNT(*) as cnt FROM {table} {where}", params
        )
        return int(row["cnt"]) if row else 0

    def assert_record_exists(self, table: str,
                              conditions: dict, msg: str = None):
        count = self.count_rows(table, conditions)
        assert count > 0, \
            msg or f"No record in '{table}' with {conditions}"
        logger.success(f"PASS: record exists in {table}")

    def assert_record_not_exists(self, table: str,
                                  conditions: dict, msg: str = None):
        count = self.count_rows(table, conditions)
        assert count == 0, \
            msg or f"Record found in '{table}' — expected none"
        logger.success(f"PASS: no record in {table}")

    def assert_column_value(self, table: str, column: str,
                             conditions: dict, expected):
        row = self.fetch_one(
            f"SELECT {column} FROM {table} WHERE "
            + " AND ".join(f"{k} = :{k}" for k in conditions),
            conditions
        )
        assert row is not None, f"No row in {table} with {conditions}"
        assert row[column] == expected, \
            f"Expected {column}='{expected}', got '{row[column]}'"
        logger.success(f"PASS: {table}.{column} = '{expected}'")

    def assert_table_exists(self, table: str):
        inspector = inspect(self.engine)
        tables    = inspector.get_table_names()
        assert table in tables, f"Table '{table}' not found"
        logger.success(f"PASS: table '{table}' exists")

    def assert_row_count(self, table: str,
                          expected: int, conditions: dict = None):
        actual = self.count_rows(table, conditions)
        assert actual == expected, \
            f"Row count: expected {expected}, got {actual}"
        logger.success(f"PASS: {table} has {expected} rows")

    def truncate(self, table: str):
        self.execute(f"DELETE FROM {table}")
        logger.warning(f"Table '{table}' cleared")

    def cleanup(self):
        if self.session:
            self.session.close()
        logger.info("DB connection closed")