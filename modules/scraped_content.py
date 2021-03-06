import json
import logging

import pandas as pd

from modules.redis_connector import RedisConnector


class ScrapedContent:

    rd: RedisConnector = ""
    redis_key: str = ""

    def __init__(this, redis_connector: RedisConnector) -> None:
        this.rd = redis_connector.get_redis_object()
        print(this.redis_key)

    def set_redis_key(this, redis_key: str) -> None:
        this.redis_key = redis_key

    def fetch_content_from_db(this) -> str:
        return this.rd.execute_command("JSON.GET", this.redis_key)

    def get_content_list(this) -> str:
        return this.fetch_content_from_db()

    def destroy_content(this) -> None:
        this.rd.execute_command("JSON.DEL", this.redis_key)

    # def drop_duplicates(this):
    #     json_string = this.rd.execute_command('JSON.GET',this.redis_key)
    #     df = pd.read_json(json_string, convert_dates=False)
    #     df = df.drop_duplicates()
    #     df = df.sort_values(by=['date'])
    #     json_string = df.to_json(orient="records")
    #     this.insert_new_data(json_string)

    # def sort_data(this, sort_columns:list) -> None:
    #     json_string = this.rd.execute_command('JSON.GET',this.redis_key)
    #     df = pd.read_json(json_string, convert_dates=False)
    #     df = df.drop_duplicates()
    #     df = df.sort_values(by=sort_columns)
    #     json_string = df.to_json(orient="records")
    #     this.insert_new_data(json_string)

    def insert_new_data(this, json_string: str) -> None:
        this.rd.execute_command("JSON.SET", this.redis_key, "$", json_string)

    def fetch_audjdication_page_content(this, url: str) -> str:
        json_string = this.rd.execute_command("JSON.GET", this.redis_key)
        df = pd.read_json(json_string)
        df = df.loc[df["url"] == url, ["scraped_content"]]
        return df.to_string(index=False)

    def insert_scraped_content(this, url: str, content: str) -> None:
        logging.debug(f"inserting data to {this.redis_key}.")
        logging.debug(f"{url}")
        json_string = json.dumps({"url": url, "scraped_content": content})
        this.rd.execute_command("JSON.ARRAPPEND", this.redis_key, "$", json_string)

    def is_adjudication_page_in_scraped_data(this, url: str) -> bool:
        url_list = this.rd.execute_command("JSON.GET", this.redis_key, "$..url")
        url_list = "no data" if url_list == None else url_list
        return url in url_list
