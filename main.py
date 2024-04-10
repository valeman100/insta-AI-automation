import os
import time
import openai
import json
from openai import OpenAI
from dotenv import load_dotenv
from requests_html import HTMLSession
import pandas as pd
from images.functions import generate_image, edit_image
from instagram.functions import publish_to_instagram
from text.functions import generate_post_text, clean_string
import mock

handled_errors = (openai.RateLimitError, openai.Timeout, openai.BadRequestError)

load_dotenv('.env')
openai.api_key = os.getenv('OPENAI_API_KEY')
current_time = time.strftime("%Y-%m-%d-%H-%M")
client = OpenAI()


def get_post_text(url):
    session = HTMLSession()
    html = session.get(url)
    text = clean_string(html.text)
    text = text.strip()
    return text

    # from selenium import webdriver
    #
    # # Set up options for the Chrome WebDriver
    # options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Optional: Run in headless mode without opening a browser window
    #
    # # Initialize the WebDriver
    # driver = webdriver.Chrome(options=options)
    #
    # # Load the webpage
    # driver.get(url)
    #
    # # Get the page source after JavaScript execution
    # html = driver.page_source
    #
    # # Close the WebDriver
    # driver.quit()


def log_to_db(df, json_post_text, img_path, published, image_prompt):
    # values = {"main_title": [json_post_text["main_title"]],
    #           "subtitle": [json_post_text["subtitle"]],
    #           "post_caption": [json_post_text["post_caption"]],
    #           "hashtags": [json_post_text["hashtags"]],
    #           "json": [json.dumps(json_post_text)],
    #           "date": [current_time],
    #           "edited_img_path": [img_path],
    #           "published": [published]
    #           "image_prompt": [image_prompt]}
    # df = pd.DataFrame.from_dict(values).to_csv("logs.csv")

    df.loc[len(df)] = [json_post_text["main_title"], json_post_text["subtitle"], json_post_text["post_caption"],
                       json_post_text["hashtags"], json.dumps(json_post_text), current_time,
                       img_path, published, image_prompt]
    # df = df.drop_duplicates(subset=["post_caption"])
    df.to_csv("logs.csv")


if __name__ == "__main__":
    df = pd.read_csv("logs.csv", index_col=0)
    url = os.getenv('URL')
    text = get_post_text(url)
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
