from selenium import webdriver
from fastapi import FastAPI, HTTPException
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
from transformers import pipeline
import json

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--disable-gpu")

chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import csv
import pandas as pd


pipe_SentimentAnalysis = pipeline(
    "text-classification", model="lxyuan/distilbert-base-multilingual-cased-sentiments-student", return_all_scores = True, device = -1)


pipe = pipeline("token-classification", model="ml6team/keyphrase-extraction-kbir-inspec")
# https://www.amazon.in/s?k=iphone+13

# Flow right now
""" 
1. Search amazon
2. Select top 3 products
3. Go to the product page 
4. Go to the product review page
5. Extract reviews 
"""


def make_query(search_text):
    query_list = search_text.lower().split(" ")
    query = f"{query_list[0]}"
    for query_term in query_list[1:]:
        query = query + f"+{query_term}"

    return query


def search_amazon(query):
    print(f"https://www.amazon.in/s?k={query}")
    return f"https://www.amazon.in/s?k={query}"


# driver.get("https://www.amazon.in/iphone-13/s?k=iphone+13"
def get_amazon_page_list(page_link, product_name):
    driver = webdriver.Chrome(options=chrome_options)
    product_name = product_name.replace(" ", "_")
    driver.get(page_link)
    time.sleep(1)
    with open(
        f"amazon_{product_name}_search.csv", "w", newline="", encoding="utf-8"
    ) as search_page:
        search_writer = csv.writer(search_page)
        search_writer.writerow(
            [
                "Name",
                "Link",
                "Image_link",
                "Price",
                "Number_of_ratings",
                "Discount",
                "Fastes_delivery_date",
                "Bought_last_month",
                "About_iten",
            ]
        )
        for i in range(5, 9):
            xpath_page = f'//*[@id="search"]/div[1]/div[1]/div/span[1]/div[1]/div[{i}]/div/div/span/div/div/div/div[2]/div/div/div[1]/h2/a'
            # //*[@id="search"]/div[1]/div[1]/div/span[1]/div[1]/div[5]/div/div/span/div/div/div/div[2]/div/div/div[1]/h2/a
            # xpath_price = f'//*[@id="search"]/div[1]/div[1]/div/span[1]/div[1]/div[{i}]/div/div/span/div/div/div/div[2]/div/div/div[3]/div[1]/div/div[1]/div[1]/div[1]/a/span/span[2]/span[2]'
            #                #//*[@id="search"]/div[1]/div[1]/div/span[1]/div[1]/div[4]/div/div/div/div/span/div/div/div/div[2]/div/div/div[3]/div[1]/div/div[1]/div[2]/div[1]/a/span/span[2]/span[2]
            # //*[@id="search"]/div[1]/div[1]/div/span[1]/div[1]/div[6]/div/div/span/div/div/div/div[2]/div/div/div[3]/div[1]/div/div[1]/div[2]/div[1]/a/span/span[2]/span[2]
            # xpath_no_of_ratings = f'//*[@id="search"]/div[1]/div[1]/div/span[1]/div[1]/div[{i}]/div/div/span/div/div/div/div[2]/div/div/div[2]/div[1]/span[2]/a/span'

            try:
                page_element = driver.find_element(By.XPATH, xpath_page)
                name = page_element.find_element(By.TAG_NAME, "span")
                # price = driver.find_element(By.XPATH, xpath_price)
                # no_of_ratings = driver.find_element(By.XPATH, xpath_no_of_ratings)
                search_writer.writerow(
                    [
                        name.text,
                        page_element.get_attribute("href"),
                    ]
                )

                print(name.text)
                print(page_element.get_attribute("href"))
                # print(price.text)
                # print(no_of_ratings.text)

            except:
                print("Couldnt find element")


