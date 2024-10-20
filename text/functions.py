import json
import re
from pprint import pp
from string import Template
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from selenium import webdriver
from utilities.cost_calculation import calculate_cost


def generate_post_text(client, text, model="gpt-4o"):
    post_desc_prompt = '''[POST TOPIC]:
$page'''

    system_message = '''I want you to respond only in English.
Pretend to be a social media manager, content writer, and Virtual Assistant for my instagram page which focuses on Artificial Inteligence an thech news. 
I will give you a post topic with a description, your goal is to generate a post caption for an Instagram post regarding that topic. 
Create an engaging Instagram post caption divided into paragraphs. 
The caption should contain at least 100-150 words about the topic given below. 
The caption should contain emojis preferably at the beginning of each paragraph.

Do not write long DMs, be concise and to the point.
Do not include any hashtags or @mentions in the caption.

Answer with a JSON object with the following structure:
{
  "main_title": "A captivating title for the post of a maximum of 35 characters.",
  "subtitle": "A captivating subtitle for the post of a maximum of 80 characters.",
  "post_caption": "Your post caption here.",
  "hashtags": "Provide a list of 15 hashtags with # written in a single line separated with a space character. 
80% of hashtags should be long-tail and 20% should be high-volume hashtags. Do not include any @mentions."
}'''

    post_desc_prompt = Template(post_desc_prompt).substitute(page=text)

    completion = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        temperature=0.0,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": post_desc_prompt}
        ]
    )
    json_text = json.loads(completion.choices[0].message.content)
    json_text["post_caption"] = json_text["post_caption"][:json_text["post_caption"].find("#")]
    pp(json_text)
    cost = calculate_cost(completion)

    return json_text, cost


def clean_string(html):
    soup = BeautifulSoup(html, features="lxml")
    for br in soup.find_all("br"):
        br.replace_with("\n")
    text = soup.get_text()
    text = re.sub(r'(\n+\s+)+', '\n', text)
    text = re.sub(r'\t+', ' ', text)
    text = text.replace(u'\xa0', ' ')
    return text


def from_html_to_text(url):
    session = HTMLSession()
    html = session.get(url)
    text = clean_string(html.text)
    text = text.strip()
    return text


def from_selenium_to_text(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Optional: Run in headless mode without opening a browser window
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    html = driver.page_source
    text = clean_string(html)
    text = text.strip()

    driver.quit()
    if len(text) < 500:
        raise ValueError("Text is too short")
    return text


def get_post_text(url):
    text = from_html_to_text(url)
    if len(text) < 500:
        text = from_selenium_to_text(url)
    return text


def check_post_text(client, post, previous_posts, model="gpt-4o"):
    user_message = '''Title one: $previous_post_1
Title two: $previous_post_2

post description: $post'''

    system_message = ''' I'll give you two post titles.
Your task is to check if one of the following titles would be compliant with the description below.

Answer with a JSON object with the following structure:
{"compliant": a string with yes if one of the titles is compliant or no otherwise}'''

    post_1 = previous_posts["main_title"].iloc[0] + " - " + previous_posts["subtitle"].iloc[0]
    post_2 = previous_posts["main_title"].iloc[1] + " - " + previous_posts["subtitle"].iloc[1]

    user_message = Template(user_message).substitute(
        post=post,
        previous_post_1=post_1,
        previous_post_2=post_2
    )

    completion = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        temperature=0.0,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    )
    json_text = json.loads(completion.choices[0].message.content)
    cost = calculate_cost(completion)

    return json_text, cost
