import os
import time
import html2text
import openai
import requests
import json
from openai import OpenAI
from dotenv import load_dotenv
from string import Template
from requests_html import HTMLSession
from PIL import Image, ImageFont, ImageDraw
from copy import deepcopy
from instagrapi import Client
import mock
import pandas as pd

load_dotenv('.env')
openai.api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI()
current_time = time.strftime("%Y-%m-%d-%H-%M")


def generate_image(json_post):
    post_desc_prompt = f'''post description:
    {json_post["post_caption"]}

    Prompt for Text-to-Image Language Model: '''

    system_message = f'''Your task is to generate a text prompt for a text-to-image language model.
    Pretend to be an SMM, content writer, and Virtual Assistant for Instagram.
    I will give you a post description and your goal is to suggest me a post image prompt, for that post, that I will ingest in an image generative model.'''

    completion = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        temperature=0.0,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": post_desc_prompt}
        ]
    )

    image_prompt = completion.choices[0].message.content

    response = client.images.generate(
        model="dall-e-3",
        prompt=image_prompt,
        size="1024x1024",
        quality="standard",  # hd
        n=1,
        response_format="url",
        style="vivid"  # natural
    )

    image_url = response.data[0].url
    request = requests.get(image_url, stream=True)
    generated_image = Image.open(request.raw)
    generated_image.show()
    img_path = f"images/generated/{current_time}.png"
    generated_image.save(img_path)

    return img_path


def generate_post_text(text):
    post_desc_prompt = '''[POST TOPIC]:
$page'''

    system_message = '''I want you to respond only in English.
Pretend to be an SMM, content writer, and Virtual Assistant for Instagram. 
I will give you a post topic, your goal is to generate a post caption for an Instagram post regarding that topic. 
Captions should contain at least a few paragraphs of text.
Create an engaging Instagram post caption. The caption should contain at least 100-150 words about the topic 
given below. The caption should not contain any hashtags. Do not put the caption into quotes.
At the end of the post provide a list of 15 hashtags with # written in a single line separated with a space character. 
80% of hashtags should be long-tail and 20% should be high-volume hashtags. Do not include any @mentions.
Do not write long DMs, be concise and to the point.

Answer with a JSON object with the following structure:
{
  "main_title": "A captivating title for the post of a maximum of 35 characters.",
  "subtitle": "A captivating subtitle for the post of a maximum of 80 characters.",
  "post_caption": "Your post caption here.",
  "hashtags": "Your hashtags here."
}'''

    post_desc_prompt = Template(post_desc_prompt).substitute(page=text)

    completion = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        response_format={"type": "json_object"},
        temperature=0.0,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": post_desc_prompt}
        ]
    )
    json_text = json.loads(completion.choices[0].message.content)

    return json_text


def get_post_text(url):
    session = HTMLSession()
    html = session.get(url)
    h = html2text.HTML2Text()
    text = h.handle(html.text)
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


def edit_image(image_path, json_post_text):
    generated_image = Image.open(image_path)

    shadow = Image.open("images/const/shadow.png")
    generated_image.paste(shadow.convert('RGBA'), (0, 0), shadow)
    logo = Image.open("images/const/logo.png")
    generated_image.paste(logo.convert('RGBA'), (0, 0), logo)

    title = json_post_text["main_title"]
    size_b, size = 55, 55
    font_b = ImageFont.truetype('TTLakesNeueCond-Bold.ttf', size_b)
    subtitle = json_post_text["subtitle"]
    font = ImageFont.truetype('fonts/TT Lakes Neue Trial Condensed Regular.ttf', size)

    draw = ImageDraw.Draw(generated_image)
    W, H = generated_image.size
    _, _, wt, ht = draw.textbbox((0, 0), title, font=font_b)
    _, _, ws, hs = draw.textbbox((0, 0), subtitle, font=font)

    c = 20
    i = 0
    while wt > W - 2 * c:
        i += 1
        font_b = ImageFont.truetype('TTLakesNeueCond-Bold.ttf', size_b - i)
        _, _, wt, ht = draw.textbbox((0, 0), title, font=font_b)

    if ws > W - 2 * c:
        const = deepcopy(subtitle)
        words = subtitle.split(" ")
        while ws > W - 2 * c - 40:
            words.pop(-1)
            subtitle = " ".join(words)
            _, _, ws, hs = draw.textbbox((0, 0), subtitle, font=font)
        subtitle = " ".join(words) + "\n" + const[len(subtitle) + 1:]
        _, _, ws, hs = draw.textbbox((0, 0), subtitle, font=font)

    draw.text((c, (H - ht - hs) - c), title, font=font_b, fill="white")
    draw.text((c, (H - hs) - c), subtitle, font=font, fill="white")
    generated_image.show()

    final_path = "images/posts/" + image_path.split("/")[-1]
    generated_image.save(final_path)

    return final_path


def publish_to_instagram(photo_path, caption):
    cl = Client()
    cl.login(os.getenv('INSTAGRAM_USERNAME'), os.getenv('INSTAGRAM_PASSWORD'))
    cl.photo_upload(photo_path, caption)
    return True


def log_to_db(json_post_text, img_path, published):
    # values = {"main_title": [json_post_text["main_title"]],
    #           "subtitle": [json_post_text["subtitle"]],
    #           "post_caption": [json_post_text["post_caption"]],
    #           "hashtags": [json_post_text["hashtags"]],
    #           "json": [json.dumps(json_post_text)],
    #           "date": [current_time],
    #           "edited_img_path": [img_path],
    #           "published": [published]}
    # df = pd.DataFrame.from_dict(values).to_csv("logs.csv")

    df = pd.read_csv("logs.csv", index_col=0)
    df.loc[len(df)] = [json_post_text["main_title"], json_post_text["subtitle"], json_post_text["post_caption"],
                       json_post_text["hashtags"], json.dumps(json_post_text), current_time, img_path, published]
    df = df.drop_duplicates(subset=["post_caption"])
    df.to_csv("logs.csv")


if __name__ == "__main__":
    url = "https://www.macrumors.com/2024/02/28/tim-cook-apple-generative-ai-break-new-ground/?utm_source=tldrai"
    # text = get_post_text(url)
    # json_post_text = generate_post_text(text)
    json_post_text = mock.json_post_text
    # generated_img_path = generate_image(json_post_text)
    generated_img_path = mock.img_path
    # edited_img_path = edit_image(generated_img_path, json_post_text)
    edited_img_path = mock.edited_img_path
    publish = input("Do you want to publish to Instagram? (y/n): ")
    published = False
    if publish == "y":
        published = publish_to_instagram(edited_img_path,
                                         json_post_text["post_caption"] + "\n" + json_post_text["hashtags"])
    log_to_db(json_post_text, edited_img_path, published)
    print("Done!")