def get_review_page(link, p_name):
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(link)
    WebDriverWait(driver, 5)
    df = pd.read_csv(f"amazon_{p_name}_search.csv")

    reviews_link = driver.find_element(
        By.XPATH, '//*[@id="reviews-medley-footer"]/div[2]/a'
    )

    try:
        image = driver.find_element(By.XPATH, '//*[@id="landingImage"]')
        # //*[@id="landingImage"]
        image_link = image.get_attribute("src")
    except:
        image_link = None
        print("Couldnt find image")
    try:
        price = driver.find_element(
            By.XPATH,
            '//*[@id="corePriceDisplay_desktop_feature_div"]/div[1]/span[3]/span[2]/span[2]',
        )
        print(price.text)
        price = price.text
    except:
        price = None
        print("Couldnt find price")

    try:
        discount = driver.find_element(
            By.XPATH, '//*[@id="corePriceDisplay_desktop_feature_div"]/div[1]/span[2]'
        )
        print(discount.text)
        discount = discount.text
    except:
        discount = None
        print("Couldnt find discount")

    try:
        no_of_ratings = driver.find_element(
            By.XPATH, '//*[@id="acrCustomerReviewText"]'
        )
        print(no_of_ratings.text)
        no_of_ratings = no_of_ratings.text
    except:
        no_of_ratings = None
        print("couldnt find no of ratings")

    about_item = driver.find_element(By.XPATH, '//*[@id="feature-bullets"]/ul')
    print(about_item)
    about_item_para = ""
    about_points = about_item.find_elements(By.TAG_NAME, "span")
    for _ in about_points:
        about_item_para += f"{_.text}"

    try:
        fastest_delivery = driver.find_element(
            By.XPATH,
            '//*[@id="mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE"]/span/span',
        )
        print(fastest_delivery.text)
        fastest_delivery = fastest_delivery.text
    except:
        fastest_delivery = None
        print("Couldnt find fastest_delivery")

    try:
        bought_last_month = driver.find_element(
            By.XPATH, '//*[@id="social-proofing-faceout-title-tk_bought"]/span[1]'
        )
        print(bought_last_month.text)
        bought_last_month = bought_last_month.text
    except:
        bought_last_month = None
        print("couldnt find bought last month")

    new_data = {
        "Image_link": image_link,
        "Price": price,
        "Number_of_ratings": no_of_ratings,
        "Discount": discount,
        "Fastest_delivery_date": fastest_delivery,
        "Bought_last_month": bought_last_month,
        "About_item": about_item_para,
    }

    df.loc[
        df["Link"] == link,
        [
            "Image_link",
            "Price",
            "Number_of_ratings",
            "Discount",
            "Fastest_delivery_date",
            "Bought_last_month",
            "About_item",
        ],
    ] = [
        new_data["Image_link"],
        new_data["Price"],
        new_data["Number_of_ratings"],
        new_data["Discount"],
        new_data["Fastest_delivery_date"],
        new_data["Bought_last_month"],
        new_data["About_item"],
    ]
    df.to_csv(f"amazon_{p_name}_search.csv", index=False)
    print("1st function worked")
    link_r = reviews_link.get_attribute("href")
    driver.quit()
    return link_r


def sanitize_file_name(file_name):
    sanitized_name = re.sub(r'[<>:"/\\|?*]', "_", file_name)
    return sanitized_name


def get_review_elements(review_page_link, p_name):
    print("Starting 2nd function")
    driver = webdriver.Chrome(options=chrome_options)
    with open(
        f"amazon_{p_name}_reviews.csv", "w", newline="", encoding="utf-8"
    ) as reviews:
        review_writer = csv.writer(reviews)
        review_writer.writerow(["reviewer_name", "review_title", "review"])
        for i in range(1, 6):
            review_page = review_page_link + f"&pageNumber={i}"
            # print(review_page)
            driver.get(review_page)

            name_elements = driver.find_elements(By.CLASS_NAME, "a-profile-name")
            title_elements = driver.find_elements(
                By.CSS_SELECTOR, 'a[data-hook="review-title"]'
            )
            review_elements = driver.find_elements(
                By.CSS_SELECTOR, 'span[data-hook="review-body"]'
            )
            # print(len(name_elements), len(title_elements), len(review_elements))
            try:

                for j in range(len(title_elements)):
                    review_writer.writerow(
                        [
                            name_elements[j + 2].text,
                            title_elements[j].text,
                            review_elements[j].text,
                        ]
                    )
            except:
                print()

            # for name in name_elements:
            #     print(name.text)
        driver.quit()

