from scrape_reviews import get_reviews
from get_sentiment import get_sentiment
from get_competerior_links import get_competetior_reviews
import pandas as pd

restaurant_database = r"C:\Desktop\Restaurant_Comparator\data_collection\web_scraping\restaurant_database.csv"

# take input form user about the restaurant
res_name_in = input("Please enter Restaurant name: ").lower().split(' ')

df = pd.read_csv(restaurant_database)
res_link = None
res_name = None
for index, row in df.iterrows():
    if res_name_in[0] in row["Link"] and res_name_in[1] in row["Link"]:
        res_link = row["Link"]
        res_name = row["Name"]


def get_res_name(restaurant_link):
    for index, row in df.iterrows():
        if restaurant_link in row["Link"]:
            restaurant_name = row["Name"]

    return restaurant_name.lower().replace(" ","_")


res_name = res_name.lower().replace(" ","_")

get_reviews(res_name,res_link)
compe_links = get_competetior_reviews(res_link)

for link in compe_links:
    get_reviews(get_res_name(link), link)

print("Searched res Sentiment: ",get_sentiment(res_name))

 










