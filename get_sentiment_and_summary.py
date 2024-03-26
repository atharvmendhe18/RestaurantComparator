from transformers import pipeline
import pandas as pd

from selenium import webdriver

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument('--headless')
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument(
#     "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
# )
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import csv
import os


restaurant_database = r"/Users/atharvmendhe/Documents/Zomato_compatator/RestaurantComparator/Database/restaurant_database.csv"
sentiment_and_summary_db = r"/Users/atharvmendhe/Documents/Zomato_compatator/RestaurantComparator/Database/sentiment_and_summary_database.csv"


df = pd.read_csv(restaurant_database)
df_sen_sum = pd.read_csv(sentiment_and_summary_db)


def get_res_link(restaurant_name):
    restaurant_link = None
    for index, row in df.iterrows():
        restaurant_name = restaurant_name.lower().replace(" ", "_")
        if restaurant_name == row["Name"].lower().replace(" ", "_"):
            restaurant_link = row["Link"]
            break
    print(f"Getting res link for {restaurant_name}")
    print(restaurant_link)
    return restaurant_link


pipe_SentimentAnalysis = pipeline(
    "text-classification",
    model="lxyuan/distilbert-base-multilingual-cased-sentiments-student",
    return_all_scores=True,
    device=-1,
)

pipe_ReviewSummarization = pipeline(
    "summarization", model="Falconsai/text_summarization"
)


def get_sentiment_and_summary(res_name):
    df = pd.read_csv(
        f"/Users/atharvmendhe/Documents/Zomato_compatator/RestaurantComparator/Database/{res_name}_reviews.csv",
        encoding="utf-8",
    )
    df.dropna(axis=0, inplace=True)
    sentiments = []
    final_sentiment = None
    total_reviews = ""
    for review in df["Review"]:
        sentiments.append(pipe_SentimentAnalysis(review)[0])
        total_reviews += f" {review}"

    sentiment_dict = {
        "positive": 0,
        "negative": 0,
    }

    for sentiment in sentiments:
        if sentiment[0]["score"] > 0.4:
            sentiment_dict["positive"] += 1
        else:
            sentiment_dict["negative"] += 1

    if sentiment_dict["positive"] > sentiment_dict["negative"]:
        final_sentiment = "Positive"
    else:
        final_sentiment = "Negative"

    summary = pipe_ReviewSummarization(total_reviews)

    driver = webdriver.Chrome(options=chrome_options)
    dine_in_ratings = None
    delivery_ratings = None
    img_link = None
    driver.get(get_res_link(res_name))
    try:
        dine_in_ratings = driver.find_element(
            By.XPATH,
            '//*[@id="root"]/div/main/div/section[3]/section/section/div/div/div/section/div[1]/div[1]/div/div/div[1]',
        )
        dine_in_ratings = dine_in_ratings.text
    except:
        print("Couldnt find dine in ratings")

    try:
        delivery_ratings = driver.find_element(
            By.XPATH,
            '//*[@id="root"]/div/main/div/section[3]/section/section/div/div/div/section/div[3]/div[1]/div/div/div[1]',
        )
        delivery_ratings = delivery_ratings.text
    except:
        print("Couldnt find delivery ratings")

    try:
        img_link = driver.find_element(
            By.XPATH, '//*[@id="root"]/div/main/div/section[2]/div[1]/div/div/img'
        )
        img_link = img_link.get_attribute("src")

    except:
        print("Couldnt finf img link")

    return {
        "res_name": res_name,
        "sentiment": final_sentiment,
        "summary": summary,
        "dinein_ratings": dine_in_ratings,
        "delivery_ratings": delivery_ratings,
        "img_link": img_link,
    }
