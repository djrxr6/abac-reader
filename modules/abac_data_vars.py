import redis, json
import pandas as pd

from modules.redis_connector import RedisConnector
from modules.scraped_content import ScrapedContent

class AbacDataVars(ScrapedContent):

    last_page_index: int = ''
    base_url: str = ''

    redis_key: str = 'abac_data:vars'

    def __init__(this, redis_connector: RedisConnector):
        super().__init__(redis_connector)

        json_object = json.loads(super().db_get_json_content())

        this.base_url = json_object["base_url"]
        this.last_page_index = json_object["last_page_index"]

    def get_last_page_index(this):
        return this.last_page_index
    
    def get_base_url(this):
        return this.base_url

    def set_last_page_index(this, last_page_index):
        this.last_page_index = last_page_index

    def update_db(this):
        json_string = json.dumps({"base_url": this.base_url ,"last_page_index": this.last_page_index })
        this.rd.execute_command('JSON.SET', this.redis_key, json_string)
        

    
