from scrape_menu import get_menu
from get_sentiment_and_summary import get_res_link
import pandas as pd
import os

project_directory = os.path.dirname(os.path.abspath(__file__))

df = pd.read_csv(f"{project_directory}Database/sentiment_and_summary_database.csv")

for index, res_name in enumerate(df["Name"][5:15]):
    res_link = get_res_link(res_name)
    get_menu(res_name, res_link)
