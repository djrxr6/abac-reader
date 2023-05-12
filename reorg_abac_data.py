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
    
    set_mediums_db(df)
    set_code_section_db(df)

    print(pd.unique(df['outcome']))

    json_string: str = df.to_json(orient='records')
    redis_conector.get_redis_object().execute_command('JSON.SET', 'abac_data:deep_object', "$",json_string)
    #Could store additional dataframes in redis
    #Weekly/Monthly counts of medium and code secrions


def set_mediums_db(df):
    set_items_to_db_from_df_column(df,'medium')

def set_code_section_db(df) -> None:
    set_items_to_db_from_df_column(df,'outcome')

def set_items_to_db_from_df_column(df: pd.DataFrame, column: str) -> None:
    items: list = df[column].str.split(',', expand=True).stack().reset_index(level=1)
    new_df = pd.DataFrame(set(items[0]))
    new_df = new_df.reset_index()
    new_df.columns = ['id','label']
    json_string = new_df.to_json(orient='records')
    
    redis_conector: RedisConnector = RedisConnector()
    redis_conector.get_redis_object().execute_command('JSON.SET', f"abac_data:{column}", "$",json_string)


if __name__ == "__main__":
    main()
