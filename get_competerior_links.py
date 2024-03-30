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


def get_competetior_links(og_link):
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(og_link)

    links = []
    for i in range(1,4):
        try:
            xpath = f'//*[@id="root"]/div/main/div/section[4]/section/section/article[1]/section[2]/section/div/section/section/section/section/section[{i}]/div/a[1]'
            link_element = driver.find_element(By.XPATH, xpath)
            links.append(link_element.get_attribute("href"))
        except:
            print("Couldnt find the link element")    

    driver.quit()    
    
    return links







