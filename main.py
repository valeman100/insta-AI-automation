import os
import time
import openai
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd
from database.db import log_to_db
from email.fetch import get_last_email_from, get_urls_from_html
from images.functions import generate_image, edit_image
from instagram.functions import publish_to_instagram
from text.functions import generate_post_text, get_post_text

handled_errors = (openai.RateLimitError, openai.Timeout, openai.BadRequestError)

load_dotenv('.env')
openai.api_key = os.getenv('OPENAI_API_KEY')
current_time = time.strftime("%Y-%m-%d-%H-%M")
client = OpenAI()

df = pd.read_csv("logs.csv", index_col=0)
body = get_last_email_from('dan@tldrnewsletter.com')
urls = get_urls_from_html(body)
text = get_post_text(urls[0])
json_post_text = generate_post_text(client, text)
# json_post_text = mock.json_post_text
generated_img_path, image_prompt = generate_image(client, json_post_text, df[-2:]["image_prompt"], current_time)
# image_prompt = mock.image_prompt
# generated_img_path = mock.img_path
edited_img_path = edit_image(generated_img_path, json_post_text)
# edited_img_path = mock.edited_img_path

publish = input(f"Do you want to publish to Instagram? (y/n): \n\n {json_post_text['post_caption']}")
published = False
if publish == "y":
    published = publish_to_instagram(edited_img_path, json_post_text)
log_to_db(df, json_post_text, edited_img_path, published, image_prompt)

print("Done!")
