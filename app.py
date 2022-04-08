from os import sep
from posixpath import split
from bs4 import BeautifulSoup, ResultSet
import redis

import requests, logging
import pandas as pd
from modules.abac_scraped_list_pages import AbacScrapedListPages
from modules.redis_connector import RedisConnector
from modules.abac_data import AbacData
from modules.abac_scraped_content import AbacScrapedContent

import modules.abac_data_vars as advars

def check_for_more_entries(li: ResultSet,i: int) -> int:
    entries = 0
    if i < len(li):
        if li[i].name == "dd":
            entries += 1
            entries += check_for_more_entries(li,i+1)
    return entries

def scrape_adjudication_page(url: str,index_page: str) -> str:

    if ASC.is_adjudication_page_in_scraped_data(url):
        article = ASC.fetch_audjdication_page_content(url)
        article = BeautifulSoup(article, "html.parser")
    else:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        article = soup.find("article")
        ASC.insert_scraped_content(url,str(article))

    title = article.find("h1").text
    element_list = article.find_all(["dt","dd"])
    
    #Field Separator
    fs = ";"

    #Variable for building output line
    output_line = title + fs + index_page + fs+ url + fs

    list_iterator = 0
    while list_iterator < len(element_list):
    #for list_iterator, element in enumerate(element_list):
        if element_list[list_iterator].name == "dt":
            if (
                (   element_list[list_iterator].text in ["Brand Involved"] 
                    and element_list[list_iterator + 2].text in ["Company"])
                or
                (   element_list[list_iterator].text in ["Outcome"] 
                    and element_list[list_iterator + 2].text in ["Nature of Breach"])
                ):
                output_line += element_list[list_iterator + 1].text + fs + element_list[list_iterator + 3].text + fs
                list_iterator += 4
            elif (
                element_list[list_iterator].text in ["Brand Involved"] 
                or element_list[list_iterator].text in ["Outcome"]
                ):
                output_line += element_list[list_iterator + 1].text +fs + "" + fs
                list_iterator += 2 
            else:
                list_iterator += 1
        elif element_list[list_iterator].name == "dd":
            if list_iterator < len(element_list)-1:
                number = check_for_more_entries(element_list, list_iterator)
                if number > 1:
                    x = 0
                    while x < number:
                        output_line += element_list[list_iterator+x].text + ","
                        x += 1
                else:
                    output_line += element_list[list_iterator].text
                output_line += fs
                list_iterator += number
            else:
                output_line += element_list[list_iterator].text
                list_iterator += 1

    return output_line

def get_urls_from_abac_page(page_url: str) -> list:
    logging.debug(f'Page Index URL:{page_url}')

    if ASLP.is_adjudication_page_in_scraped_data(page_url):
        logging.debug(f'Index page cached.')
        article = ASLP.fetch_audjdication_page_content(page_url)
        article = BeautifulSoup(article, "html.parser")
    else:
        logging.debug(f'Index page not cached. Adding to DB.')
        page = requests.get(page_url)
        soup = BeautifulSoup(page.content, "html.parser")
        article = soup.find("article", {"class":"archive", "id":"content"})
        ASLP.insert_scraped_content(page_url,str(article))

    list_of_headings = article.find_all('h2')

    urls_array = []
    logging.debug(f'Parsing adjudications...')
    for heading in list_of_headings:
        anchor_element = heading.a 
        url = anchor_element.get('href')
        logging.debug(f'Parsing adjudication {url}...')
        if not db_data.is_adjudication_page_in_data(url):
            urls_array.append(scrape_adjudication_page(url,page_url))
    logging.debug(f'Parsing of adjudications complete...')
    return urls_array

def write_primary_results_csv_file(lines_array: list) -> None:

    output_file_name = "abac-adjudications-detailed.txt"

    with open(output_file_name, "w") as output_file:
        output_file.write("title;url;date;decision;brand;company;outcome;nature;medium;code_section\n")

    with open(output_file_name, "a") as output_file:
        for line in lines_array:
            output_file.write(line + "\n")

