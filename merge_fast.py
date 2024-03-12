from fastapi import FastAPI, HTTPException
from scrape_reviews import get_reviews
#from get_sentiment import get_sentiment\
from get_sentiment_and_summary import get_sentiment_and_summary
from get_competerior_links import get_competetior_reviews
import pandas as pd

app = FastAPI()

restaurant_database = r"C:\Desktop\/Codes\Zomato_comparator\Database\/restaurant_database.csv"

# Load the restaurant database
df = pd.read_csv(restaurant_database)

def get_res_name(restaurant_link):
    for index, row in df.iterrows():
        if restaurant_link in row["Link"]:
            restaurant_name = row["Name"]

    return restaurant_name.lower().replace(" ", "_")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Restaurant Comparator API!"}

@app.get("/analyze_sentiment/")
async def analyze_sentiment(restaurant_name: str):
    restaurant_name = restaurant_name.lower()
    df = pd.read_csv(restaurant_database)

    res_name_in = restaurant_name.split(" ")
    print(res_name_in)
    df = pd.read_csv(restaurant_database)
    res_link = None
    res_name = None
    for index, row in df.iterrows():
        all_present = True
        for word in res_name_in:
            if word not in row["Link"]:
                all_present = False

        if all_present:
            res_link = row["Link"]
            res_name = row["Name"]
            print("Found the res")


    res_name = res_name.lower().replace(" ","_")
    print(res_name, res_link)

    #get reviews of the orignal searched restaurant
    get_reviews(res_name,res_link)

    # get cpompetetior links
    compe_links = get_competetior_reviews(res_link)

    # get competetior reviews
    for link in compe_links:
        get_reviews(get_res_name(link), link)

    sentiment_with_summary = {}
    sentiment_with_summary[1] = get_sentiment_and_summary(res_name)
    j = 2
    for link in compe_links:
        sentiment_with_summary[j] = get_sentiment_and_summary(get_res_name(link))
        j += 1

    return sentiment_with_summary

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