def get_sentiment(product_name):
    print("Starting sentiment analysis")
    df = pd.read_csv(f"C:\Desktop\Restaurant_Comparator\data_collection\web_scraping\/amazon_{product_name}_reviews.csv", encoding='utf-8')
    df.dropna(axis=0, inplace=True)
    sentiments = []
    for review in df['review']:
        print(review)
        sentiments.append(pipe_SentimentAnalysis(review)[0])

    sentiment_dict = {
    'positive': 0,
    'negative': 0,
    }

    for sentiment in sentiments:
        if sentiment[0]['score'] > 0.5:
            sentiment_dict['positive'] += 1
        else:
            sentiment_dict['negative'] += 1  
        
    if sentiment_dict['positive'] > sentiment_dict['negative']:
        return "Positive"
    else:
        return "Negative" 

def get_keywords(direct_text_to_extract):
    keywords_dict = pipe(direct_text_to_extract)
    to_return_list = []

    for i in range(min(20, len(keywords_dict))):
        to_return_list.append(keywords_dict[i]['word'])

    return to_return_list    



def return_json_dict_keywords(product_name_with_underscore):
    df = pd.read_csv(f"amazon_{product_name_with_underscore}_search.csv")
    return_dict = []
    i = 0
    to_append_dict = {}
    for index, row in df.iterrows():
        if i == 0:
            # to_append_dict = {}
            total_review = ""
            p_name = row["Name"].replace(" ","_")
            # sentimet = get_sentiment(p_name)
            to_append_dict["Name"] = row["Name"]
            to_append_dict["Image_link"] = str(row["Image_link"])
            to_append_dict["Price"] = str(row["Price"])
            to_append_dict["Fastes_delivery_date"] = str(row["Fastes_delivery_date"])
            to_append_dict["Bought_last_month"] = str(row["Bought_last_month"])
            to_append_dict["Number_of_ratings"] = str(row["Number_of_ratings"])
            p_name = sanitize_file_name(p_name)
            df = pd.read_csv(f'C:\Desktop\Restaurant_Comparator\data_collection\web_scraping\/amazon_{p_name}_reviews.csv',encoding='utf-8')
            for review in df['review']:
                total_review += str(review)
            keywords = get_keywords(total_review)
            to_append_dict["Keywords"] = keywords   
            return_dict.append(to_append_dict)
            i += 1
    print(to_append_dict)
    return to_append_dict



def return_json_dict_sentiment(product_name_with_underscore):
    df = pd.read_csv(f"amazon_{product_name_with_underscore}_search.csv")
    return_dict = {}
    i = 0
    for index, row in df.iterrows():
        to_append_dict = {}
        p_name = row["Name"].replace(" ","_")
        p_name = sanitize_file_name(p_name)
        sentiment = get_sentiment(p_name)
        to_append_dict["Name"] = row["Name"]
        to_append_dict["Image_link"] = str(row["Image_link"])
        to_append_dict["Price"] = str(row["Price"])
        to_append_dict["Fastes_delivery_date"] = str(row["Fastes_delivery_date"])
        to_append_dict["Bought_last_month"] = str(row["Bought_last_month"])
        to_append_dict["Number_of_ratings"] = str(row["Number_of_ratings"])
        to_append_dict["Sentiment"] = str(sentiment)
        return_dict[f"product{i}"] = to_append_dict
        
    json_data = json.dumps(return_dict)

    print(json_data)
    return json_data


def coupon_price(coupon_price_singal_digit):
    modified_coupon_list = coupon_price_singal_digit.copy()
    if modified_coupon_list[-1] != '0':
        modified_coupon_list[-1] = '0'

    if modified_coupon_list[-2] in ['6', '7', '8'] :
        modified_coupon_list[-2] = '5'

    if modified_coupon_list[-2] in ['4', '3', '2', '1']:
        modified_coupon_list[-2] = '0'
        
    coupon_price = int("".join(modified_coupon_list))

    if modified_coupon_list[-2] == '9':
        convert_to_int = int("".join(modified_coupon_list))
        ten = convert_to_int + 10
        coupon_price = ten

    return coupon_price

