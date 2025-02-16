from db.models.base import BaseTable
from sqlalchemy import ForeignKey, UniqueConstraint, Identity, Column, Integer, String, FLOAT, BOOLEAN

class PersonalItem(BaseTable):
    __tablename__ = "item"
    __table_args__ = (
        # Unique constraint
        UniqueConstraint("purchase_id", "code"),

        # Schema definition
        {"schema": "personal"}
    )

    id = Column(Integer, Identity(always=True), primary_key=True, nullable=False)
    code = Column(String, nullable=False)
    name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(FLOAT, nullable=True)
    is_discount = Column(BOOLEAN, nullable=False)
    purchase_id = Column(Integer, ForeignKey("personal.purchase.id", ondelete="CASCADE"), nullable=False)

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

    def update(self,session,receipt_id:int,code:int,**kwargs):
        """
        Update table

        Args:
            photo (str): Photo's storage path
            item_code (str): Product's code bar

        Raises:
            ValueError: Missing kwargs argument.
        """
        # Query the row to update
        row = session.query(self.__class__).filter_by(receipt_id=receipt_id, code=code).first()
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