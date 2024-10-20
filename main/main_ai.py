import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import time
import openai
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd

import mock
from database.db import log_to_db
from emails.fetch import get_last_email_from, get_urls_from_html
from images.functions import generate_image, edit_image
from instagram.functions import publish_to_instagram
from text.functions import generate_post_text, get_post_text, check_post_text

BASE_PATH = '/Users/vale/Developer/pycharm/insta-AI-automation/'
model = "gpt-4o"

load_dotenv(BASE_PATH + '.env')
openai.api_key = os.getenv('OPENAI_API_KEY')
current_time = time.strftime("%Y-%m-%d-%H-%M")
client = OpenAI()
cost = 0

df = pd.read_csv(BASE_PATH + "logs.csv", index_col=0)
body = get_last_email_from('dan@tldrnewsletter.com')
urls = get_urls_from_html(body)

text = get_post_text(urls[1])
check, cost_t = check_post_text(client, text, df[-2:])
cost += cost_t
if check["compliant"] == "yes":
    text = get_post_text(urls[1])
json_post_text, cost_t = generate_post_text(client, text, model)
cost += cost_t
# json_post_text = mock.json_post_text
generated_img_path, image_prompt, cost_t = generate_image(client, json_post_text, df[-2:]["image_prompt"], current_time,
                                                          model)
cost += cost_t
# image_prompt = mock.image_prompt
# generated_img_path = mock.img_path
edited_img_path = edit_image(generated_img_path, json_post_text)
# edited_img_path = mock.edited_img_path
published = publish_to_instagram(edited_img_path, json_post_text)
log_to_db(df, json_post_text, edited_img_path, published, image_prompt, current_time)

print(f"Executed successfully run at {current_time} with a total cost of $ {round(cost, 3)}")
