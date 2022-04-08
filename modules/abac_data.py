import redis, json
import pandas as pd

from modules.redis_connector import RedisConnector
from modules.scraped_content import ScrapedContent


class AbacData(ScrapedContent):

    redis_key = 'abac_data'
   
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

#    def add_abac_data(this,json_string):
#        this.rd.execute_command('JSON.ARRAPPEND',this.redis_key,'$',json_string)
    
    def get_abac_data(this):
        return super().get_content_list()
    
    def is_adjudication_page_in_data(this, url):
        return super().is_adjudication_page_in_scraped_data(url)


    
