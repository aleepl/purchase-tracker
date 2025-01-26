import re
from datetime import datetime


def identify_date_format(date):

    if re.match(r"\d{4}/\d{2}/\d{2}",date):
        return datetime.strptime(date, "%Y/%m/%d").strftime("%Y/%m/%d")
    elif re.match(r"\d{2}/\d{2}/\d{4}",date):
        return datetime.strptime(date, "%d/%m/%Y").strftime("%Y/%m/%d")
    elif re.match(r"\d{2}/\d{2}/\d{2}",date) and int(date.split("/")[-1]) >= 12:
        return datetime.strptime(date, "%d/%m/%y").strftime("%Y/%m/%d")
    elif re.match(r"\d{2}/\d{2}/\d{2}",date) and int(date.split("/")[0]) >= 12:
        return datetime.strptime(date, "%y/%m/%d").strftime("%Y/%m/%d")

    return None