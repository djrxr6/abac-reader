import json
import pandas as pd
#from modules.redis_connector import RedisConnector
from modules.scraped_content import ScrapedContent


class AbacScrapedContent(ScrapedContent):

    
    redis_key = 'abac_scraped_content'
