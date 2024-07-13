import json

from main import current_time


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
