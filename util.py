"""
Get prices from the website and save them to a CSV file.
"""
import csv
import logging
import sys
from datetime import datetime
from os import path

import requests
from bs4 import BeautifulSoup
from pathlib import Path

tv = {"SONY": "https://www.coolblue.nl/en/product/906254/sony-bravia-oled-xr-77a80k-2022.html",
      "LG": "https://www.coolblue.nl/en/product/903398/lg-oled77c24la-2022.html"}

current_path = Path(__file__).parent.absolute()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"{current_path}price_tracker.log"),
        logging.StreamHandler(stream=sys.stdout)
    ]
)


def price_tracker():
    """
    Get the price and write it in price_tracker.csv.
    """
    # add header if the file is not exist
    get_yesterday_price()

    if not path.exists("price_tracker.csv"):
        with open(f"{current_path}/price_tracker.csv", "a") as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Brand", "Price"])

    date = datetime.now().strftime("%Y-%m-%d")
    for brand, url in tv.items():
        data = [date, brand, get_current_price(url)]
        logging.info(data)
        with open(f"{current_path}/price_tracker.csv", "a") as file:
            writer = csv.writer(file)
            writer.writerow(data)


def get_current_price(url):
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


def get_yesterday_price():
    """
    Get the price of yesterday from price_tracker.csv.
    """
    if path.exists(f"{current_path}/price_tracker.csv"):
        with open(f"{current_path}/price_tracker.csv", "r") as file:
            lines = file.readlines()
        logging.info(lines[-2].split("\n")[0].split(","))
        logging.info(lines[-1].split("\n")[0].split(","))
