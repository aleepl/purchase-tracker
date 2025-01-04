import logging
import os

from config.settings import settings
from app.utils.slack_tools import Slack


# Logging paths
log_filename = f"execution_time={settings.execution_time}.log"
log_target = os.path.join(settings.logging_target, f"{settings.executation_day}", log_filename)

# Create local dirname if it doesn't exist
os.makedirs(os.path.dirname(log_target), exist_ok=True)

# Logging configurations
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create handlers
stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler(log_target)

# Set format to handlers
log_fomatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
stream_handler.setFormatter(log_fomatter)
file_handler.setFormatter(log_fomatter)

# Add handlers to logger
logger.addHandler(stream_handler)
logger.addHandler(file_handler)


def log_msg(message, slack_log=False, add_breakline=False):
    def wrap(func):
        def wrapper(*args, **kwargs):
            try:
                message_read_success_start = "[+] %s started."
                logger.debug(message_read_success_start, message)

                df = func(*args, **kwargs)

                message_read_success_end = "[+] %s completed."
                logger.debug(message_read_success_end, message)
                if add_breakline:
                    logger.debug("[+]")
                if slack_log:
                    Slack(settings.slack_app_token).post_message(
                        settings.slack_success_channel, message_read_success_end % message
                    )
                return df
            except Exception as e:
                message_read_failure = "[-] %s failed. Please check"
                logger.exception(message_read_failure, message)
                if slack_log:
                    Slack(settings.slack_app_token).post_message(
                        settings.slack_error_channel, message_read_failure % message
                    )
                raise e

        return wrapper

    return wrap


if __name__ == "__main__":
    print(settings.execution_time)
    print(settings.logging_target)
    print(settings.executation_day)
