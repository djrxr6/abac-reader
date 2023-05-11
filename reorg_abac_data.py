#
#   The purpose of this program is to take the data which is output
#   from the abac_reader.py program, stored in redis under 'abac_data'
#   and utlize pandas to reorganise the data better for the frontent.
#       

import pandas as pd
import redis


from modules.redis_connector import RedisConnector
from modules.abac_data import AbacData

def main():
    redis_conector: RedisConnector = RedisConnector()
    abac_data: AbacData = AbacData(redis_conector) 
    data = abac_data.fetch_content_from_db()