def scrape_flipkart_search(query):
    base_url = "https://www.flipkart.com/search"
    params = {"q": query}

    response = requests.get(base_url, params=params)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    search_results = soup.find_all("div", {"class": "_1AtVbE"})

    counter = 0  # Counter to keep track of non-advertisement products
    results = []

    for result in search_results:
        if counter >= 4:
            break  # Stop iterating once 5 non-advertisement products are found

        if result.find("div", class_=["_1xHGtK _373qXS", "_4ddWXP"]):
            inner_products = result.find_all("div", class_=["_1xHGtK _373qXS", "_4ddWXP"])

            for inner_product in inner_products:
                ad_flag_inner = inner_product.find("div", class_=["_2I5qvP", "_4HTuuX"])

                if not ad_flag_inner:  # Check if the inner product is an advertisement
                    title_element_inner = inner_product.find("a", class_=["IRpwTa", "s1Q9rs"])
                    if not title_element_inner:
                        continue

                    title_inner = title_element_inner.text.strip()

                    price_element_inner = inner_product.find("div", {"class": "_30jeq3"})
                    if not price_element_inner:
                        continue
                    
                    price_list = []
                    price_inner = price_element_inner.text.strip()
                    price_list.append(price)

                    href_element_inner = inner_product.find("a", class_=["_2UzuFa", "s1Q9rs"])
                    if not href_element_inner:
                        continue

                    href_inner = urljoin("https://www.flipkart.com", href_element_inner["href"])

                    img_div_inner = inner_product.find('div', attrs={'class': 'CXW8mj'})
                    img_tag_inner = img_div_inner.find('img', attrs={'class': '_396cs4'})
                    if not img_tag_inner:
                        continue

                    img_url_inner = img_tag_inner.get('src')

                    rating_element_inner = inner_product.find("div", class_=["_3LWZlK _1rdVr6 _1BLPMq", "_3LWZlK _1BLPMq", "_3LWZlK _32lA32 _1BLPMq", "_3LWZlK"])
                    if rating_element_inner:
                        rating_inner = rating_element_inner.text.strip()
                    else:
                        continue

                    results.append({
                        'id': counter,
                        "platform": "Flipkart",
                        "title": title_inner,
                        "price": price_inner,
                        "href": href_inner,
                        "img_url": img_url_inner,
                        "rating": rating_inner
                    })

                    counter += 1

                    # Fetching offers from the URL
                    response_inner = requests.get(href_inner)
                    soup_inner = BeautifulSoup(response_inner.content, "html.parser")
                    offers = soup_inner.find_all("li", {"class": "_16eBzU col"})
                    for offer in offers:
                        results[-1].setdefault("offers", []).append(offer.text.strip())
                    reviews = soup_inner.find("span", {"class": "_2_R_DZ"})
                    if reviews:
                        reviews_text = reviews.text.strip()
                        reviews_number = reviews_text.split("&")[-1].strip()
                        results[-1]["reviews"] = reviews_number
                    cut_price_element = soup_inner.find("div", {"class": "_3I9_wc _2p6lqe"})
                    if cut_price_element:
                        cut_price = cut_price_element.text.strip()
                        results[-1]["cut_price"] = cut_price

                    #coupons
                    coupon_price_list = []
                    for prices in price_list:
                        without_special_symbol = prices.removeprefix("₹").replace(",", "")
                        price_int = int(without_special_symbol)
                        coupon_price_float = price_int * 0.05
                        coupon_price_list.append(str(round(coupon_price_float)))

                    coupon_price_singal_digit = []
                    for i in coupon_price_list:
                        for char in i:
                            coupon_price_singal_digit.append(char)
                    coupon_price_val = coupon_price(coupon_price_singal_digit)
                    
                    results[-1]['after 5%'] = coupon_price_list
                    results[-1]['coupon_val'] = coupon_price_val

        else:
            ad_flag = result.find("div", {"class": "_2tfzpE"})

            if not ad_flag:  # Check if the result is an advertisement
                title_element = result.find("div", {"class": "_4rR01T"})
                if not title_element:
                    continue

                title = title_element.text.strip()

                price_list = []
                price_element = result.find("div", {"class": "_30jeq3"})
                if not price_element:
                    continue

                price = price_element.text.strip()
                price_list.append(price)

                href_element = result.find("a", {"class": "_1fQZEK"})
                if not href_element:
                    continue

                href = urljoin("https://www.flipkart.com", href_element["href"])

                img_div = result.find('div', attrs={'class': 'CXW8mj'})
                img_tag = img_div.find('img', attrs={'class': '_396cs4'})
                if not img_tag:
                    continue

                img_url = img_tag.get('src')

                rating_element = result.find("div", class_=["_3LWZlK _1rdVr6 _1BLPMq", "_3LWZlK _1BLPMq", "_3LWZlK _32lA32 _1BLPMq", "_3LWZlK"])
                if rating_element:
                    rating = rating_element.text.strip()
                else:
                    continue

                results.append({
                    'id':counter,
                    "platform": "Flipkart",
                    "title": title,
                    "price": price,
                    "href": href,
                    "img_url": img_url,
                    "rating": rating
                })

                counter += 1

                # Fetching offers from the URL
                response_inner = requests.get(href)
                soup_inner = BeautifulSoup(response_inner.content, "html.parser")
                offers = soup_inner.find_all("li", {"class": "_16eBzU col"})
                for offer in offers:
                    results[-1].setdefault("offers", []).append(offer.text.strip())
                reviews = soup_inner.find("span", {"class": "_2_R_DZ"})
                if reviews:
                    reviews_text = reviews.text.strip()
                    reviews_number = reviews_text.split("&")[-1].strip()
                    results[-1]["reviews"] = reviews_number

                cut_price_element = soup_inner.find("div", {"class": "_3I9_wc _2p6lqe"})
                if cut_price_element:
                    cut_price = cut_price_element.text.strip()
                    results[-1]["cut_price"] = cut_price

                #coupons
                coupon_price_list = []
                for prices in price_list:
                    without_special_symbol = prices.removeprefix("₹").replace(",", "")
                    price_int = int(without_special_symbol)
                    coupon_price_float = price_int * 0.05
                    coupon_price_list.append(str(round(coupon_price_float)))
                print(coupon_price_list)

                coupon_price_singal_digit = []
                for i in coupon_price_list:
                    for char in i:
                        coupon_price_singal_digit.append(char)
                print(coupon_price_singal_digit)
                coupon_price_val = coupon_price(coupon_price_singal_digit)
                
                results[-1]['after 5%'] = coupon_price_list
                results[-1]['coupon_val'] = coupon_price_val
                
    print(results)
    return results

