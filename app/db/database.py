# import sqlite3
# import psycopg2
# from abc import ABC, abstractmethod

from sqlalchemy import create_engine,text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateSchema

class  Database:
    """Database connection and session management."""

    def __init__(self,connection_string,autocommit=False):
        if autocommit:
            self.engine = create_engine(connection_string,isolation_level="AUTOCOMMIT")
        else:
            self.engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.engine)
        self._session = None  # Internal session instance

    def get_session(self):
        """Create and return a new session."""
        if self._session is None:
            self._session = self.Session()
        return self._session

    def execute_query(self, query, params=None):
        """Execute a query and return the result."""
        if isinstance(query,str):
            query = text(query)

        with self.engine.connect() as connection:
            result = connection.execute(query, params or {})
            
            # Extract column names
            columns = result.keys()

            # Fetch all rows
            rows = result.fetchall()

            return columns, rows

    def execute_update(self, query, params=None):
        """Execute an update or insert query."""
        if isinstance(query,str):
            query = text(query)

        with self.engine.connect() as connection:
            connection.execute(query, params or {})

    def close_session(self):
        """Close the current session if it exists."""
        if self._session:
            self._session.close()
            self._session = None

    def create_schema(self,schema):
        """Create the schema if it doesn't exist"""
        with self.engine.connect() as connection:
            connection.execute(CreateSchema(schema,if_not_exists=True))
            connection.commit()

if __name__=="__main__":
    import os 
    from app.config.settings import settings

    with open(os.path.join("app","db","queries","extract","ingest_receipt.sql"),"r") as query:
        receipt_query = query.read()
    db = Database(connection_string=settings.finance_db_url)
    print(db.execute_query(receipt_query))