def write_final_results_csv_file() -> None:
    results = pd.read_csv("abac-adjudications-detailed.txt",sep=";",index_col=False)

    print(results)

    results = add_new_columns(results)

    print(results[["medium",'M-Dig','M-TV']])
    print(results.loc[0:3,'medium':'M-Dig'])

    results.to_csv('abac-adjudications-full-NEW.txt',sep=";",index=False)

def res_upd_helper(target: str, search: str) -> int:
    if target is None:
        var = 0
    else:
        var = 1 if(search in target) else 0
        var = 0 if('Part' in target) else var
    return var

def add_new_columns(df) -> pd.DataFrame:

    df['M-Dig'] = df['medium'].apply(lambda x: res_upd_helper(x, 'Digital'))
    df['M-TV'] = df['medium'].apply(lambda x: res_upd_helper(x, 'Television'))
    df['M-NP'] = df['medium'].apply(lambda x: res_upd_helper(x, 'Naming/packaging'))
    df['M-R'] = df['medium'].apply(lambda x: res_upd_helper(x, 'Radio'))
    df['M-C'] = df['medium'].apply(lambda x: res_upd_helper(x, 'Cinema'))
    df['M-O'] = df['medium'].apply(lambda x: res_upd_helper(x, 'Outdoor'))
    df['M-POS'] = df['medium'].apply(lambda x: res_upd_helper(x, 'Point of sale'))
    df['M-P'] = df['medium'].apply(lambda x: res_upd_helper(x, 'Print'))

    df['C-ai'] = df['code_section'].apply(lambda x: res_upd_helper(x, '(a)(i)'))
    df['C-aii'] = df['code_section'].apply(lambda x: res_upd_helper(x, '(a)(ii)'))
    df['C-aiii'] = df['code_section'].apply(lambda x: res_upd_helper(x, '(a)(iii)'))
    df['C-aiv'] = df['code_section'].apply(lambda x: res_upd_helper(x, '(a)(iv)'))
    df['C-bi'] = df['code_section'].apply(lambda x: res_upd_helper(x, '(b)(i)'))
    df['C-bii'] = df['code_section'].apply(lambda x: res_upd_helper(x, '(b)(ii)'))
    df['C-biii'] = df['code_section'].apply(lambda x: res_upd_helper(x, '(b)(iii)'))
    df['C-biv'] = df['code_section'].apply(lambda x: res_upd_helper(x, '(b)(iv)'))
    df['C-ci'] = df['code_section'].apply(lambda x: res_upd_helper(x, '(c)(i)'))
    df['C-cii'] = df['code_section'].apply(lambda x: res_upd_helper(x, '(c)(ii)'))
    df['C-ciii'] = df['code_section'].apply(lambda x: res_upd_helper(x, '(c)(iii)'))
    df['C-civ'] = df['code_section'].apply(lambda x: res_upd_helper(x, '(c)(iv)'))
    df['C-d'] = df['code_section'].apply(lambda x: res_upd_helper(x, '(d)'))

    date = pd.DatetimeIndex(df['date'])

    df['year'] = date.year
    df['month'] = date.month
    df['day'] = date.day

    return df

