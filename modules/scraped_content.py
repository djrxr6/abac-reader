

import json
import pandas as pd
from modules.redis_connector import RedisConnector


class ScrapedContent:


    rd = ''
    redis_key = ''

    def __init__(this, redis_connector: RedisConnector):
        this.rd = redis_connector.get_redis_object()
        print(this.redis_key)

    def get_content_list(this):
        return this.rd.execute_command('JSON.GET',this.redis_key)    

    def destroy_content(this):
        this.rd.execute_command('JSON.DEL', this.redis_key)

    def drop_duplicates(this):
        json_string = this.rd.execute_command('JSON.GET',this.redis_key)
        df = pd.read_json(json_string, convert_dates=False)
        print(df)
        df = df.drop_duplicates()
        print(df)

        df = df.sort_values(by=['date'])

        #this.destroy_content()

        #this.insert_scraped_content()

        json_string = df.to_json(orient="records")
        this.insert_new_data(json_string)
    
    def sort_data(this,sort_columns:list):
        json_string = this.rd.execute_command('JSON.GET',this.redis_key)
        df = pd.read_json(json_string, convert_dates=False)
        print(df)
        df = df.drop_duplicates()
        print(df)

        df = df.sort_values(by=sort_columns)

        #this.destroy_content()

        #this.insert_scraped_content()

        json_string = df.to_json(orient="records")
        this.insert_new_data(json_string)
    
    def insert_new_data(this,json_string):
        this.rd.execute_command('JSON.SET',this.redis_key,'$',json_string)

    def load_audjdication_page_content(this, url):
        json_string = this.rd.execute_command('JSON.GET',this.redis_key)
        df = pd.read_json(json_string)
        df = df.loc[df['url']==url,['scraped_content']]
        return df.to_string(index=False)

    def insert_scraped_content(this ,url:str ,content: str):
        json_string = json.dumps({"url": url ,"scraped_content": content })
        this.rd.execute_command('JSON.ARRAPPEND',this.redis_key,'$',json_string)

    def is_adjudication_page_in_scraped_data(this, url):
        url_list = this.rd.execute_command('JSON.GET',this.redis_key,'$..url')
        url_list = 'no data' if url_list == None else url_list
        return url in url_list


