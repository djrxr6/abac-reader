import logging
from os import sep
from posixpath import split

import pandas as pd
import requests
from bs4 import BeautifulSoup, ResultSet

import modules.abac_data_vars as advars
from modules.abac_data import AbacData
from modules.abac_scraped_content import AbacScrapedContent
from modules.abac_scraped_list_pages import AbacScrapedListPages
from modules.redis_connector import RedisConnector
from modules.ABACScraper import ABACScraper

from icecream import ic


logging.basicConfig(level=logging.DEBUG)
logging.debug("abac-reader started")

pd.set_option('display.max_columns', None)
#redis_connector = RedisConnector()

db_data = AbacData(RedisConnector())

ASC = AbacScrapedContent(RedisConnector())
ASLP = AbacScrapedListPages(RedisConnector())
ADVARS = advars.AbacDataVars(RedisConnector())

ABACScraper = ABACScraper(ASC, ASLP, ADVARS, db_data)

def main() -> None:

    json_existing_abac_data = db_data.get_abac_data()

    if json_existing_abac_data is None:
        df_existing_abac_data = pd.DataFrame()
    else:
        df_existing_abac_data = pd.read_json(db_data.get_abac_data(), convert_dates=False)

    if ABACScraper.is_new_adjudications():

        logging.debug("New adjudications have been found.")

        # Destroy the cached index pages data
        ASLP.insert_new_data("[]")

        abac_adjudications_pages_urls = []

        for page_index in range(1, get_final_page_index()):
        #for page_index in range(84, 86): #use this to debug with a smaller subset of data.
            abac_adjudications_pages_urls.extend(
                ABACScraper.get_urls_from_abac_page(f"{ADVARS.get_base_url()}{page_index}")
            )
        ic(abac_adjudications_pages_urls)
        df_new_abac_adjudications = pd.DataFrame(abac_adjudications_pages_urls)

        df_new_abac_adjudications = df_new_abac_adjudications.fillna("")

        # Add new columns based on primary data.
        df_new_abac_adjudications = add_new_columns(df_new_abac_adjudications)

        # Concatenate the existing data with the new data
        df_updated_abac_adjudications = pd.concat(
            [df_existing_abac_data, df_new_abac_adjudications], ignore_index=True
        )
        # Add combined new and existing data to the database.
        db_data.set_abac_data(df_updated_abac_adjudications.to_json(orient="records"))

        df_updated_abac_adjudications.to_csv("abac-adjudications-full.csv", index=False)

    else:
        logging.debug("There are no new adjudications.")

    return

def res_upd_helper(target: str, search: str) -> int:
    if target is None:
        var = 0
    else:
        var = 1 if (search in target) else 0
        var = 0 if ("Part" in target) else var
    return var

def add_new_columns(df) -> pd.DataFrame:
 
    df = apply_code_version_column_updates(df)
    df = apply_medium_column_updates(df)
    df = apply_code_section_column_updates(df)

    date = pd.DatetimeIndex(df["date"])

    df["year"] = date.year
    df["month"] = date.month
    df["day"] = date.day

    return df

def update_code_version(row, column_name, version_value):
# Function to update code version and set the 'code_section' column
    if column_name in row and isinstance(row[column_name], str) and row[column_name] != "":
        # Only update if the new version is higher than the current version
        if row["code_version"] < version_value:
            row["code_version"] = version_value
            row["code_section"] = row[column_name]  # Copy the value to 'code_section'
    return row

def apply_code_version_column_updates(df):
    # Apply the function row-wise to update 'code_version' and 'code_section'

    df["code_version"] = 0
    df["code_section"] = ""
        
    # List of columns and corresponding version values
    columns_with_versions = [
        ("Current Code section - from 1 August 2023", 3),
        ("Current Code sections - from 1 August 2023", 3),
        ("New Code section - post 1 July 2014", 2),
        ("New Code sections - post 1 July 2014", 2),
        ("Old Code section - pre 1 July 2014", 1),
        ("Old Code sections - pre 1 July 2014", 1),
    ]
    for column_name, version_value in columns_with_versions:
        if column_name in df.columns:
            # Apply row-wise operation using apply(axis=1) to update both columns
            df = df.apply(lambda row: update_code_version(row, column_name, version_value), axis=1)
    return df

