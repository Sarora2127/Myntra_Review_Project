# src > scrapper > scrape.py
from flask import request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.exception import CustomException
from bs4 import BeautifulSoup as bs
import pandas as pd
import os, sys
import time
from selenium.webdriver.chrome.options import Options
from urllib.parse import quote
import re

class ScrapeReviews : # to scrape the reviews
    def __init__ (self, product_name:str, no_of_products:int):
        options = Options()
        # options.add_argument("--no-sandbox")
        # options.add_argument("--disable-dev-shm-usage")
        # options.add_argument('--headless')

        # Start a new Chrome Browser Session
        self.driver = webdriver.Chrome(options=options)
        self.product_name = product_name
        self.no_of_products = no_of_products
    
    def scrape_product_urls(self, product_name):
        try:
            search_string = product_name.replace(" ","-")
            # no_of_products = int(self.request.form['prod_no'])
            encoded_query = quote(search_string) # url encoding %20
            # Navigate to the URL
            self.driver.get(
                f"https://www.myntra.com/{search_string}?rawQuery={encoded_query}"
            )
            myntra_text = self.driver.page_source
            myntra_html = bs(myntra_text, "html.parser")
            pclass = myntra_html.findAll("ul",{"class":"results-base"})
            product_urls=[]
            for i in pclass:
                href = i.find_all("a",href=True)
                for product_no in range(len(href)):
                    t = href[product_no]["href"]
                    product_urls.append(t)
            return product_urls
        except Exception as e:
            raise CustomException(e,sys)
        
    def extract_reviews(self,product_link):
        try:
            productLink = "https://www.myntra.com/"+product_link
            self.driver.get(productLink)
            prodRes = self.driver.page_source
            prodRes_html = bs(prodRes, "html.parser")
            title_h = prodRes_html.findAll("title")
            self.product_title = title_h[0].text
            overallRating = prodRes_html.findAll("div",{"class":"index-overallRating"})
            for i in overallRating:
                self.product_rating_value = i.find("div").text
            price = prodRes_html.findAll("span",{"class":"pdp-price"})
            for i in price:
                self.product_price = i.text
            product_reviews = prodRes_html.find(
                "a",{"class":"detailed-reviews-allReviews"}
            )
            # === 1. Extract Rating Count ===
            rating_count_div = prodRes_html.find("div", {"class": "index-ratingsCount"})
            if rating_count_div:
                # rating_text = rating_count_div.get_text(strip=True)
                rating_text = rating_count_div.get_text(separator=" ", strip=True)
                match = re.search(r"[\d.]+[kKmM]?", rating_text)
                if match:
                    raw_rating = match.group()
                    if 'k' in raw_rating.lower():
                        self.rating_count = int(float(raw_rating.lower().replace('k', '')) * 1000)
                    elif 'm' in raw_rating.lower():
                        self.rating_count = int(float(raw_rating.lower().replace('m', '')) * 1000000)
                    else:
                        self.rating_count = int(raw_rating)
            if not product_reviews:
                return None
            return product_reviews
        except Exception as e:
            raise CustomException(e,sys)

    def extract_products(self, product_reviews: list):
        try:
            t2 = product_reviews["href"]
            Review_link = "https://www.myntra.com" + t2
            self.driver.get(Review_link)
            self.scroll_to_load_reviews()
            # Re-fetch product page content after reviews have loaded
            product_page = self.driver.page_source
            proRes_html = bs(product_page, "html.parser")
            '''
            # === 2. Extract Product Specifications ===
            product_details = {}
            descriptors_container = proRes_html.find('div', class_='pdp-productDescriptorsContainer')
            if descriptors_container:
                titles = descriptors_container.find_all('h4', class_='pdp-product-description-title')
                contents = descriptors_container.find_all('p', class_='pdp-product-description-content')
                for title, content in zip(titles, contents):
                    section_name = title.get_text(strip=True)
                    ul = content.find('ul')
                    if ul:
                        items = [li.get_text(strip=True) for li in ul.find_all('li')]
                    else:
                        items = content.get_text(separator="\n").strip().split('\n')
                    product_details[section_name] = items

            # Table-based specifications
            specs_container = proRes_html.find('div', class_='index-tableContainer')
            if specs_container:
                rows = specs_container.find_all('div', class_='index-row')
                for row in rows:
                    key_div = row.find('div', class_='index-rowKey')
                    value_div = row.find('div', class_='index-rowValue')
                    if key_div and value_div:
                        key = key_div.get_text(strip=True)
                        value = value_div.get_text(strip=True)
                        product_details[key] = value'''

            # Load all reviews
            review_page = self.driver.page_source
            review_html = bs(review_page, "html.parser")
            review = review_html.findAll("div", {"class": "detailed-reviews-userReviewsContainer"})
            reviews = []

            for i in review:
                user_rating = i.findAll("div", {"class": "user-review-main user-review-showRating"})
                user_comment = i.findAll("div", {"class": "user-review-reviewTextWrapper"})
                user_name = i.findAll("div", {"class": "user-review-left"})

                for j in range(len(user_rating)):
                    try:
                        rating = user_rating[j].find("span", class_="user-review-starRating").get_text().strip()
                    except:
                        rating = "No rating Given"
                    try:
                        comment = user_comment[j].text
                    except:
                        comment = "No comment Given"
                    try:
                        name = user_name[j].find("span").text
                    except:
                        name = "No name Given"
                    try:
                        date = user_name[j].find_all("span")[1].text
                    except:
                        date = "No Date Given"

                    mydict = {
                        "Product Name": self.product_title,
                        "Over_All_Rating": self.product_rating_value,
                        "Price": self.product_price,
                        "Date": date,
                        "Rating": rating,
                        "Name": name,
                        "Comment": comment,
                        "Rating_Count": self.rating_count
                    }

                    '''# Flatten any list values in product_details
                    for k, v in product_details.items():
                        if isinstance(v, list):
                            mydict[k] = ", ".join(v)
                        else:
                            mydict[k] = v'''

                    reviews.append(mydict)

            review_data = pd.DataFrame(
                reviews,
                columns=[
                    "Product Name",
                    "Over_All_Rating",
                    "Price",
                    "Date",
                    "Rating",
                    "Name",
                    "Comment",
                    "Rating_Count"
                ]  #+ list(product_details.keys())
            )
            return review_data

        except Exception as e:
            raise CustomException(e, sys)

    
    def scroll_to_load_reviews(self):
        # change the window size to load more data
        self.driver.set_window_size(1920,1080)
        # Get the initial height of the page
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        # Scroll in smaller increments, waiting between scrolls 
        while True:
            # Scroll down by a small amount
            self.driver.execute_script("window.scrollBy(0,1000);")
            time.sleep(3) 
            # Calculate the new Height after scrolling
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            # Break the loop if no new content is loaded after scrolling
            if new_height == last_height:
                break

            # Update the last height for the next iteration
            last_height = new_height
    
    '''def extract_products(self, product_reviews: list):
        try:
            t2 = product_reviews["href"]
            Review_link = "https://www.myntra.com"+t2
            self.driver.get(Review_link)
            self.scroll_to_load_reviews()
            review_page = self.driver.page_source
            review_html = bs(review_page, "html.parser")
            review = review_html.findAll("div",{"class":"detailed-reviews-userReviewsContainer"})
            for i in review:
                user_rating = i.findAll(
                    "div",{"class":"user-review-main user-review-showRating"}
                )
                user_comment = i.findAll(
                    "div", {"class": "user-review-reviewTextWrapper"}
                )
                user_name = i.findAll("div", {"class": "user-review-left"})
            reviews = []
            for i in range(len(user_rating)):
                try:
                    rating = (
                        user_rating[i].find("span",class_="user-review-starRating").get_text().strip()
                    )
                except:
                    rating = "No rating Given"
                try:
                    comment = user_comment[i].text
                except:
                    comment="No comment Given"
                try:
                    name = user_name[i].find("span").text
                except:
                    name="No name Given"
                try:
                    date = user_name[i].find_all("span")[1].text
                except:
                    date = "No Date Given"
                
                mydict = {
                    "Product Name":self.product_title,
                    "Over_All_Rating":self.product_rating_value,
                    "Price":self.product_price,
                    "Date":date,
                    "Rating":rating,
                    "Name":name,
                    "Comment":comment,
                }
                reviews.append(mydict)
            review_data = pd.DataFrame(
                reviews,
                columns=[
                    "Product Name",
                    "Over_All_Rating",
                    "Price",
                    "Date",
                    "Rating",
                    "Name",
                    "Comment"
                ],
            )
            return review_data
        except Exception as e:
            raise CustomException(e, sys)'''
    
    def skip_products(self, search_string, no_of_products, skip_index):
        product_urls:list = self.scrape_product_urls(search_string, no_of_products+1)
        product_urls.pop(skip_index)
        return product_urls

    def get_review_data(self) -> pd.DataFrame:
        try:
            # search string = self.request.form["content"].replace(" ","-")
            # no_of_products = int(self.request.form["prod_no"])
            product_urls = self.scrape_product_urls(product_name = self.product_name)
            if not product_urls:
                raise CustomException("No products found for this keyword!", sys)
            product_details = []
            review_len = 0
            # Stop loop if:
            # - We reach the desired number of reviews
            # - OR there are no more product URLs to check
            while review_len<self.no_of_products and review_len < len(product_urls):
                product_url = product_urls[review_len]
                review = self.extract_reviews(product_url)
                if review:
                    product_detail = self.extract_products(review)
                    product_details.append(product_detail)
                    
                else:
                    print(f"No reviews found for product at index {review_len}")
                review_len +=1
            self.driver.quit()
            if not product_details:
                raise CustomException("No review data could be extracted from any product.", sys)
            data = pd.concat(product_details, axis=0)
            data.to_csv("data.csv",index=False)
            return data
            # columns = data.columns
            # values = [[data.loc[i,col] for col in data.columns] for i in range(len(data))]
            # return columns, values
        except Exception as e:
            raise CustomException(e,sys)
