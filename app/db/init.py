import os
from db.models.base import BaseTable
from db.database import Database
from config.settings import settings,BASE_DIR
from utils.logger import log_msg

@log_msg(message="Database initiation", slack_log=True, add_breakline=True)
def init():
    # Database initiation
    finance_db = Database(connection_string=settings.finance_db_url,autocommit=True)

    # Schemas
    schemas = ["ingest",
               "personal"]
    for schema in schemas:
        finance_db.create_schema(schema)

    # Initiation of all tables
    BaseTable.metadata.create_all(finance_db.engine)

    # Initiation objects within ingest schema
    schema = "ingest"

    # Functions
    functions = ["audit_change"]
    for function in functions:    
        with open(os.path.join(BASE_DIR,"db","queries","create","function",f"{schema}_{function}.sql"), "r") as query_file:
            query = query_file.read()
            finance_db.execute_update(query)

    # Triggers
    triggers = ["receipt_audit"]
    for trigger in triggers:    
        with open(os.path.join(BASE_DIR,"db","queries","create","trigger",f"{schema}_{trigger}.sql"), "r") as query_file:
            query = query_file.read()
            finance_db.execute_update(query)
            
    # Initiation objects within personal schema
    schema = "personal"

    # Functions
    functions = ["audit_change"]
    for function in functions:
        with open(os.path.join(BASE_DIR,"db","queries","create","function",f"{schema}_{function}.sql"), "r") as query_file:
            query = query_file.read()
            finance_db.execute_update(query)

    # Triggers
    triggers = ["item_audit",
                "purchase_audit"]
    for trigger in triggers:    
        with open(os.path.join(BASE_DIR,"db","queries","create","trigger",f"{schema}_{trigger}.sql"), "r") as query_file:
            query = query_file.read()
            finance_db.execute_update(query)

if __name__=="__main__":
    init()