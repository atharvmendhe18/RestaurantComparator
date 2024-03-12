from fastapi import FastAPI, HTTPException
from scrape_reviews import get_reviews
from get_sentiment import get_sentiment
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
        if res_name_in[0] in row["Link"] and res_name_in[1] in row["Link"]:
            res_link = row["Link"]
            res_name = row["Name"]
            print("Found the res")


    def get_res_name(restaurant_link):
        for index, row in df.iterrows():
            if restaurant_link in row["Link"]:
                restaurant_name = row["Name"]

        return restaurant_name.lower().replace(" ","_")


    res_name = res_name.lower().replace(" ","_")
    print(res_name, res_link)

    get_reviews(res_name,res_link)
    compe_links = get_competetior_reviews(res_link)

    for link in compe_links:
        get_reviews(get_res_name(link), link)
    sentiment_score = get_sentiment(res_name)
    return {"restaurant_name": restaurant_name, "sentiment_score": sentiment_score}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
