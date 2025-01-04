import os
import cv2
import re
import copy
import numpy as np
import pandas as pd
from paddleocr import PaddleOCR
from app.config.settings import Settings, BASE_DIR

def transform(receipt: np.ndarray) -> pd.DataFrame:
    # Parameters
    ocr_language = Settings.ocr_language
    ocr_version = Settings.ocr_version
    ocr_base_dir = os.path.join(BASE_DIR, Settings.ocr_base_dir, Settings.ocr_version)

    # Regex expressions
    rg_code = re.compile(r"^\d{4,13}")
    rg_item = re.compile(r"\D+/\d{4,13}|\D+")
    rg_price = re.compile(r"\d{1,}(?:\,|\.)\d{2,}")
    rg_quantity = re.compile(r"(\d{1})\s*\@\s*")
    rg_discount = re.compile(r"TPD/\d{4,13}")
    rg_invalid_item = re.compile(r"(x{4,})|sous-total|taxe|txke|total",flags=re.IGNORECASE)

    # Retrieve image resolution
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

    # Initialize variables
    data = []
    empty_row = {"code": None, "item": None, "price": None, "quantity": 1, "is_discount": False}
    row = copy.deepcopy(empty_row)

    # Process each line of sorted text
    for idx,text in enumerate(sorted_text):
        # Search for all patterns
        search_code = rg_code.search(text)
        search_item = rg_item.search(text)
        search_price = rg_price.search(text)
        search_quantity = rg_quantity.search(text)
        search_discount = rg_discount.search(text)
        search_invalid_item = rg_invalid_item.search(text)

        # Skip invalid items
        if search_invalid_item:
            continue

        # Update row based on matches
        if search_quantity:
            row["quantity"] = int(search_quantity.group(1))
        elif search_price:
            if row["price"]:
                data.append(row)
                row = copy.deepcopy(empty_row)
            row["price"] = search_price.group(0)
        elif search_code or search_item:
            if row["code"]:
                data.append(row)
                row = copy.deepcopy(empty_row)
            if search_discount:
                row["is_discount"] = True
            if search_code:
                row["code"] = search_code.group(0)
            if search_item:
                row["item"] = search_item.group(0)

    # Append last row
    if (len(sorted_text) == idx+1) and (row["code"] or row["item"] or row["price"]):
        data.append(row)
    
    # Create DataFrame from data extracted
    df = pd.DataFrame(data)

    # Filter invalid records
    df = df[df["code"].notnull() & df["item"].notnull() & df["price"].notnull()].copy()

    # Standardization
    df["code"] = df["code"].astype("Int64")
    df["item"] = df["item"].astype("string")
    df["price"] = df["price"].str.replace(",",".").astype(float)
    df["quantity"] = df["quantity"].astype("Int64")
    df["is_discount"] = df["is_discount"].astype(bool)

    return df

def load() -> None:
    # Compare current state of the data with new run

    # Insert new data

    # Update existing data

    # Delete deleted data

    

def insert_product(source_path):
    # Extract
    receipt = cv2.imread(source_path)

    # Transform
    df_product = transform(receipt)

    # Load



if __name__=="__main__":
    insert_product(".\\.tests\\data\\IMG_0881.jpg")