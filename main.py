import os

import html2text
import openai
from openai import OpenAI
from dotenv import load_dotenv
from string import Template
from requests_html import HTMLSession

load_dotenv('.env')
openai.api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI()


def generate_image(image_prompt):
    if image_prompt:
        response = client.images.generate(
            model="dall-e-3",
            prompt=image_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
            response_format="url",
            style="vivid"  # natural
        )

        image_url = response.data[0].url

    return image_url


def generate_description(url):
    # generate post description
    post_desc_prompt = '''I want you to respond only in English.
    Pretend to be an SMM, content writer and my Virtual Assistant for Instagram. 
    I will give you a post topic, your goal is to suggest me a post caption for that post. 
    Captions should contain at least a few paragraphs of text.
    Create an engaging Instagram post captions. Each caption should contain at least 100-150 words about the topic 
    given below. Captions should not contain any hashtags. Do not put Captions into quotes.
    At the end of the post provide a list of 15 hashtags with # written in a single line separated with a space character. 
    80% of hashtags should be long-tail and 20% should be high-volume hashtags. Do not include any @mentions.
    Do not write long DMs, be concise and to the point.

    [TOPIC POST]:
    $page

    [POST CAPTION AND HASHTAGS]:'''

    session = HTMLSession()
    html = session.get(url)
    h = html2text.HTML2Text()
    text = h.handle(html.text)
    text = text.strip()

    post_desc_prompt = Template(post_desc_prompt).substitute(page=text)

    completion = client.chat.completions.create(
        model="gpt-4-1106-preview",
        temperature=0.0,
        messages=[
            # {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": post_desc_prompt}
        ]
    )

    return completion.choices[0].message.content


def generate_post(image_prompt=None, url=None):
    if image_prompt:
        image_url = generate_image(image_prompt)
    if url:
        post_desc = generate_description(url)


if __name__ == "__main__":
    generate_post(
        "A photograph of a white Siamese cat.",
        "https://openai.com/blog/new-models-and-developer-products-announced-at-devday?itm_source=tldrai")

    print("Done!")
