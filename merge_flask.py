from flask import Flask, request, jsonify
from flask_cors import CORS
from scrape_reviews import get_reviews
from get_sentiment_and_summary import get_sentiment_and_summary
from get_competerior_links import get_competetior_links
from get_menu_list import get_menu_list
from scrape_menu import get_menu
from compare_menus import compare_menus
import pandas as pd
import csv
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

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
project_directory = os.path.dirname(os.path.abspath(__file__))
restaurant_database = f"{project_directory}/Database/restaurant_database.csv"
sentiment_and_summary_db = (
    f"{project_directory}/Database/sentiment_and_summary_database.csv"
)

# Load the restaurant database
df = pd.read_csv(restaurant_database)


def get_res_name(restaurant_link):
    restaurant_name = None
    for index, row in df.iterrows():
        if restaurant_link in row["Link"]:
            restaurant_name = row["Name"]
    # restaurant_name = df.loc[restaurant_link, "Name"]

    if restaurant_name == None:
        print("Went through the if statement of get_res_name function")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(restaurant_link)
        restaurant_name = driver.find_element(
            By.XPATH,
            '//*[@id="root"]/div/main/div/section[3]/section/section/div/div/div/h1',
        )
        restaurant_name = restaurant_name.text
        with open(
            restaurant_database, "a", newline="", encoding="utf-8"
        ) as restaurant_db:
            res_db_writer = csv.writer(restaurant_db)
            res_db_writer.writerow([restaurant_name, restaurant_link])

    return restaurant_name.lower().replace(" ", "_")


def make_query(search_text):
    query_list = search_text.lower().split(" ")
    query = f"{query_list[0]}"
    for query_term in query_list[1:]:
        query = query + f"+{query_term}"

    return query


def get_res_link_not_in_db(res_name_input):
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(f"https://google.com/search?q={make_query(res_name_input)}+zomato")
    new_element = driver.find_element(
        By.XPATH,
        '//*[@id="kp-wp-tab-overview"]/div[1]/div/div/div/div/div/div[1]/div/div/span/a',
    )
    new_link = new_element.get_attribute("href")

    return new_link


# default?]
@app.route("/")
def index():
    return {"message": "Welcome to the Restaurant Comparator API!"}


@app.route("/analyze_sentiment/", methods=["POST"])
def analyze_sentiment():
    req = request.get_json()
    restaurant_name = req["query"]
    restaurant_name = restaurant_name.lower()
    print(restaurant_name)
    df = pd.read_csv(restaurant_database)

    res_name_in = restaurant_name.split(" ")
    print(res_name_in)
    df = pd.read_csv(restaurant_database)
    res_link = None
    res_name = None
    for index, row in df.iterrows():
        all_present = True
        for word in res_name_in:
            if word.lower() not in row["Link"]:
                all_present = False

        if all_present:
            res_link = row["Link"]
            res_name = row["Name"]
            print("Found the res")
            break
    if res_link == None:
        print("Going through the other condtion of the 1st res")
        res_link = get_res_link_not_in_db(restaurant_name)
        res_name = get_res_name(res_link)
        print("res found FINALLY")

    res_name = res_name.lower().replace(" ", "_")
    print(res_name, res_link)
    global res_list
    res_list = []
    res_list.append(res_name)  # store res_name to compare menus afterwards
    # get reviews of the orignal searched restaurant
    get_reviews(res_name, res_link)
    get_menu(res_name, res_link)
    df_sum = pd.read_csv(sentiment_and_summary_db)
    sentiment_with_summary = {}
    # get cpompetetior links
    compe_links = get_competetior_links(res_link)

    if res_name not in df_sum["Name"].values:
        print("Went through the 1st condtion if")
        sentiment_with_summary[1] = get_sentiment_and_summary(res_name)
        with open(
            sentiment_and_summary_db, "a", newline="", encoding="utf-8"
        ) as write_summaray:
            writer = csv.writer(write_summaray)
            writer.writerow(
                [
                    res_name,
                    sentiment_with_summary[1]["sentiment"],
                    sentiment_with_summary[1]["summary"],
                    sentiment_with_summary[1]["dinein_ratings"],
                    sentiment_with_summary[1]["delivery_ratings"],
                    sentiment_with_summary[1]["img_link"],
                ]
            )
    else:
        print("Went through the 2nd condtion else")
        print(f"{res_name} alreadys has summary and sentiment stored")
        for index, row in df_sum.iterrows():
            if row["Name"] == res_name:
                sentiment_with_summary[1] = {
                    "res_name": res_name,
                    "sentiment": row["Sentiment"],
                    "summary": row["Summary"],
                    "dinein_ratings": row["Dinein_ratings"],
                    "delivery_ratings": row["Delivery_ratings"],
                    "img_link": row["Img_link"],
                }
    # get competetior reviews
    j = 2
    for link in compe_links:

        comp_res_name = get_res_name(link)
        get_reviews(comp_res_name, link)
        get_menu(comp_res_name, link)
        res_list.append(comp_res_name)
        if comp_res_name not in df_sum["Name"].values:
            print("Went through the 1st condtion if")
            sentiment_with_summary[j] = get_sentiment_and_summary(comp_res_name)
            with open(
                sentiment_and_summary_db, "a", newline="", encoding="utf-8"
            ) as write_summaray:
                writer = csv.writer(write_summaray)
                writer.writerow(
                    [
                        comp_res_name,
                        sentiment_with_summary[j]["sentiment"],
                        sentiment_with_summary[j]["summary"],
                        sentiment_with_summary[j]["dinein_ratings"],
                        sentiment_with_summary[j]["delivery_ratings"],
                        sentiment_with_summary[j]["img_link"],
                    ]
                )
            j += 1
        else:
            print("Went through the 2nd condtion else")
            print(f"{comp_res_name} alreadys has summary and sentiment stored")
            for index, row in df_sum.iterrows():
                if row["Name"] == comp_res_name:
                    sentiment_with_summary[j] = {
                        "res_name": comp_res_name,
                        "sentiment": row["Sentiment"],
                        "summary": row["Summary"],
                        "dinein_ratings": row["Dinein_ratings"],
                        "delivery_ratings": row["Delivery_ratings"],
                        "img_link": row["Img_link"],
                    }
                    j += 1
    print(sentiment_with_summary)
    print(res_list)
    sentiment_with_summary[1]["Menu"] = get_menu_list(res_name)
    return jsonify(sentiment_with_summary)


@app.route("/compare_menu/", methods=["POST"])
def compare_menu():
    print(res_list)
    req = request.get_json()
    dish_name = req["query"]
    return_dict = {}
    compared_menus = compare_menus(res_list, dish_name)

    for i in range(len(compared_menus)):
        return_dict[i] = compared_menus[i]

    return jsonify(return_dict)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
