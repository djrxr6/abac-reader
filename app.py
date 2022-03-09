from os import sep
from posixpath import split
from xmlrpc.client import ResponseError
from bs4 import BeautifulSoup

import requests, logging, redis
import pandas as pd

def check_for_more_entries(li,i):
    entries = 0
    if i < len(li):
        if li[i].name == "dd":
            entries += 1
            entries += check_for_more_entries(li,i+1)
    return entries

def scrape_adjudication_page(url):

    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    title = soup.find("h1").text
    element_list = soup.find_all(["dt","dd"])

    #Field Separator
    fs = ";"

    #Variable for building output line
    output_line = title + fs + url + fs

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

def get_urls_from_abac_page(page_url):
    page = requests.get(page_url)
    soup=BeautifulSoup(page.content, "html.parser")

    main_article_element = soup.find("article", {"class":"archive", "id":"content"})
    list_of_headings = main_article_element.find_all('h2')

    urls_array = []

    for heading in list_of_headings:
        anchor_element = heading.a 
        url = anchor_element.get('href')
        urls_array.append(scrape_adjudication_page(url))
        #TODO: In here I can work out how to stop when the data is already recorded so as not to retrive it again.
    return urls_array

def write_primary_results_csv_file(lines_array):

    output_file_name = "abac-adjudications-detailed.txt"

    with open(output_file_name, "w") as output_file:
        output_file.write("title;url;date;decision;brand;company;outcome;nature;medium;code_section\n")

    with open(output_file_name, "a") as output_file:
        for line in lines_array:
            output_file.write(line + "\n")

def write_final_results_csv_file():
    results = pd.read_csv("abac-adjudications-detailed.txt",sep=";",index_col=False)

    print(results)

    results = add_new_columns(results)

    print(results[["medium",'M-Dig','M-TV']])
    print(results.loc[0:3,'medium':'M-Dig'])

    results.to_csv('abac-adjudications-full-NEW.txt',sep=";",index=False)

def add_new_columns(df):

    df['M-Dig'] = df['medium'].apply(lambda row: 1 if ('Digital' in row) else 0)
    df['M-TV'] = df['medium'].apply(lambda row: 1 if ('Television' in row) else 0)
    df['M-NP'] = df['medium'].apply(lambda row: 1 if ('Naming/packaging' in row) else 0)
    df['M-R'] = df['medium'].apply(lambda row: 1 if ('Radio' in row) else 0)
    df['M-C'] = df['medium'].apply(lambda row: 1 if ('Cinema' in row) else 0)
    df['M-O'] = df['medium'].apply(lambda row: 1 if ('Outdoor' in row) else 0)
    df['M-POS'] = df['medium'].apply(lambda row: 1 if ('Point of sale' in row) else 0)
    df['M-P'] = df['medium'].apply(lambda row: 1 if ('Print' in row) else 0)

    df["C-ai"] = df['code_section'].apply(lambda row: 1 if ("(a)(i)" in row) else 0)
    df["C-aii"] = df['code_section'].apply(lambda row: 1 if ("(a)(ii)" in row) else 0)
    df["C-aiii"] = df['code_section'].apply(lambda row: 1 if ("(a)(iii)" in row) else 0)
    df["C-aiv"] = df['code_section'].apply(lambda row: 1 if ("(a)(iv)" in row) else 0)
    df["C-bi"] = df['code_section'].apply(lambda row: 1 if ("(b)(i)" in row) else 0)
    df["C-bii"] = df['code_section'].apply(lambda row: 1 if ("(b)(ii)" in row) else 0)
    df["C-biii"] = df['code_section'].apply(lambda row: 1 if ("(b)(iii)" in row) else 0)
    df["C-biv"] = df['code_section'].apply(lambda row: 1 if ("(b)(iv)" in row) else 0)
    df["C-ci"] = df['code_section'].apply(lambda row: 1 if ("(c)(i)" in row) else 0)
    df["C-cii"] = df['code_section'].apply(lambda row: 1 if ("(c)(ii)" in row) else 0)
    df["C-ciii"] = df['code_section'].apply(lambda row: 1 if ("(c)(iii)" in row) else 0)
    df["C-civ"] = df['code_section'].apply(lambda row: 1 if ("(c)(iv)" in row) else 0)
    df["C-d"] = df['code_section'].apply(lambda row: 1 if ("(d)" in row) else 0)

    return df

