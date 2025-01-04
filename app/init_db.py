import os
from db.database import DatabaseFactory
from config.settings import Settings,BASE_DIR

def init_db():
    # Database initiation
    db_factory = DatabaseFactory()
    finance_db = db_factory.get_database(db_type=Settings.finance_db_type,
                                         database=Settings.finance_db,
                                         host=Settings.finance_db_host,
                                         user=Settings.finance_db_username,
                                         password=Settings.finance_db_password)
    finance_db.connect()

    # Schemas
    schemas = ["personal"]
    for schema in schemas:
        with open(os.path.join(BASE_DIR,"db","queries",f"create_{schema}_schema.sql"), "r") as query:
            finance_db.execute_update(query)

    # Initiation objects within personal schema
    # Tables
    tables = ["audit_log",
              "receipt",
              "product"]
    for table in tables:    
        with open(os.path.join(BASE_DIR,"db","queries","personal","tables",f"create_{table}.sql"), "r") as query:
            finance_db.execute_update(query)

    # Functions
    triggers = ["audit_change"]
    for trigger in triggers:    
        with open(os.path.join(BASE_DIR,"db","queries","personal","functions",f"create_{trigger}.sql"), "r") as query:
            finance_db.execute_update(query)

    # Triggers
    triggers = ["product_audit_trigger",
                "receipt_audit_trigger"]
    for trigger in triggers:    
        with open(os.path.join(BASE_DIR,"db","queries","personal","triggers",f"create_{trigger}.sql"), "r") as query:
            finance_db.execute_update(query)

if __name__=="__main__":
    init_db()