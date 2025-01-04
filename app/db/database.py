from db.base import PostgresDatabase, SQLiteDatabase

class DatabaseFactory:
    """Factory to create database instances."""

    @staticmethod
    def get_database(db_type, **kwargs):
        if db_type == "postgresql":
            return PostgresDatabase(
                host=kwargs.get("host"),
                database=kwargs.get("database"),
                user=kwargs.get("user"),
                password=kwargs.get("password"),
                port=kwargs.get("port"),
            )
        elif db_type == "sqlite":
            return SQLiteDatabase(db_path=kwargs.get("db_path"))
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
