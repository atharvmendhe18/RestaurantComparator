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



# input links sorted in other file system, direct zomato link will be provided
def get_reviews(res_name, res_link):
    
  
    restaurant_name = res_name # this name will be obtained form the database 

    file_path = f'C:\Desktop\Codes\Zomato_comparator\Database\{restaurant_name}_reviews.csv'
    if not os.path.exists(file_path):
        with open(file_path, 'w', newline='', encoding='utf-8') as reviews:
            reviews_writer  = csv.writer(reviews)
            driver = webdriver.Chrome(options=chrome_options)
            reviews_writer.writerow(["Review"])
            next_page_link = res_link
            for _ in range(2,20):
                driver.get(next_page_link)
                time.sleep(3)
                review_elements = driver.find_elements(By.XPATH, '//*[@id="root"]/div/main/div/section[4]/div/div/section/div[2]/p')
                #rating_elements = driver.find_elements(By.XPATH, '//*[@id="root"]/div/div[2]/div[3]/div/div/section/div[2]/div[1]/div/div[1]/div/div/div[1]')
                # print(review_elements,rating_elements)
                for review in review_elements:
                    # print(review.text)
                    reviews_writer.writerow([review.text])

            
                            
                next_page_link = f"{res_link}/reviews?page={_}&sort=dd&filter=reviews-dd"

                
        driver.quit()
    else:
        print(f"The file '{file_path}' already exists. So skipping the scraping part")

