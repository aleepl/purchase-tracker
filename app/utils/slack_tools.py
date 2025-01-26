import os
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class Slack:
    def __init__(self, token):
        self.token = token
        self.client = WebClient(token=token)

    def download_file(self, file, target):
        try:
            response = self.client.files_info(file=file)
            file_info = response["file"]
        except SlackApiError as e:
            print(f"Error fetching file info: {e.response['error']}")

        # Extract event metadata
        if file_info["mimetype"].startswith("image/"):
            file_url = file_info.get("url_private")
            file_channel = file_info.get("channels")[0]
            file_name = file_info.get("name")

        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(file_url, headers=headers)

        if response.status_code != 200:
            raise requests.exceptions.RequestException(
                "Download request has failed. Status code {}".format(response.status_code)
            )

        os.makedirs(os.path.join(target, file_channel), exist_ok=True)
        saved_file_path = os.path.join(target, file_channel, file_name)

        with open(saved_file_path, "wb") as f:
            f.write(response.content)
        
        return saved_file_path

    def post_message(self, channel, message):
        self.client.chat_postMessage(channel=channel, text=message)


if __name__ == "__main__":
    slack_token = os.environ.get("SLACK_OAUTH_TOKEN")
    file_id = "F087C5Y53H6"
    target_folder = ".\\data\\slack"
    # Slack(slack_token).download_file(file_id,target_folder)
