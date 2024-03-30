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

driver = webdriver.Chrome(options=chrome_options)
    permantly_closed = driver.find_element(
        By.XPATH,
        '//*[@id="root"]/div/main/div/section[3]/section/section/div/div/section[2]/section/span',
    )
    if permantly_closed.text == "Permanently Closed":
        print("The restaurant is permanently closed. Skipping scraping.")
        driver.quit()
        return