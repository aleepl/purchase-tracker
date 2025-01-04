import os
from dotenv import load_dotenv
from datetime import datetime

# Common settings for all environments
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
DOTENV_PATH = os.path.join(BASE_DIR,".env")

# Load environment variables
load_dotenv(DOTENV_PATH)

class Settings:
    # Current timestamp parameters
    timenow: datetime = datetime.now()
    executation_day: str = timenow.strftime("%Y%m%d")
    execution_time: str = timenow.strftime("%Hh%Mm%Ss")
    # Slack
    slack_app_token: str = os.environ.get("SLACK_OAUTH_TOKEN")
    slack_success_channel: str = os.environ.get("SLACK_SUCCESS_CHANNEL")
    slack_error_channel: str = os.environ.get("SLACK_ERROR_CHANNEL")
    # Configurations
    logging_target: str = os.environ.get("SLACK_ERROR_CHANNEL")
    # Databases
    finance_db: str = os.environ.get("FINANCE_DATABASE")
    finance_db_type: str = os.environ.get("FINANCE_DATABASE_TYPE")
    finance_db_host: str = os.environ.get("FINANCE_DATABASE_HOST")
    finance_db_username: str = os.environ.get("FINANCE_DATABASE_USERNAME")
    finance_db_password: str = os.environ.get("FINANCE_DATABASE_PASSWORD")
    finance_db_port: str = os.environ.get("FINANCE_DATABASE_PORT")
    # Paddle OCR Model
    ocr_language: str = os.environ.get("OCR_LANGUAGE")
    ocr_version: str = os.environ.get("OCR_VERSION")
    ocr_base_dir: str = os.environ.get("OCR_BASE_DIR")
    receipt_y_tolerance: str = os.environ.get("OCR_BASE_DIR")


settings = Settings()

if __name__ == "__main__":
    print(settings.timenow)
    print(settings.executation_day)
    print(settings.execution_time)
    print(settings.slack_app_token)
    print(settings.slack_success_channel)
    print(settings.slack_error_channel)
