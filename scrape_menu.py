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
project_directory = os.path.dirname(os.path.abspath(__file__))

# input links sorted in other file system, direct zomato link will be provided
def get_menu(res_name, res_link):

    restaurant_name = res_name  # this name will be obtained from the database
    file_path = f"{project_directory}/Database/Menu/{restaurant_name}_menu.csv"
    if not os.path.exists(file_path):
        with open(file_path, "w", newline="", encoding="utf-8") as menu:
            order_link = f"{res_link}/order"
            menu_writer = csv.writer(menu)
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(order_link)
            menu_elements = driver.find_elements(
                By.CLASS_NAME,
                "sc-1s0saks-15.iSmBPS",
            )
            price_elements = driver.find_elements(By.CLASS_NAME, "sc-17hyc2s-1.cCiQWA")
            menu_elements = [menu_element.text for menu_element in menu_elements]
            price_elements = [price_element.text for price_element in price_elements]

            menu_writer.writerow(["Name", "Price"])

            for menu_item, price_item in zip(menu_elements, price_elements):
                menu_writer.writerow([menu_item, price_item])

            print(menu_elements, price_elements)
            print(len(menu_elements), len(price_elements))
    else:
        print(f"Skipping the menu scrapping for the {res_name} as it already exists.")


if __name__ == "__name__":
    get_menu()
