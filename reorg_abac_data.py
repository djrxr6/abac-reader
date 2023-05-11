#
#   The purpose of this program is to take the data which is output
#   from the abac_reader.py program, stored in redis under 'abac_data'
#   and utlize pandas to reorganise the data better for the frontent.
#       

import pandas as pd

from modules.redis_connector import RedisConnector
from modules.abac_data import AbacData

def main():
    redis_conector: RedisConnector = RedisConnector()
    abac_data: AbacData = AbacData(redis_conector) 
    data = abac_data.fetch_content_from_db()
    print(data)
    column_datatypes = {
        'title': 'string',
        'url': 'string',
        'decision': 'string',
        'brand': 'string',
        'company': 'string',
        'outcome': 'category',
        'nature' : 'string',
        'medium' : 'category'
    }
    df = pd.read_json(data, dtype=column_datatypes)
    df['id'] = df.reset_index().index
    df = df.astype({col: bool for col in df.columns[11:32]})
    print(df.info())

    print(pd.unique(df['outcome']))
    print(pd.unique(df['medium']))

    #Could store additional dataframes in redis
    #Weekly/Monthly counts of medium and code secrions

if __name__ == "__main__":
    main()