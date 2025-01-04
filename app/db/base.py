import sqlite3
import psycopg2
from abc import ABC, abstractmethod

class DatabaseInterface(ABC):
    """Abstract base class for database interactions."""

    @abstractmethod
    def connect(self):
        """Establish a database connection."""
        pass

    @abstractmethod
    def execute_query(self, query: str, params: tuple = None):
        """Execute a SELECT query and return results."""
        pass

    @abstractmethod
    def execute_update(self, query: str, params: tuple = None):
        """Execute an INSERT, UPDATE, or DELETE query."""
        pass

    @abstractmethod
    def close(self):
        """Close the database connection."""
        pass


class PostgresDatabase(DatabaseInterface):
    """PostgreSQL implementation of the database interface."""

    def __init__(self, host, database, user, password, port=5432):
        self.connection = None
        self.config = {
            "host": host,
            "database": database,
            "user": user,
            "password": password,
            "port": port,
        }

    def connect(self):
        """Establish a PostgreSQL connection."""
        self.connection = psycopg2.connect(**self.config)

    def execute_query(self, query: str, params: tuple = None):
        """Execute a SELECT query and return results."""
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    def execute_update(self, query: str, params: tuple = None):
        """Execute an INSERT, UPDATE, or DELETE query."""
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            self.connection.commit()

    def close(self):
        """Close the PostgreSQL connection."""
        if self.connection:
            self.connection.close()


class SQLiteDatabase(DatabaseInterface):
    """SQLite implementation of the database interface."""

    def __init__(self, db_path):
        self.connection = None
        self.db_path = db_path

    def connect(self):
        """Establish an SQLite connection."""
        self.connection = sqlite3.connect(self.db_path)

    def execute_query(self, query: str, params: tuple = None):
        """Execute a SELECT query and return results."""
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    def execute_update(self, query: str, params: tuple = None):
        """Execute an INSERT, UPDATE, or DELETE query."""
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            self.connection.commit()

    def close(self):
        """Close the SQLite connection."""
        if self.connection:
            self.connection.close()
