import redis, json
import pandas as pd

from modules.redis_connector import RedisConnector
from modules.scraped_content import ScrapedContent


class AbacData(ScrapedContent):


    redis_key = 'abac_data'

    def get_last_page_index(this):
        return int(this.rd.get("LAST_PAGE_INDEX"))
    
    def set_last_page_index(this, val):
        this.rd.set("LAST_PAGE_INDEX",val)
        
    def get_base_url(this):
        return this.rd.get("BASE_URL")
    
    def get_most_recent_adjudication_url(this):
        try:
            last_index = this.rd.execute_command('JSON.ARRLEN',this.redis_key,'$')
        except redis.exceptions.ResponseError:
            url_at_index = ''
        else:
            last_record_position = last_index[0] -1
            url_at_index = this.rd.execute_command('JSON.GET' ,this.redis_key, f'[{last_record_position}].url')
        return url_at_index
    
    def set_abac_data(this,json_string):
        super().insert_new_data(json_string)
        #this.rd.execute_command('JSON.SET',this.redis_key,'$',json_string)

    def add_abac_data(this,json_string):
        this.rd.execute_command('JSON.ARRAPPEND',this.redis_key,'$',json_string)
    
    def get_abac_data(this):
        return super().get_content_list()
        #return this.rd.execute_command('JSON.GET',this.redis_key)
    
    def is_adjudication_page_in_data(this, url):
        #url_list = this.rd.execute_command('JSON.GET',this.redis_key,'$..url')
        #return url in url_list
        return super().is_adjudication_page_in_scraped_data(url)


    
