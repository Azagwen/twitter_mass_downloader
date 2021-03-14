from datetime import datetime
from pathlib import Path

import json
import os
import requests
import twitter


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


api = get_api()
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


def GetStatusInfoFromURL(url: str):
    split_url = url.split("/")
    status_id = split_url.pop(len(split_url) - 1)
    user_id = split_url.pop(len(split_url) - 2)
    return f"@{user_id}", status_id


def download_images(url: str):
    current_status = GetStatusInfoFromURL(url)

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
            tweet_image = m["media_url_https"]
            author_name = f"{current_status[0]}_{current_status[1]}_0{str(i).zfill(1)}"
            r = requests.get(tweet_image)

            with open(f"{author_name}.png", 'wb') as f:
                f.write(r.content)

            print(f"{tweet_image}, {author_name}")
            logger.append(f"{tweet_image}, {author_name}")
            url_history.append(url)
            i = i + 1


def get_videos():
    url = "https://twitter.com/Zdenalie/status/1248908614103793664"

    current_status = GetStatusInfoFromURL(url)
    tweet_json = json.loads(api.GetStatus(current_status[1]).AsJsonString())
    new_url = tweet_json["urls"][0]["expanded_url"]
    new_status = GetStatusInfoFromURL(new_url)
    new_tweet_json = json.loads(api.GetStatus(new_status[1]).AsJsonString())

    print(json.dumps(new_tweet_json, indent=4))


def multi_download_images(url_list):
    for url in url_list:
        download_images(url)


def write_logs():
    now = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")

    try:
        os.mkdir("logs")
    except FileExistsError:
        print('"logs/" already exists, doing nothing.')

    with open(f"logs/log_{now}.json", "w") as f:
        f.write(json.dumps(logger, indent=4))

    if len(fail_logger) > 0:
        with open(f"logs/fails_log_{now}.json", "w") as f:
            f.write(json.dumps(fail_logger, indent=4))

    with open(f"logs/url_history_{now}.json", "w") as f:
        f.write(json.dumps(url_history, indent=4))


print(json.dumps(open_input(), indent=4))
multi_download_images(open_input())
write_logs()