def get_final_page_index():

    logging.debug("CALL: get_final_page_index()")
    #take most recent highest index from database
    #increment until response 400, rewriting variable for each 200 response
    #update value in database
    #return final page number (first 400 response index, minus one)
    
    final_page_number = DB_LAST_PAGE_INDEX

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

    if DB_LAST_PAGE_INDEX == final_page_number:
        logging.debug('Last page index has not changed.')
    else:
        logging.debug('Last page index to be updated.')
        db_data.set_last_page_index(final_page_number)

    logging.debug("EXIT: get_final_page_index()")

    return range_boundary

def is_new_adjudications():
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

    logging.debug('EXIT: is_new_adjudications()')
    return url == db_url

#def get_most_recent_adjudication_in_db():
#    return MOST_RECENT_ADJUDICATION_URL_FROM_DATABASE

class DbData:
    rd = ''
    host, port = '192.168.1.117',6379

    def __init__(this):
        this.rd = redis.Redis(this.host, this.port, decode_responses=True)

    def get_last_page_index(this):
        return int(this.rd.get("LAST_PAGE_INDEX"))
    
    def set_last_page_index(this, val):
        this.rd.set("LAST_PAGE_INDEX",val)
        
    def get_base_url(this):
        return this.rd.get("BASE_URL")
    
    def get_most_recent_adjudication_url(this):
        try:
            last_index = this.rd.execute_command('JSON.ARRLEN','abac_data','$')
        except redis.exceptions.ResponseError:
            url_at_index = ''
        else:
            last_record_position = last_index[0] -1
            url_at_index = this.rd.execute_command('JSON.GET' ,'abac_data', f'[{last_record_position}].url')
        return url_at_index
    
    def set_abac_data(this,json_string):
        this.rd.execute_command('JSON.SET','abac_data','$',json_string)

    def add_abac_data(this,json_string):
        this.rd.execute_command('JSON.ARRAPPEND','abac_data','$',json_string)
    
    def get_abac_data(this):
        return this.rd.execute_command('JSON.GET','abac_data')

########################################
# Begin
########################################

#TODO: Some variables need to be renamed to be more accurate. (urls_array and abac_adjudications_pages_urls)

logging.basicConfig(level=logging.DEBUG)
logging.debug('abac-reader started')

db_data = DbData()

BASE_URL = db_data.get_base_url()

DB_LAST_PAGE_INDEX = db_data.get_last_page_index()

json_existing_abac_data = db_data.get_abac_data()

if json_existing_abac_data is None:
    df_existing_abac_data = pd.DataFrame()
else:
    df_existing_abac_data = pd.read_json(db_data.get_abac_data())
    #TODO: Need to look into how I can stop date conversion. Might be in the Redis class "decode"

if not is_new_adjudications():
    
    logging.debug("New adjudications have been found.")

    abac_adjudications_pages_urls = []
    array_of_abac_data = []

    for page_index in range(1, get_final_page_index()):
        abac_adjudications_pages_urls.extend(get_urls_from_abac_page(f'{BASE_URL}{page_index}'))        

    columns = "title;url;date;decision;brand;company;outcome;nature;medium;code_section;temp_column"
    columns = columns.split(';')

    for line in abac_adjudications_pages_urls:
        array_of_abac_data.append(line.split(';'))
    
    df_new_abac_adjudications = pd.DataFrame(array_of_abac_data,columns=columns)
    df_new_abac_adjudications = df_new_abac_adjudications.drop(columns=['temp_column'])
    df_new_abac_adjudications = add_new_columns(df_new_abac_adjudications)
    df_new_abac_adjudications = df_new_abac_adjudications.iloc[::-1]

    df_updated_abac_adjudications = pd.concat([df_existing_abac_data,df_new_abac_adjudications],ignore_index=True)

    json_abac_adjudications = df_updated_abac_adjudications.to_json(orient="records")

    db_data.set_abac_data(json_abac_adjudications)

    #Currently keeping functionality to write csv file output
    #write_primary_results_csv_file(abac_adjudications_pages_urls)
    #write_final_results_csv_file()

else:
    logging.debug("There are no new adjudications.")
