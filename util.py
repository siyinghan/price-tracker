"""
Get prices from the website and save them to a CSV file.
"""
import csv
import logging
import sys
from datetime import datetime

import requests
from bs4 import BeautifulSoup

tv = {"SONY": "https://www.coolblue.nl/en/product/906254/sony-bravia-oled-xr-77a80k-2022.html",
      "LG": "https://www.coolblue.nl/en/product/903398/lg-oled77c24la-2022.html"}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("price_tracker.log"),
        logging.StreamHandler(stream=sys.stdout)
    ]
)


def price_tracker():
    """
    Get the price and write it in price_tracker.csv.
    """
    date = datetime.now().strftime("%Y-%m-%d")
    for brand, url in tv.items():
        data = [date, brand, get_price(url)]
        logging.info(data)
        with open("price_tracker.csv", "a") as file:
            writer = csv.writer(file)
            writer.writerow(data)


def get_price(url):
    """
    Get the price from the Coolblue page.
    :param url: str
    :return: str
    """
    price = parse(craw(url))
    logging.debug(f"Get current price: {price}")
    return price


def craw(url):
    """
    Get the page text of the URL.
    :param url: str
    :return: str
    """
    headers = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/109.0.0.0 Safari/537.36"}
    response = requests.get(url, headers=headers)
    logging.info(f"Get response from {url}")
    return response.text


def parse(html):
    """
    Get the price of the page text.
    :param html: str
    :return: str
    """
    find_class = "sales-price__current"
    soup = BeautifulSoup(html, "html.parser")
    element = soup.find("strong", class_=find_class)
    logging.debug(f"Get element of class '{find_class}'")
    return element.get_text().split(",")[0]
