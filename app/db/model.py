from sqlalchemy import Column, Integer, String, JSON, TIMESTAMP, func
from db.base import Base

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    table_name = Column(String, nullable=False)
    operation_type = Column(String, nullable=False)
    changed_at = Column(TIMESTAMP, server_default=func.now())
    user_name = Column(String, nullable=True)
    old_data = Column(JSON, nullable=True)
    new_data = Column(JSON, nullable=True)
