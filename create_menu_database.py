from scrape_menu import get_menu
from get_sentiment_and_summary import get_res_link
import pandas as pd

df = pd.read_csv("Database/sentiment_and_summary_database.csv")

for index, res_name in enumerate(df["Name"][5:15]):
    res_link = get_res_link(res_name)
    get_menu(res_name, res_link)