def get_final_page_index() -> int:

    logging.debug("CALL: get_final_page_index()")

    STORED_FINAL_PAGE_INDEX_NUMBER = ADVARS.get_last_page_index()
    
    final_page_number = STORED_FINAL_PAGE_INDEX_NUMBER

    logging.debug(f"Final page number from DB is: {final_page_number}")

    code = 200

    logging.debug('Checking final page url')

    while code == 200:
        final_page_number += 1
        print(final_page_number)
        final_page_url = f"{BASE_URL}{final_page_number}/"
        final_page_response = requests.get(final_page_url)
        logging.debug(f'Final page URL response {final_page_response}')
        code = final_page_response.status_code
    
    range_boundary = final_page_number
    final_page_number -= 1

    logging.debug("Loop exited")
    logging.debug(f"Final Page Number is: {final_page_number}")
    logging.debug(f"Range boundary is: {range_boundary}")

    if STORED_FINAL_PAGE_INDEX_NUMBER == final_page_number:
        logging.debug('Last page index has not changed.')
    else:
        logging.debug('Last page index to be updated.')
        #db_data.set_last_page_index(final_page_number)
        ADVARS.set_last_page_index(final_page_number)
        ADVARS.update_db()

    logging.debug("EXIT: get_final_page_index()")

    return range_boundary

def is_new_adjudications() -> bool:
    logging.debug('CALL: is_new_adjudications()')
    newest_adjudications_page_index_url = f'{BASE_URL}1/'

    page = requests.get(newest_adjudications_page_index_url)
    soup=BeautifulSoup(page.content, "html.parser")

    main_article_element = soup.find("article", {"class":"archive", "id":"content"})
    list_of_headings = main_article_element.find_all('h2')

    anchor_element = list_of_headings[0].a 
    url = anchor_element.get('href')
    logging.debug(f'Most recent adjudication URL is {url}')

    db_url = db_data.get_most_recent_adjudication_url().strip('"')
    logging.debug(f'Most recent adjudication URL in DB is {db_url}')

    logging.debug(f'New adjudications? {url != db_url}')

    logging.debug('EXIT: is_new_adjudications()')
    return url != db_url

########################################
# Begin
########################################

#TODO: Some variables need to be renamed to be more accurate. (urls_array and abac_adjudications_pages_urls)

logging.basicConfig(level=logging.DEBUG)
logging.debug('abac-reader started')

redis_connector = RedisConnector()

db_data = AbacData(redis_connector)

ASC = AbacScrapedContent(redis_connector)
ASLP = AbacScrapedListPages(redis_connector)
ADVARS = advars.AbacDataVars(redis_connector)

BASE_URL = ADVARS.get_base_url()

json_existing_abac_data = db_data.get_abac_data()

if json_existing_abac_data is None:
    df_existing_abac_data = pd.DataFrame()
else:
    df_existing_abac_data = pd.read_json(db_data.get_abac_data(), convert_dates=False)

if is_new_adjudications():
    
    logging.debug("New adjudications have been found.")

    #Destroy the cached index pages data
    ASLP.insert_new_data("[]")

    abac_adjudications_pages_urls = []
    array_of_abac_data = []

    for page_index in range(1, get_final_page_index()):
        abac_adjudications_pages_urls.extend(get_urls_from_abac_page(f'{BASE_URL}{page_index}'))        

    columns = "title;index_page;url;date;decision;brand;company;outcome;nature;medium;code_section;temp_column"
    columns = columns.split(';')

    for line in abac_adjudications_pages_urls:
        logging.debug(f'{line}')
        row = line.split(';')        
        if len(row) == len(columns) - 1:
            row.append(' ')
        array_of_abac_data.append(row)
    
    df_new_abac_adjudications = pd.DataFrame(array_of_abac_data,columns=columns)
    df_new_abac_adjudications = df_new_abac_adjudications.drop(columns=['temp_column'])
    df_new_abac_adjudications = add_new_columns(df_new_abac_adjudications)
    df_new_abac_adjudications = df_new_abac_adjudications.iloc[::-1]

    
    df_updated_abac_adjudications = pd.concat([df_existing_abac_data,df_new_abac_adjudications],ignore_index=True)

    json_abac_adjudications = df_updated_abac_adjudications.to_json(orient="records")

    db_data.set_abac_data(json_abac_adjudications)

    #Currently keeping functionality to write csv file output
    write_primary_results_csv_file(abac_adjudications_pages_urls)
    #write_final_results_csv_file()

else:
    logging.debug("There are no new adjudications.")
