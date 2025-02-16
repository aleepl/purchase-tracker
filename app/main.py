import argparse
from db.init import init
from etl.ingest.receipt import insert_receipt
from etl.personal.purchase import insert_purchase
from etl.personal.item import insert_item
from utils.logger import log_msg

@log_msg(message="Purchase tracker pipeline", slack_log=True, add_breakline=False)
def main():
    parser = argparse.ArgumentParser(
        description="Purchase Tracker arguments",
    )
    parser.add_argument("--db_init", action="store_true", help="Initialize Database schema")
    parser.add_argument("--file_id", type=str, required=True, default=None, help="Slack file id to be processed")

    args = parser.parse_args()
    db_init = args.db_init
    file_id = args.file_id

    if db_init:
        init()

    # Ingest schema
    insert_receipt(file_id)

    # Personal schema
    insert_purchase()
    insert_item()
        

if __name__=="__main__":
    import sys

    # Simulate passing command-line arguments
    sys.argv = ["main.py", "--db_init", "--file_id", "F087CDQAE4U"]
    main()
