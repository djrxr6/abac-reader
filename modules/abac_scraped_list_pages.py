import json
import pandas as pd
#from modules.redis_connector import RedisConnector
from modules.scraped_content import ScrapedContent


class AbacScrapedListPages(ScrapedContent):
    redis_key = 'abac_scraped_list_pages'
