from datetime import datetime
from pathlib import Path

import json
import os
import requests
import twitter


# TODO: fix externally hosted videos being incorrectly encoded
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


def get_status_info_from_url(url: str):
    split_url = url.split("/")
    status_id = split_url.pop(len(split_url) - 1)
    user_id = split_url.pop(len(split_url) - 2)
    return f"@{user_id}", status_id.split("?")[0]


api = get_api()
api.tweet_mode = "extended"
logger = []
fail_logger = []
url_history = []


def open_input():
    url_input = Path("input.json")

    if Path(url_input).exists():
        with open(url_input) as f:
            data = f.read()
    else:
        print("input.json not found.")
        return

    return json.loads(data)


def open_dev_input():
    url_input = Path("test_input.json")

    if Path(url_input).exists():
        with open(url_input) as f:
            data = f.read()
    else:
        print("test_input.json not found.")
        return

    return json.loads(data)


def get_folders_in_input():
    json_file = open_dev_input()

    for (folder, url) in json_file.items():
        return str(folder), str(url)


def download_images_v2(input_data):
    target_folder = input_data[0]
    url = input_data[1]
    folder_list = input_data[2]
    current_folder = ""
    matched = ""
    path = Path("output")

    for f_id in folder_list:
        if f_id == target_folder:
            current_folder = folder_list[f_id]
            matched = f"Matched ( {f_id}: {folder_list[f_id]} ), "
            break

    current_status = get_status_info_from_url(url)
    if not current_folder.__contains__("__none__") and current_folder != "":
        full_path = f"{path}/{current_folder}"
        create_directory(
            path=full_path,
            notice=False
        )
    else:
        full_path = path

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

        i = 0
        for m in tweet_media:
            author_name = f"{current_status[0]}_{current_status[1]}_0{str(i).zfill(1)}"

            if "video_info" in m:
                tweet_media = m["video_info"]["variants"][0]["url"]
            else:
                tweet_media = m["media_url_https"]

            media = requests.get(tweet_media)

            if str(tweet_media).__contains__(".jpg"):
                extension = "jpg"
            elif str(tweet_media).__contains__(".png"):
                extension = "png"
            elif str(tweet_media).__contains__(".mp4"):
                extension = "mp4"
            elif str(tweet_media).__contains__(".gif"):
                extension = "gif"
            else:
                extension = "txt"

            with open(f"{full_path}/{author_name}.{extension}", 'wb') as f:
                f.write(media.content)

            print(f"{matched}{current_folder}/, {tweet_media}, {author_name}")
            logger.append(f"{tweet_media}, {author_name}")
            url_history.append(url)
            i = i + 1


def multi_download_images(input_data):
    for (data) in input_data.items():
        for (url) in data[1]:
            if data[0] != "__comment" and data[0] != "folder_list":
                folder_list = json.loads(str(input_data["folder_list"]).replace("\'", "\""))
                download_images_v2((str(data[0]), str(url), folder_list))


def create_directory(path, notice: bool):
    final_path = Path(path)

    try:
        os.mkdir(final_path)
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


print(json.dumps(open_dev_input(), indent=4))
create_directories()
multi_download_images(open_dev_input())
write_logs()
