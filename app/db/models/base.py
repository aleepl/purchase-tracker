from abc import ABCMeta, abstractmethod
from sqlalchemy.orm import as_declarative, DeclarativeMeta

# Custom metaclass combining ABCMeta and DeclarativeMeta
class DeclarativeABCMeta(ABCMeta, DeclarativeMeta):
    pass

@as_declarative(metaclass=DeclarativeABCMeta)
class BaseTable:
    """Base class for all tables."""

    @abstractmethod
    def insert(self, session, data):
        """Insert data into the table."""
        pass

    @abstractmethod
    def update(self, session, filters, updates):
        """Update data in the table."""
        pass

if __name__=="__main__":
    print(type(BaseTable))