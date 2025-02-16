from datetime import datetime
from db.models.base import BaseTable
from sqlalchemy import text, Index, Identity, Column, Integer, String, TIMESTAMP, JSON

class IngestAuditLog(BaseTable):
    __tablename__ = "audit_log"
    __table_args__ = (
        # Index for table_name
        Index("idx_audit_log_table_name", "table_name", unique=False),

        # Schema definition
        {"schema": "ingest"},
    )

    id = Column(Integer, Identity(always=True), primary_key=True, nullable=False)
    table_name = Column(String(255), nullable=False)
    operation_type = Column(String(255), nullable=False)
    changed_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    user_name = Column(String(255), nullable=True, server_default=text("CURRENT_USER"))
    old_data = Column(JSON, nullable=True)
    new_data = Column(JSON, nullable=True)

    def insert(self, session, **kwargs):
        """
        Insert a new row into the table.

        Args:
            session: SQLAlchemy session object.
            kwargs: Column names and their corresponding values to insert.

        Raises:
            ValueError: If no columns or invalid columns are provided.
        """
        if not kwargs:
            raise ValueError("No data provided for insertion")

        # Validate column names
        for key in kwargs.keys():
            if not hasattr(self.__class__, key):
                raise ValueError(f"Column '{key}' does not exist in the table")

        # Create a new instance of the table with the provided data
        new_row = self.__class__(**kwargs)

        # Add the new row to the session and commit
        session.add(new_row)
        session.commit()

    def update(self,session,table_name:str,operation_type:str,changed_at:datetime,usern_name:str,**kwargs):
        """
        Update table

        Args:
            photo (str): Photo's storage path
            item_code (str): Product's code bar

        Raises:
            ValueError: Missing kwargs argument.
        """
        # Query the row to update
        row = session.query(self.__class__).filter_by(table_name=table_name,operation_type=operation_type,changed_at=changed_at,usern_name=usern_name).first()
        if not row:
            raise ValueError("Row not found with the given photo and item_code")

        # Update the attributes
        for key, value in kwargs.items():
            if hasattr(row, key):  # Ensure the column exists
                setattr(row, key, value)
            else:
                raise ValueError(f"Column '{key}' does not exist in the table")

        # Commit the changes
        session.commit()