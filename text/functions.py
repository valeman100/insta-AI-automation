import json
import re
from pprint import pp
from string import Template
from bs4 import BeautifulSoup


def generate_post_text(client, text):
    post_desc_prompt = '''[POST TOPIC]:
$page'''

    system_message = '''I want you to respond only in English.
Pretend to be a social media manager, content writer, and Virtual Assistant for my instagram page which focuses on Artificial Inteligence news. 
I will give you a post topic, your goal is to generate a post caption for an Instagram post regarding that topic. 
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
        model="gpt-4-turbo-preview",
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

    return json_text


def clean_string(html):
    soup = BeautifulSoup(html, features="lxml")
    for br in soup.find_all("br"):
        br.replace_with("\n")
    text = soup.get_text()
    text = re.sub(r'(\n+\s+)+', '\n', text)
    text = re.sub(r'\t+', ' ', text)
    text = text.replace(u'\xa0', ' ')
    return text
