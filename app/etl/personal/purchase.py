import os
import pandas as pd
from db.database import Database
from config.settings import settings, BASE_DIR
from db.models.personal_purchase import PersonalPurchase
from utils.logger import log_msg

def transform(df_receipt):
    # Get needed columns
    columns = ["photo","store","address","timestamp","tax","total"]
    df = df_receipt[columns].copy()

    # Drop duplicates
    df.drop_duplicates(inplace=True)

    return df

def get_loads(df_old, df_new) -> None:
    # Create a composite key
    df_old["key"] = df_old["photo"]
    df_new["key"] = df_new["photo"]

    # Set the composite key as index
    df_old.set_index("key", inplace=True)
    df_new.set_index("key", inplace=True)

    # Identify inserts
    inserts = df_new[~df_new.index.isin(df_old.index)].to_dict(orient="records")

    # Identify updates
    df_new["id"] = df_new.index.map(df_old.to_dict(orient="dict")["id"])
    df_old = df_old[[col for col in sorted(df_old.columns)]].copy()
    df_new = df_new[[col for col in sorted(df_new.columns)]].copy()
    common_keys = df_old.index.intersection(df_new.index)

    if common_keys.empty:
        df_diff = pd.DataFrame(columns=df_new.columns)
    else:
        df_diff = df_new.loc[common_keys].compare(df_old.loc[common_keys])
    df_updates = df_new.loc[df_diff.index]
    updates = df_updates.to_dict(orient="records")

    # Identify deletes
    deletes = df_old[~df_old.index.isin(df_new.index)].to_dict(orient="records")

    return inserts, updates, deletes

@log_msg(message="Insert personal purchase", slack_log=True, add_breakline=True)
def insert_purchase():
    # Create db client
    finance_db = Database(connection_string=settings.finance_db_url,autocommit=True)
    finance_session = finance_db.get_session()

    # Open queries
    with open(os.path.join(BASE_DIR,"db","queries","extract","personal_purchase.sql"),"r") as query:
        old_purchase_query = query.read()
    with open(os.path.join(BASE_DIR,"db","queries","extract","ingest_receipt.sql"),"r") as query:
        old_receipt_query = query.read()

    # Extract
    old_purchase_cols,old_purchase_rows = finance_db.execute_query(query=old_purchase_query)
    df_old_purchase = pd.DataFrame(data=old_purchase_rows,columns=old_purchase_cols)

    old_receipt_cols,old_receipt_rows = finance_db.execute_query(query=old_receipt_query)
    df_old_receipt = pd.DataFrame(data=old_receipt_rows,columns=old_receipt_cols)

    # Transform
    df_new_purchase = transform(df_old_receipt)

    # Load
    inserts, updates, deletes = get_loads(df_old_purchase,df_new_purchase)
    with finance_session.begin():
        finance_session.bulk_insert_mappings(PersonalPurchase, inserts)
        finance_session.bulk_update_mappings(PersonalPurchase, updates)
        finance_session.query(PersonalPurchase).filter(PersonalPurchase.id.in_([row["id"] for row in deletes])).delete()
    finance_db.close_session()

if __name__=="__main__":
    insert_purchase()