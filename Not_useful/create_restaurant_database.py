from selenium import webdriver

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import csv
import string


driver = webdriver.Chrome(options=chrome_options)
# the below script was used to create the restaurant database
with open(
    "data_collection\web_scraping\estaurant_database.csv",
    "w",
    newline="",
    encoding="utf-8",
) as restaurant_csv:
    restaurant_writer = csv.writer(restaurant_csv)

    restaurant_writer.writerow(["Name", "Link"])

    for letter in string.ascii_lowercase:
        page_number = 1
        len_resto_elements = 1
        page_link = f"https://www.zomato.com/mumbai/directory/restaurants-{letter}-1"
        while len_resto_elements != 0:
            driver.get(page_link)
            restaurant_elements = driver.find_elements(By.CLASS_NAME, "plr10")
            len_resto_elements = len(restaurant_elements)

            for restaurant_element in restaurant_elements:
                tag = restaurant_element.find_element(By.TAG_NAME, "a")
                restaurant_writer.writerow([tag.text, tag.get_attribute("href")])

            page_number += 1
            page_link = f"https://www.zomato.com/mumbai/directory/restaurants-{letter}-{page_number}"


driver.quit()