# scrape_flipkart_search()


def get_flipkart_reviews(p_link):
    url = p_link
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Find the total number of review pages
    # total_pages = int(soup.find("div", class_="_2MImiq _1Qnn1K").span.string.split()[-1])

    reviews = []

    # Iterate through all review pages
    for page in range(1, 5):
        print(f"Scraping page {page}...")
        page_url = url + f"&page={page}"
        response = requests.get(page_url)
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Find all review containers on the page
        review_containers = soup.find_all("div", class_="_1AtVbE")
        
        # Extract review text and rating from each container
        for container in review_containers:
            review_text_element = container.find("div", class_="t-ZTKy")
        
            # Find rating element with different class names
            rating_element = container.find("div", class_=["_3LWZlK _1rdVr6 _1BLPMq", "_3LWZlK _1BLPMq", "_3LWZlK _32lA32 _1BLPMq","_3LWZlK"])
        
            # Check if the required elements exist
            if review_text_element and rating_element:
                review_text = review_text_element.get_text(strip=True)
                rating = rating_element.text
                reviews.append(review_text)
            
        return reviews

def get_flipkart_first_product(search_term):
    search_term = search_term.lower()
    results = scrape_flipkart_search(search_term)
    # reviews_list = get_flipkart_reviews(results[0]['href'])
    # total_reviews = ""
    # for review in reviews_list:
    #     total_reviews += str(review)
    # print(total_reviews)
    # keyowrds = get_keywords(total_reviews)    
    to_return_dict = {}
    to_return_dict["Name"] = results[0]['title']
    to_return_dict["Link"] = results[0]['href']
    to_return_dict["Price"] = results[0]['price']
    to_return_dict["Image_link"] = results[0]['img_url']
    to_return_dict["No_of_reviews"] = results[0]['reviews']

    print(to_return_dict)
    return to_return_dict




app = FastAPI()


@app.get("/")
async def read_root():
    return {"message": "Welcome to the Product Comparator API!"}


