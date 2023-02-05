"""
Get prices from the website and save them to a CSV file.
"""
import logging
import sys
from datetime import datetime

import requests
import yaml
from bs4 import BeautifulSoup
from pathlib import Path

from mysql.connector import connection

current_path = Path(__file__).parent.absolute()

logging.basicConfig(
    level=logging.INFO,
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
    logging.debug(f"Get response from {url}")
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


class PriceTracker:
    def __init__(self, location):
        self.location = location
        self.cnx = None
        self.cur = None
        self.last_index = None
        self.item_url_info = dict()
        self.item_name_list = list()
        self.connect_to_db()

    # def price_tracker():
    #     """
    #     Get the price and write it in price_tracker.csv.
    #     """
    #     # add header if the file is not exist
    #     get_yesterday_price()
    # 
    #     if not path.exists("price_tracker.csv"):
    #         with open(f"{current_path}/price_tracker.csv", "a") as file:
    #             writer = csv.writer(file)
    #             writer.writerow(["Date", "Brand", "Price"])
    # 
    #     date = datetime.now().strftime("%Y-%m-%d")
    #     for brand, url in tv.items():
    #         data = [date, brand, get_current_price(url)]
    #         logging.info(data)
    #         with open(f"{current_path}/price_tracker.csv", "a") as file:
    #             writer = csv.writer(file)
    #             writer.writerow(data)

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
        Get the price of yesterday from the database.
        """
        price_list = list()
        # get items name
        self.cur.execute("SHOW COLUMNS FROM test")
        columns = self.cur.fetchall()
        for index in range(len(columns)):
            if index > 1:
                self.item_name_list.append(columns[index][0])
        # get yesterday price
        self.cur.execute("SELECT * FROM test ORDER BY id DESC LIMIT 1")
        data = self.cur.fetchall()[0]
        date = data[1]
        for index in range(len(data)):
            if index == 0:
                self.last_index = index
            elif index > 1:
                price_list.append(data[index])
        logging.info(f"{date} {dict(zip(self.item_name_list, price_list))}")

    def create_dict_to_db(self):
        price_dict = {}
        date = datetime.now().strftime("%Y-%m-%d")
        self.get_item_and_url()
        for item, url in self.item_url_info.items():
            price_dict[item] = parse(craw(url))
        logging.info(f"{date} {price_dict}")
        price_dict["date"] = date
        columns = "`, `".join(price_dict.keys())
        columns = f"`{columns}`"
        values = ", ".join(price_dict.values())
        self.cur.execute(f"INSERT INTO test ({columns}) VALUES ({values})")
        self.cnx.commit()

    def __del__(self):
        self.cnx.close()
        self.cur.close()
