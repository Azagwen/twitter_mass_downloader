from datetime import datetime
from pathlib import Path

import json
import os
import requests
import twitter


# TODO: fix externally hosted videos being incorrectly encoded (Fixed I think ? I forgot lol)
# Issue root : proxy videos
# possible solution : https://stackoverflow.com/questions/32145166/get-video-from-tweet-using-twitter-api


def get_api():
    url_input = Path("tokens.json")

    if Path(url_input).exists():
        with open(url_input) as f:
            data = json.loads(f.read())
    else:
        print(f"{Path} not found.")
        return

    return twitter.Api(
        consumer_key=data["consumer_key"],
        consumer_secret=data["consumer_secret"],
        access_token_key=data["access_token_key"],
        access_token_secret=data["access_token_secret"],
        sleep_on_rate_limit=True
    )


# Define main variables
api = get_api()
api.tweet_mode = "extended"
logger = []
fail_logger = []
url_history = []


def remove_if_present(input_list: list, target: str):
    if target in input_list:
        input_list.remove(target)


def get_status_and_author_from_url(url: str) -> tuple:
    split_url = url.split("/")
    remove_if_present(split_url, "photo")
    remove_if_present(split_url, "1")
    remove_if_present(split_url, "2")
    remove_if_present(split_url, "3")
    remove_if_present(split_url, "4")
    status_id = split_url.pop(len(split_url) - 1)
    user_id = split_url.pop(len(split_url) - 2)

    return f"@{user_id}", status_id.split("?")[0]


def open_input() -> dict:
    url_input = Path("input.json")

    if Path(url_input).exists():
        with open(url_input) as f:
            data = f.read()
    else:
        print("input.json not found.")
        return dict()

    return json.loads(data)


def open_dev_input() -> dict:
    url_input = Path("test_input.json")

    if Path(url_input).exists():
        with open(url_input) as f:
            data = f.read()
    else:
        print("test_input.json not found.")
        return dict()

    return json.loads(data)


def get_folders_in_input() -> tuple:
    json_file = open_dev_input()

    for (folder, url) in json_file.items():
        return str(folder), str(url)


def download_images_v2(input_data):
    url = input_data[1]
    current_status = ""
    media_index = 0

    if isinstance(url, str):
        current_status = get_status_and_author_from_url(url)
    elif isinstance(url, dict):
        current_status = get_status_and_author_from_url(url["url"])
        media_index = url["media_index"]

    try:
        tweet_json = json.loads(api.GetStatus(current_status[1]).AsJsonString())
    except twitter.TwitterError:
        print(f"Error encountered with: {url}")
        fail_logger.append(f"Error encountered with: {url}")
        url_history.append(url)
        return

    if "media" not in tweet_json:
        print(f"No media found in: {url}")
        fail_logger.append(f"No media found in: {url}")
        url_history.append(url)
        return
    else:
        tweet_media = tweet_json["media"]

        if isinstance(url, str):
            index = 0
            for media_data in tweet_media:
                wirte_media(input_data, current_status, index, media_data, False)
                url_history.append(url)
                index += 1
        elif isinstance(url, dict):
            wirte_media(input_data, current_status, media_index, tweet_media[media_index - 1], True)


def wirte_media(input_data: tuple, current_status: tuple, index: int, media_data: dict, is_forced_index: bool):
    target_folder = input_data[0]
    folder_list = input_data[2]
    current_folder = ""
    matched = ""
    path = Path("output")
    author_name = f"{current_status[0]}_{current_status[1]}_0{str(index).zfill(1)}"

    # Check the folder list to see if the folder our URL has to go into has a variable for it.
    # Might get slow if user has a lot of folder variables
    for folder in folder_list:
        # Match found, the target folder is already defined, so we get its full ame and move on
        if folder == target_folder:
            current_folder = folder_list[folder]
            matched = f"Matched ( {folder}: {folder_list[folder]} ), "
            break
        # No Match found, the target folder is set as the destination by default
        current_folder = target_folder

    # Check if the folder name is forcefully undefined, dump in output folder if True
    if "__none__" not in current_folder and current_folder != "":
        output_path = f"{path}/{current_folder}"
        create_directory(
            path=output_path,
            notice=False
        )
    else:
        output_path = path

    # Check if media data is of a video, if not, grab the image key instead
    if "video_info" in media_data:
        tweet_media = media_data["video_info"]["variants"][0]["url"]
    else:
        tweet_media = media_data["media_url_https"]

    # Determine the media's extension
    if ".jpg" in tweet_media:
        extension = "jpg"
    elif ".png" in tweet_media:
        extension = "png"
    elif ".mp4" in tweet_media:
        extension = "mp4"
    elif ".gif" in tweet_media:
        extension = "gif"
    else:
        extension = "txt"

    # Write the media file
    with open(f"{output_path}/{author_name}.{extension}", 'wb') as f:
        f.write(requests.get(tweet_media).content)

    # Print sucess statement
    forced_index_str = ""
    if is_forced_index:
        v = "th"
        if index == 1:
            v = "st"
        elif index == 2:
            v = "nd"
        forced_index_str = f", {index + 1}{v} media"
    print(f"{matched}{current_folder}/{forced_index_str}, {tweet_media}, {author_name}")
    logger.append(f"{tweet_media}, {author_name}")


def multi_download_images(input_data):
    for (data) in input_data.items():
        for (url) in data[1]:
            if data[0] != "__comment" and data[0] != "folder_list":
                folder_list = json.loads(str(input_data["folder_list"]).replace("\'", "\""))
                download_images_v2((str(data[0]), url, folder_list))


def create_directory(path, notice: bool):
    final_path = Path(path)

    try:
        os.makedirs(final_path)
    except FileExistsError:
        if notice:
            print(f'"{final_path}" already exists, doing nothing.')
        else:
            pass


def create_directories():
    path_output = Path("output")
    path_logs = Path("logs")

    create_directory(
        path=path_output,
        notice=True
    )
    create_directory(
        path=path_logs,
        notice=True
    )


def write_logs():
    now = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    path = Path("logs")

    with open(f"{path}/log_{now}.json", "w") as f:
        f.write(json.dumps(logger, indent=4))

    if fail_logger != "[]" or len(fail_logger) > 0:
        with open(f"{path}/fails_log_{now}.json", "w") as f:
            f.write(json.dumps(fail_logger, indent=4))

    with open(f"{path}/url_history_{now}.json", "w") as f:
        f.write(json.dumps(url_history, indent=4))


print(json.dumps(open_input(), indent=4))
create_directories()
multi_download_images(open_input())
write_logs()
