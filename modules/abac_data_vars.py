import json
import logging

from modules.redis_connector import RedisConnector
from modules.scraped_content import ScrapedContent


class AbacDataVars(ScrapedContent):

    last_page_index: int = ""
    base_url: str = ""

    redis_key: str = "abac_data:vars"

    def __init__(this, redis_connector: RedisConnector):
        super().__init__(redis_connector)

        json_object = json.loads(super().fetch_content_from_db())

        this.base_url = json_object["base_url"]
        this.last_page_index = json_object["last_page_index"]

    def get_last_page_index(this) -> int:
        return this.last_page_index

    def get_base_url(this) -> str:
        return this.base_url

    def set_last_page_index(this, last_page_index: int) -> None:
        this.last_page_index = last_page_index

    def update_db(this) -> None:
        json_string = json.dumps(
            {"base_url": this.base_url, "last_page_index": this.last_page_index}
        )
        logging.debug(f"Key: {this.redis_key}")
        logging.debug(f"JSON string: {json_string}")
        this.rd.execute_command("JSON.SET", this.redis_key, "$", json_string)
