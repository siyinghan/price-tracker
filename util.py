"""
Get prices from the website and save them to the database.
"""
import logging
import sys
import time

import requests
import yaml
from bs4 import BeautifulSoup
from pathlib import Path

from mysql.connector import connection

current_path = Path(__file__).parent.absolute()

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"{current_path}/price_tracker.log"),
        logging.StreamHandler(stream=sys.stdout)
    ]
)


def craw(url):
    """
    Get the page text of the URL.
    :param url: str
    :return: str
    """
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/109.0.0.0 Safari/537.36"}
    response = requests.get(url, headers=headers)
    logging.info(f"Get response from {url}")
    return response.text


def parse1(html):
    """
    Get the price of the page text.
    :param html: str
    :return: str
    """
    find_class = "sales-price__current"
    soup = BeautifulSoup(html, "html.parser")
    element = soup.findAll("strong", class_=find_class)
    logging.debug(f"Get element of class '{find_class}'")
    return element[0].get_text().split(",")[0]


def parse2(html):
    """
    Get the price of the page text.
    :param html: str
    :return: str
    """
    find_class = "sales-price__current"
    soup = BeautifulSoup(html, "html.parser")
    element = soup.findAll("strong", class_=find_class)
    logging.debug(f"Get element of class '{find_class}'")
    return element[1].get_text().split(",")[0]


class PriceTracker:
    """
    Get prices from the website and save them to the database.
    """

    def __init__(self, location):
        self.location = location
        self.cnx = None
        self.cur = None
        self.last_index = None
        self.yesterday_price = dict()
        self.item_url_info = dict()
        self.item_name_list = list()
        self.connect_to_db()

    def run(self):
        """
        Run PriceTracker.
        """
        # add header if the file is not exist
        self.get_yesterday_price()
        self.get_current_price()

    def read_db_conf(self):
        """
        Read the database configuration file.
        :return: dict()
        """
        with open(f"{current_path}/conf/mysql_{self.location}.yaml") as file:
            mysql_config = yaml.safe_load(file)
        logging.info(f"Read mysql_{self.location}.yaml success")
        return mysql_config

    def connect_to_db(self):
        """
        Connect to the database.
        """
        self.cnx = connection.MySQLConnection(**self.read_db_conf())
        self.cur = self.cnx.cursor()
        logging.info("Connect to the database success")

    def get_item_and_url(self):
        """
        Connection to the database and retrieve item info.
        """
        self.cur.execute("SELECT * FROM item_info")
        data = self.cur.fetchall()
        for item in data:
            self.item_url_info[item[1]] = item[2]
        logging.info(f"Get item url info")

    def get_yesterday_price(self):
        """
        Get the prices of yesterday from the database.
        """
        price_list = list()
        # get items name
        self.cur.execute("SHOW COLUMNS FROM price")
        columns = self.cur.fetchall()
        for index in range(len(columns)):
            if index > 1:
                self.item_name_list.append(columns[index][0])
        # get yesterday price
        self.cur.execute("SELECT * FROM price ORDER BY id DESC LIMIT 1")
        try:
            data = self.cur.fetchall()[0]
            for index in range(len(data)):
                if index == 0:
                    self.last_index = index
                elif index > 1:
                    price_list.append(data[index])
            self.yesterday_price = dict(zip(self.item_name_list, price_list))
            logging.debug("Get the prices of yesterday")
        except IndexError as _:
            logging.error("No prices of yesterday")

    def get_current_price(self):
        """
        Get the prices from the pages and save them to the database.
        """
        price_dict = {}
        date = time.strftime("%Y-%m-%d")
        self.get_item_and_url()
        for item, url in self.item_url_info.items():
            if item != "Nespresso-SNE500BKS":
                price_dict[item] = parse1(craw(url))
            else:
                price_dict[item] = parse2(craw(url))
        logging.debug("Get the prices of today")
        logging.info(f"{date} {price_dict}")
        print(f"{date} {price_dict}")
        price_dict["date"] = date
        columns = "`, `".join(price_dict.keys())
        columns = f"`{columns}`"
        values = "', '".join(price_dict.values())
        values = f"'{values}'"
        self.cur.execute(f"INSERT INTO price ({columns}) VALUES ({values})")
        self.cnx.commit()
        logging.info(f"{date} {self.yesterday_price}")
        print(f"{date} {self.yesterday_price}")

    def __del__(self):
        self.cnx.close()
        self.cur.close()