def apply_medium_column_updates(df):
    df["M-Dig"] = df["medium"].apply(lambda x: res_upd_helper(x, "Digital"))
    df["M-TV"] = df["medium"].apply(lambda x: res_upd_helper(x, "Television"))
    df["M-NP"] = df["medium"].apply(lambda x: res_upd_helper(x, "Naming/packaging"))
    df["M-R"] = df["medium"].apply(lambda x: res_upd_helper(x, "Radio"))
    df["M-C"] = df["medium"].apply(lambda x: res_upd_helper(x, "Cinema"))
    df["M-O"] = df["medium"].apply(lambda x: res_upd_helper(x, "Outdoor"))
    df["M-POS"] = df["medium"].apply(lambda x: res_upd_helper(x, "Point of sale"))
    df["M-P"] = df["medium"].apply(lambda x: res_upd_helper(x, "Print"))
    return df
def apply_code_section_column_updates(df):

    df["C-ai"] = df["code_section"].apply(lambda x: res_upd_helper(x, "(a)(i)"))
    df["C-aii"] = df["code_section"].apply(lambda x: res_upd_helper(x, "(a)(ii)"))
    df["C-aiii"] = df["code_section"].apply(lambda x: res_upd_helper(x, "(a)(iii)"))
    df["C-aiv"] = df["code_section"].apply(lambda x: res_upd_helper(x, "(a)(iv)"))
    df["C-bi"] = df["code_section"].apply(lambda x: res_upd_helper(x, "(b)(i)"))
    df["C-bii"] = df["code_section"].apply(lambda x: res_upd_helper(x, "(b)(ii)"))
    df["C-biii"] = df["code_section"].apply(lambda x: res_upd_helper(x, "(b)(iii)"))
    df["C-biv"] = df["code_section"].apply(lambda x: res_upd_helper(x, "(b)(iv)"))
    df["C-ci"] = df["code_section"].apply(lambda x: res_upd_helper(x, "(c)(i)"))
    df["C-cii"] = df["code_section"].apply(lambda x: res_upd_helper(x, "(c)(ii)"))
    df["C-ciii"] = df["code_section"].apply(lambda x: res_upd_helper(x, "(c)(iii)"))
    df["C-civ"] = df["code_section"].apply(lambda x: res_upd_helper(x, "(c)(iv)"))
    df["C-d"] = df["code_section"].apply(lambda x: res_upd_helper(x, "(d)"))
    return df

def get_final_page_index() -> int:

    logging.debug("CALL: get_final_page_index()")

    STORED_FINAL_PAGE_INDEX_NUMBER = ADVARS.get_last_page_index()

    final_page_number = STORED_FINAL_PAGE_INDEX_NUMBER

    logging.debug(f"Final page number from DB is: {final_page_number}")

    code = 200

    logging.debug("Checking final page url")

    while code == 200:
        final_page_number += 1
        print(final_page_number)
        final_page_url = f"{ADVARS.get_base_url()}{final_page_number}/"
        final_page_response = requests.get(final_page_url)
        logging.debug(f"Final page URL response {final_page_response}")
        code = final_page_response.status_code

    range_boundary = final_page_number
    final_page_number -= 1

    logging.debug("Loop exited")
    logging.debug(f"Final Page Number is: {final_page_number}")
    logging.debug(f"Range boundary is: {range_boundary}")

    if STORED_FINAL_PAGE_INDEX_NUMBER == final_page_number:
        logging.debug("Last page index has not changed.")
    else:
        logging.debug("Last page index to be updated.")
        # db_data.set_last_page_index(final_page_number)
        ADVARS.set_last_page_index(final_page_number)
        ADVARS.update_db()

    logging.debug("EXIT: get_final_page_index()")

    return range_boundary

if __name__ == "__main__":
    main()