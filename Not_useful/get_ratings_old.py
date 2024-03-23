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
import pandas as pd


restaurant_database = r"C:\Desktop\/Codes\Zomato_comparator\Database\/restaurant_database.csv"
sentiment_and_summary_db = r"C:\Desktop\/Codes\Zomato_comparator\Database\/sentiment_and_summary_database.csv"
df = pd.read_csv(restaurant_database)
df_sen_sum = pd.read_csv(sentiment_and_summary_db)

def get_res_link(restaurant_name):
    restaurant_link = None
    for index, row in df.iterrows():
        restaurant_name = restaurant_name.lower().replace(" ","_")
        if restaurant_name ==  row["Name"].lower().replace(" ",'_'):
            restaurant_link= row["Link"]   
            break
    print(f"Getting res link for {restaurant_name}")    
    print(restaurant_link)    
    return restaurant_link



dine_in_ratings_list = []
delivery_ratings_list = []
img_links = []
driver = webdriver.Chrome(options=chrome_options)
for index, row in df_sen_sum.iterrows():
    dine_in_ratings = None
    delivery_ratings = None
    driver.get(get_res_link(row['Name']))
    try:
        dine_in_ratings = driver.find_element(By.XPATH,'//*[@id="root"]/div/main/div/section[3]/section/section/div/div/div/section/div[1]/div[1]/div/div/div[1]')
        dine_in_ratings_list.append(dine_in_ratings.text)
    except:
        print('Couldnt find dine in ratings')
        dine_in_ratings_list.append("")

    try:
        delivery_ratings = driver.find_element(By.XPATH,'//*[@id="root"]/div/main/div/section[3]/section/section/div/div/div/section/div[3]/div[1]/div/div/div[1]')
        delivery_ratings_list.append(delivery_ratings.text)
    except:
        print("Couldnt find delivery ratings")  
        delivery_ratings_list.append("")  

    try:
        img_link = driver.find_element(By.XPATH, '//*[@id="root"]/div/main/div/section[2]/div[1]/div/div/img')  
        img_links.append(img_link.get_attribute('src'))  
        print(img_link.get_attribute('src'))
    except:
        print("Couldnt finf img link")    
        img_links.append("")



df_sen_sum["Dinein_ratings"] = dine_in_ratings_list
df_sen_sum["Delivery_ratings"] = delivery_ratings_list
df_sen_sum['Img_link'] = img_links

df_sen_sum.to_csv(sentiment_and_summary_db,encoding='utf-8', index=False)
        

        