import os
from instagrapi import Client


def publish_to_instagram(photo_path, json_post_text):
    caption = json_post_text["post_caption"] + "\n\n" + json_post_text["hashtags"]

    cl = Client()
    cl.login(os.getenv('INSTAGRAM_USERNAME'), os.getenv('INSTAGRAM_PASSWORD'))
    cl.photo_upload(photo_path, caption)
    return True
