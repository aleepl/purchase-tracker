import os
import cv2
import re
import copy
import numpy as np
import pandas as pd
from paddleocr import PaddleOCR
from app.config.settings import settings, BASE_DIR
from app.db.database import Database
from app.utils.logger import log_msg
from app.utils.slack_tools import Slack
from app.utils.utility import identify_date_format
from datetime import datetime
from app.db.models.ingest_receipt import IngestReceipt

def transform(receipt_path: str) -> pd.DataFrame:
    # Parameters
    ocr_language = settings.ocr_language
    ocr_version = settings.ocr_version
    ocr_base_dir = os.path.join(BASE_DIR, settings.ocr_base_dir, settings.ocr_version)

    # Regex expressions
    stores = ["costco","home depot","saq","canadian tire","maxi","metro"]
    rg_receipt_store = re.compile("|".join(stores))
    rg_receipt_address = re.compile(r"\d+[\s,]+[a-zA-Z0-9\s,\.]+[a-zA-Z]{2,}[\s,]+[A-Z0-9]{3}\s*[A-Z0-9]{3}")
    rg_receipt_date = re.compile(r"\d{2,4}[-/]\d{2}[-/]\d{2}|\d{2}[-/]\d{2}[-/]\d{2,4}")
    rg_receipt_time = re.compile(r"\d{2}:\d{2}(:\d{2})?")
    rg_receipt_tax = re.compile(r"tps|tvh|tvp|tvq", flags=re.IGNORECASE)
    rg_receipt_start_sub_total = re.compile(r"(\d+[\s,\.]?\d+\ssous-total|sous-total\d+[\s,\.]?\d+)", flags=re.IGNORECASE)
    rg_receipt_end_total = re.compile(r"\stotal\s[\d\.,]+|([\d\.,]+\stotal)", flags=re.IGNORECASE)
    rg_receipt_total = re.compile(r"^total", flags=re.IGNORECASE)

    rg_item_code = re.compile(r"^\d{4,13}")
    rg_item_name = re.compile(r"\D+/\d{4,13}|\D+")
    rg_item_price = re.compile(r"\d{1,}(?:\,|\.)\d{2,}")
    rg_item_quantity = re.compile(r"(\d{1,})\s*\@\s*")
    rg_item_discount = re.compile(r"TPD/\d{4,13}")
    rg_item_invalid = re.compile(r"(x{4,})",flags=re.IGNORECASE)
    rg_item_no_more = re.compile(r"sous-total|taxe|txke|total|tps|tvh|tvp|tvq",flags=re.IGNORECASE)

    # Retrieve image resolution
    receipt = cv2.imread(receipt_path)
    height, width, _ = receipt.shape

    # Define a region of interest (ROI) centered around the receipt
    roi_x1 = int(width * 0.2)  # Start at 20% of the width
    roi_x2 = int(width * 0.8)  # End at 80% of the width

    # Crop the region of interest
    roi = receipt[:, roi_x1:roi_x2]

    # Convert to HSV color space
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # Define thresholds for white (high saturation and brightness)
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 55, 255])

    # Create a mask for white areas
    mask = cv2.inRange(hsv, lower_white, upper_white)

    # Perform morphological operations to clean the mask
    kernel = np.ones((5, 5), np.uint8)
    cleaned_mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Find contours in the mask
    contours, _ = cv2.findContours(cleaned_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Identify the largest rectangle contour
    largest_area = 0
    largest_rectangle = None

    for contour in contours:
        # Approximate contour to a polygon
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # Check if it has 4 corners and is convex
        if len(approx) == 4:
            area = cv2.contourArea(contour)
            if area > largest_area:
                largest_area = area
                largest_rectangle = approx

    if largest_rectangle is not None:
        # Get bounding box for the largest contour
        x, y, w, h = cv2.boundingRect(largest_rectangle)

    # Cropped receipt
    cropped_receipt = roi[y:y+h, x:x+w]

    # Extract data from receipt
    ocr = PaddleOCR(lang=ocr_language,
                    det_model_dir=os.path.join(ocr_base_dir,"det"), 
                    rec_model_dir=os.path.join(ocr_base_dir,"rec"),
                    cls_model_dir=os.path.join(ocr_base_dir,"cls"),
                    ocr_version=ocr_version,
                    det=True, # Identifies the locations of text in an image
                    rec=True, # Recognizes the text from cropped images or detected regions
                    cls=True, # Determines the orientation of text
                    use_angle_cls=True,
                    )
    result = ocr.ocr(cropped_receipt)

    # Extract text and bounding box positions
    text_data = []
    for line in result[0]:
        bbox, text_confidence = line
        text = text_confidence[0]
        confidence = text_confidence[1]
        
        x1, y1 = bbox[0]  # Top-left corner of the bounding box
        text_data.append({'text': text, 'y1': y1,})

    # Sort text by top-left y-coordinate (vertical position)
    text_data.sort(key=lambda item: item['y1'])

    # Get sorted only text
    sorted_text = [row["text"] for row in text_data]

    # Step 1: Extract general information about the receipt
    full_text = " ".join(sorted_text)

    # Get text from subtotal to total with cad spent for each
    start_total_pos = rg_receipt_start_sub_total.search(full_text).span()[0]
    end_total_pos = rg_receipt_end_total.search(full_text).span()[1]
    total_text = full_text[start_total_pos:end_total_pos]
    item = list(dict.fromkeys(re.findall(r"[a-zA-Z/-]+",total_text)))
    value = list(dict.fromkeys(re.findall(r"[\d\.,]+",total_text)))

    # Cocatenate total items
    if len(item) == len(value):
        receipt_data = dict(zip(item,value))
    else:
        raise ValueError("Lenght of keys is not the same as values")

    # Add some other variables
    receipt_data["photo"] = receipt_path
    receipt_data["tax"] = sum([float(receipt_data[key].replace(",",".")) if rg_receipt_tax.search(key) else 0 for key in receipt_data.keys()])
    receipt_data["total"] = sum([float(receipt_data[key].replace(",",".")) if rg_receipt_total.search(key) else 0 for key in receipt_data.keys()])
    receipt_data["store"] = rg_receipt_store.search(full_text).group() if rg_receipt_store.search(full_text) else None
    receipt_data["address"] = rg_receipt_address.search(full_text).group() if rg_receipt_address.search(full_text) else None
    receipt_data["date"] = rg_receipt_date.search(full_text).group().replace("-","/") if rg_receipt_date.search(full_text) else None
    receipt_data["date_modified"] = identify_date_format(receipt_data["date"])
    receipt_data["time"] = rg_receipt_time.search(full_text).group() if rg_receipt_time.search(full_text) else None
    receipt_data["time_modified"] = receipt_data["time"]+":00" if len(receipt_data["time"])<=5 else receipt_data["time"]
    receipt_data["timestamp"] = datetime.strptime(receipt_data["date_modified"] + " " + receipt_data["time_modified"], "%Y/%m/%d %H:%M:%S")

    # Initialize variables
    item_data = []
    empty_row = {"item_code": None, "item_name": None, "item_price": None, "item_quantity": 1, "item_is_discount": False}
    row = copy.deepcopy(empty_row)

    # Process each line of sorted text
    for idx,text in enumerate(sorted_text):
        # Search for all patterns
        search_item_code = rg_item_code.search(text)
        search_item_name = rg_item_name.search(text)
        search_item_price = rg_item_price.search(text)
        search_item_quantity = rg_item_quantity.search(text)
        search_item_discount = rg_item_discount.search(text)
        search_item_invalid = rg_item_invalid.search(text)
        search_item_no_more = rg_item_no_more.search(text)

        # Skip invalid items
        if search_item_invalid:
            continue

        # Break loop if no more items found
        if search_item_no_more:
            break

        # Update row based on matches
        if search_item_quantity:
            row["item_quantity"] = int(search_item_quantity.group(1))
        elif search_item_price:
            if row["item_price"]:
                item_data.append(row)
                row = copy.deepcopy(empty_row)
            row["item_price"] = search_item_price.group(0)
        elif search_item_code or search_item_name:
            if row["item_code"]:
                item_data.append(row)
                row = copy.deepcopy(empty_row)
            if search_item_discount:
                row["item_is_discount"] = True
            if search_item_code:
                row["item_code"] = search_item_code.group(0)
            if search_item_name:
                row["item_name"] = search_item_name.group(0)

    # Append last row
    if (len(sorted_text) == idx+1) and (row["item_code"] or row["item_name"] or row["item_price"]):
        item_data.append(row)
    
    # Create DataFrames from extracted data
    receipt_columns = ["photo","store","address","timestamp","tax","total"]
    df_item = pd.DataFrame(item_data)
    df_receipt = pd.DataFrame([{key:val for key,val in receipt_data.items() if key in receipt_columns}])
    df = df_receipt.merge(df_item,how="cross")

    # Filter invalid records
    df = df[df["item_code"].notnull() & df["item_name"].notnull() & df["item_price"].notnull()].copy()

    # Standarization
    df["item_price"] = df["item_price"].str.replace(",",".")

    return df

def get_loads(df_old, df_new) -> None:
    # Create a composite key
    df_old["key"] = df_old["photo"] + "_" + df_old["item_code"].astype("string")
    df_new["key"] = df_new["photo"] + "_" + df_new["item_code"].astype("string")

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

    return inserts, updates
    
@log_msg(message="Insert ingest receipt", slack_log=True, add_breakline=True)
def insert_receipt(file_id):
    # Create db client
    finance_db = Database(connection_string=settings.finance_db_url,autocommit=True)
    finance_session = finance_db.get_session()

    # Open queries
    with open(os.path.join(BASE_DIR,"app","db","queries","extract","ingest_receipt.sql"),"r") as query:
        old_receipt_query = query.read()

    # Download file
    file_path = Slack(settings.slack_app_token).download_file(file_id,settings.slack_receipt_dir)

    # Extract
    old_receipt_cols,old_receipt_rows = finance_db.execute_query(query=old_receipt_query)
    df_old_receipt = pd.DataFrame(data=old_receipt_rows,columns=old_receipt_cols)

    # Transform
    df_new_receipt = transform(file_path)

    # Load
    inserts, updates = get_loads(df_old_receipt,df_new_receipt)
    with finance_session.begin():
        finance_session.bulk_insert_mappings(IngestReceipt, inserts)
        finance_session.bulk_update_mappings(IngestReceipt, updates)
    finance_db.close_session()


if __name__=="__main__":
    insert_receipt("F087CDQAE4U")