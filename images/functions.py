from copy import deepcopy
import requests
from PIL import Image, ImageFont, ImageDraw

from utilities.cost_calculation import calculate_cost

BASE_PATH = '/Users/vale/Developer/pycharm/insta-AI-automation/'


def generate_image(client, json_post, previous_prompts, current_time, model="gpt-4o"):
    image_url = None
    cost = 0
    post_desc_prompt = f'''Previous Text-to-Image prompts:
1. {previous_prompts.iloc[0]}

2. {previous_prompts.iloc[1]}

Description:
{json_post["post_caption"]}

Prompt for Text-to-Image Model: '''

    system_message = f'''Your task is to generate a text prompt for an artificial intelligence model that generates images.
I will give you a description and your goal is to suggest an image prompt to ingest into an artificial intelligence text-to-image model.
The model will generate an image based on the text prompt you suggest.
The prompt must be:
- captivating, engaging and interesting. 
- compliant with the post description. 
- with specific details about colours and objects that the image will contain. 
- must contain elements present in the description.
- do not put people or writing in the image.

I will also provide you with 2 previous prompts.
Make your prompt different from the previous ones such that the images generated are visually very different from the previous ones.'''

    completion = client.chat.completions.create(
        model=model,
        temperature=0.0,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": post_desc_prompt}
        ]
    )

    image_prompt = completion.choices[0].message.content
    cost += calculate_cost(completion)
    print(f"Cost to generate image prompt: {cost}")

    for i in range(2):
        try:
            image_url, cost_t = dall_e_3(client, image_prompt)
            cost += cost_t
            print(f"Cost to generate image: {cost}")
            break
        except Exception as e:
            print(f"Error: {e}, try another prompt.")
            completion = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                temperature=0.0,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": post_desc_prompt},
                    {"role": "assistant", "content":
                        f"Error: {e}, trying another prompt that could be compliant with this error."}
                ]
            )
            image_prompt = completion.choices[0].message.content
            cost += calculate_cost(completion)

    if not image_url:
        raise Exception("Could not generate image")

    request = requests.get(image_url, stream=True)
    generated_image = Image.open(request.raw)
    # generated_image.show()
    img_path = BASE_PATH + f"images/generated/{current_time}.png"
    generated_image.save(img_path)

    return img_path, image_prompt, cost


def edit_image(image_path, json_post_text):
    generated_image = Image.open(image_path)

    shadow = Image.open(BASE_PATH + "images/const/shadow_new.png")
    generated_image.paste(shadow.convert('RGBA'), (0, 0), shadow)
    logo = Image.open(BASE_PATH + "images/const/logo.png")
    generated_image.paste(logo.convert('RGBA'), (0, 0), logo)

    title = json_post_text["main_title"]
    size_b, size = 55, 55
    font_b = ImageFont.truetype(BASE_PATH + 'text/fonts/TTLakesNeueCond-Bold.ttf', size_b)
    subtitle = json_post_text["subtitle"]
    font = ImageFont.truetype(BASE_PATH + 'text/fonts/TT Lakes Neue Trial Condensed Regular.ttf', size)

    draw = ImageDraw.Draw(generated_image)
    W, H = generated_image.size
    _, _, wt, ht = draw.textbbox((0, 0), title, font=font_b)
    _, _, ws, hs = draw.textbbox((0, 0), subtitle, font=font)

    c = 20
    i = 0
    while wt > W - 2 * c:
        i += 1
        font_b = ImageFont.truetype(BASE_PATH + 'text/fonts/TTLakesNeueCond-Bold.ttf', size_b - i)
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

    final_path = BASE_PATH + "images/posts/" + image_path.split("/")[-1]
    generated_image.save(final_path)

    return final_path


def dall_e_3(client, image_prompt):
    response = client.images.generate(
        model="dall-e-3",
        prompt=image_prompt,
        size="1024x1024",
        quality="standard",  # hd
        n=1,
        response_format="url",
        style="vivid"  # natural
    )

    return response.data[0].url, 0.040
