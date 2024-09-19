import json
import logging

import pandas as pd

from modules.redis_connector import RedisConnector
from icecream import ic


class ScrapedContent:

    rd: RedisConnector = ""
    redis_key: str = ""

    def __init__(self, redis_connector: RedisConnector) -> None:
        self.rd = redis_connector.get_redis_object()
        print(self.redis_key)

    def set_redis_key(self, redis_key: str) -> None:
        self.redis_key = redis_key

    def fetch_content_from_db(self) -> str:
        return self.rd.execute_command("JSON.GET", self.redis_key)

    def get_content_list(self) -> str:
        return self.fetch_content_from_db()

    def get_record_count(self) -> int:
        return self.rd.execute_command("JSON.ARRLEN", self.redis_key)

    def destroy_content(self) -> None:
        self.rd.execute_command("JSON.DEL", self.redis_key)

    # def drop_duplicates(self):
    #     json_string = self.rd.execute_command('JSON.GET',self.redis_key)
    #     df = pd.read_json(json_string, convert_dates=False)
    #     df = df.drop_duplicates()
    #     df = df.sort_values(by=['date'])
    #     json_string = df.to_json(orient="records")
    #     self.insert_new_data(json_string)

    # def sort_data(self, sort_columns:list) -> None:
    #     json_string = self.rd.execute_command('JSON.GET',self.redis_key)
    #     df = pd.read_json(json_string, convert_dates=False)
    #     df = df.drop_duplicates()
    #     df = df.sort_values(by=sort_columns)
    #     json_string = df.to_json(orient="records")
    #     self.insert_new_data(json_string)

    def insert_new_data(self, dict: dict) -> None:
        json_string = json.dumps(dict)
        self.rd.execute_command("JSON.SET", self.redis_key, "$", json_string)


    def fetch_audjdication_page_content(self, url: str) -> str:
        json_string = self.rd.execute_command("JSON.GET", self.redis_key)
        data_dict = json.loads(json_string)
        df = pd.DataFrame(data_dict)

        #df = pd.read_json(json_string)
        df = df.loc[df["url"] == url, ["scraped_content"]]
        return df.to_string(index=False)

    def insert_scraped_content(self, url: str, content: str) -> None:
        logging.debug(f"inserting data to {self.redis_key}.")
        logging.debug(f"{url}")
        json_string = json.dumps({"url": url, "scraped_content": content})
        self.rd.execute_command("JSON.ARRAPPEND", self.redis_key, "$", json_string)

    def is_adjudication_page_in_scraped_data(self, url: str) -> bool:
        url_list = self.rd.execute_command("JSON.GET", self.redis_key, "$..url")
        url_list = "no data" if url_list == None else url_list
        return url in url_list