@app.get("/get_products_merge/")
async def get_merges_reviews(product_name: str):
    product_name.lower()
    amazon_link = search_amazon(make_query(product_name.lower()))
    get_amazon_page_list(amazon_link, product_name)
    product_name = product_name.replace(" ", "_")
    product_name = sanitize_file_name(product_name)

    print(product_name)

    df = pd.read_csv(f"amazon_{product_name}_search.csv")
    j = 0
    sentiments = []
    for index, row in df.iterrows():
        if j < 1:
            p_name = row["Name"]
            p_link = row["Link"]
            # p_price = row['Price']
            # no_ratings = row['Number_of_ratings']
            p_name = p_name.replace(" ", "_")
            p_name = str(sanitize_file_name(p_name))
            p_review_page_link = get_review_page(p_link, product_name)
            get_review_elements(p_review_page_link, p_name)
            j += 1

    flipkart_first_product = get_flipkart_first_product(product_name.replace("_"," "))
    
    json_dict = return_json_dict_keywords(product_name)
    json_dict['Keywords'] = json_dict['Keywords'][:10]
    flipkart_first_product['Keywords'] = json_dict['Keywords'][10:]

    to_return_dict = json.dumps({"amazon": json_dict, "flipkart": flipkart_first_product})

    return to_return_dict



@app.get("/get_products_amazon/")
async def get_amazon_reviews(product_name: str):
    product_name.lower()
    amazon_link = search_amazon(make_query(product_name.lower()))
    get_amazon_page_list(amazon_link, product_name)
    product_name = product_name.replace(" ", "_")
    product_name = sanitize_file_name(product_name)

    print(product_name)

    df = pd.read_csv(f"amazon_{product_name}_search.csv")
    for index, row in df.iterrows():
        p_name = row["Name"]
        p_link = row["Link"]
        # p_price = row['Price']
        # no_ratings = row['Number_of_ratings']
        p_name = p_name.replace(" ", "_")
        p_name = str(sanitize_file_name(p_name))
        p_review_page_link = get_review_page(p_link, product_name)
        get_review_elements(p_review_page_link, p_name)

    json_dict = return_json_dict_sentiment(product_name)

    return json_dict
    # df = pd.read_csv(f"amazon_{product_name}_search.csv")
    # return_dict = {}
    # for index, row in df.iterrows():
    #     to_append_dict = {}
    #     # to_append_dict["Name"] = row["Name"]
    #     to_append_dict["Price"] = row["Price"]
    #     to_append_dict["Fastes_delivery_date"] = row["Fastes_delivery_date"]
    #     to_append_dict["Bought_last_month"] = row["Bought_last_month"]
    #     to_append_dict["Number_of_ratings"] = row["Number_of_ratings"]
    #     return_dict[f"{row['Name']}"] = to_append_dict
    # for name in df_og["Name"]:
    #     name = name.replace(" ", "_")
    #     df = pd.read_csv(f"amazon_{name}_reviews.csv")
    #     for review in df["review"]:


# get_amazon_reviews("samsung tv")


# get_review_page(
#     "https://www.amazon.in/Samsung-inches-Ready-UA32T4380AKXXL-Glossy/dp/B0B8YTGC23/ref=sr_1_3?dib=eyJ2IjoiMSJ9.YlMs65UEP2uAEeVG8gepex2P-0MSPO73Z5uGBwtN6HnGQ85hd8jpVE-YmRPalYx8UYNYI9Z9Uqyg0orYe178BOHbjlGHn5uwZ9oWcH_0ELAAX5l-X3efoJbDb7ZeiRHaE1lunfGCExczEzBdvWakLW01hsyJiHf8uEpLXSTZiaOLxdOEvqgDhvUAuuEkmWD_LelaEGx_xP4La1QQDJVm_KShWcGYY6BynJgcCcchH_Q.3o5jPtHM7zQXGBKj2AIGQT_W6jex3U6GT5fEDMo9W88&dib_tag=se&keywords=samsung+tv&qid=1709981100&sr=8-3"
# )

# get_amazon_reviews("samsung tv")

# df_og = pd.read_csv(f"amazon_samsung tv_search.csv")

# for name in df_og["Name"]:
#     name = name.replace(" ", "_")
#     df = pd.read_csv(f"amazon_{name}_reviews.csv")
#     for review in df["review"]:
#         print(review[:10])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
