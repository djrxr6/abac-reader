import enum
from os import sep
from pathlib import Path
from posixpath import split
from bs4 import BeautifulSoup

import requests, logging, redis
#import build_url_list as bul
#import abac_reader as ar
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
        #urls_array.append(anchor_element.get('href'))
        urls_array.append(scrape_adjudication_page(url))
        #TODO: In here I can work out how to stop when the data is already recorded so as not to retrive it again.
    return urls_array

def write_primary_results_csv_file(lines_array):
    output_file_name = "abac-adjudications-detailed.txt"
    #Open a file (existing) to write output to. (will overwrite)
    with open(output_file_name, "w") as output_file:
    #output_file = open("abac-adjudications-detailed.txt", "w")
        output_file.write("title;url;date;decision;brand;company;outcome;nature;medium;code_section\n")
    #output_file.close()

    with open(output_file_name, "a") as output_file:
    #output_file = open("abac-adjudications-detailed.txt", "a")
        for line in lines_array:
            output_file.write(line + "\n")
    #output_file.close()

def write_final_results_csv_file():
    results = pd.read_csv("abac-adjudications-detailed.txt",sep=";",index_col=False)

    print(results)


    # new_column_names = [
    # "M-Dig",
    # "M-TV",
    # "M-NP",
    # "M-R",
    # "M-C",
    # "M-O",
    # "M-POS",
    # "M-P",
    # "C-ai",
    # "C-aii",
    # "C-aiii",
    # "C-aiv",
    # "C-bi",
    # "C-bii",
    # "C-biii",
    # "C-biv",
    # "C-ci",
    # "C-cii",
    # "C-ciii",
    # "C-civ",
    # "C-d",
    # "Month",
    # "Year"
    # ]

    # for column_name in new_column_names:
    #     results[column_name] = 0

    results['M-Dig'] = results['medium'].apply(lambda row: 1 if ('Digital' in row) else 0)
    results['M-TV'] = results['medium'].apply(lambda row: 1 if ('Television' in row) else 0)
    results['M-NP'] = results['medium'].apply(lambda row: 1 if ('Naming/packaging' in row) else 0)
    results['M-R'] = results['medium'].apply(lambda row: 1 if ('Radio' in row) else 0)
    results['M-C'] = results['medium'].apply(lambda row: 1 if ('Cinema' in row) else 0)
    results['M-O'] = results['medium'].apply(lambda row: 1 if ('Outdoor' in row) else 0)
    results['M-POS'] = results['medium'].apply(lambda row: 1 if ('Point of sale' in row) else 0)
    results['M-P'] = results['medium'].apply(lambda row: 1 if ('Print' in row) else 0)

    results["C-ai"] = results['code_section'].apply(lambda row: 1 if ("(a)(i)" in row) else 0)
    results["C-aii"] = results['code_section'].apply(lambda row: 1 if ("(a)(ii)" in row) else 0)
    results["C-aiii"] = results['code_section'].apply(lambda row: 1 if ("(a)(iii)" in row) else 0)
    results["C-aiv"] = results['code_section'].apply(lambda row: 1 if ("(a)(iv)" in row) else 0)
    results["C-bi"] = results['code_section'].apply(lambda row: 1 if ("(b)(i)" in row) else 0)
    results["C-bii"] = results['code_section'].apply(lambda row: 1 if ("(b)(ii)" in row) else 0)
    results["C-biii"] = results['code_section'].apply(lambda row: 1 if ("(b)(iii)" in row) else 0)
    results["C-biv"] = results['code_section'].apply(lambda row: 1 if ("(b)(iv)" in row) else 0)
    results["C-ci"] = results['code_section'].apply(lambda row: 1 if ("(c)(i)" in row) else 0)
    results["C-cii"] = results['code_section'].apply(lambda row: 1 if ("(c)(ii)" in row) else 0)
    results["C-ciii"] = results['code_section'].apply(lambda row: 1 if ("(c)(iii)" in row) else 0)
    results["C-civ"] = results['code_section'].apply(lambda row: 1 if ("(c)(iv)" in row) else 0)
    results["C-d"] = results['code_section'].apply(lambda row: 1 if ("(d)" in row) else 0)

    #print(results[["code_section",'C-bi','C-d','C-bii','C-ai']])

    print(results[["medium",'M-Dig','M-TV']])
    print(results.loc[0:3,'medium':'M-Dig'])

    results.to_csv('abac-adjudications-full-NEW.txt',sep=";",index=False)

def get_final_page_index():
    logging.debug("CALL: get_final_page_index()")
    #take most recent highest index from database
    #increment until response 400, rewriting variable for each 200 response
    #update value in database
    #return final page number (first 400 response index, minus one)
    
    #TODO: Retrieve final index from database
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
    
    final_page_number -= 1

    logging.debug("Loop exited")
    logging.debug(f"Final Page Number is: {final_page_number}")

    #TODO: update database with new final index
    if DB_LAST_PAGE_INDEX == final_page_number:
        logging.debug('Last page index has not changed.')
    else:
        logging.debug('Last page index to be updated.')

    logging.debug("EXIT: get_final_page_index()")
    return final_page_number

def is_new_adjudications():
    logging.debug('CALL: is_new_adjudications()')
    newest_adjudications_page_index_url = f'{BASE_URL}1/'

    page = requests.get(newest_adjudications_page_index_url)
    soup=BeautifulSoup(page.content, "html.parser")

    main_article_element = soup.find("article", {"class":"archive", "id":"content"})
    list_of_headings = main_article_element.find_all('h2')

    anchor_element = list_of_headings[0].a 
    url = anchor_element.get('href')
    logging.debug('EXIT: is_new_adjudications()')
    return url == get_most_recent_adjudication_in_db()

def get_most_recent_adjudication_in_db():
    return MOST_RECENT_ADJUDICATION_URL_FROM_DATABASE

class DbData:
    rd = ''
    host, port ='192.168.1.117',6379
    def __init__(this):
        this.rd = redis.Redis(this.host, this.port, decode_responses=True)

    def get_last_page_index(this):
        return int(this.rd.get("LAST_PAGE_INDEX"))
        
    def get_base_url(this):
        return this.rd.get("BASE_URL")
    
    def get_most_recent_adjudication(this):
        return this.rd.get("MOST_RECENT_ADJUDICATION")
    
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

MOST_RECENT_ADJUDICATION_URL_FROM_DATABASE = db_data.get_most_recent_adjudication()

df_existing_abac_data = pd.read_json(db_data.get_abac_data())
print(df_existing_abac_data)

if not is_new_adjudications():
    
    logging.debug("New adjudications have been found.")

    abac_adjudications_pages_urls = []
    array_of_abac_data = []

    for page_index in range(1, 2):
    #for page_index in range(1, get_final_page_index()):
        abac_adjudications_pages_urls.extend(get_urls_from_abac_page(f'{BASE_URL}{page_index}'))        

    columns = "title;url;date;decision;brand;company;outcome;nature;medium;code_section;temp_column"
    columns = columns.split(';')

    for line in abac_adjudications_pages_urls:
        array_of_abac_data.append(line.split(';'))
        # df_abac_adjudication = pd.DataFrame([line.split(';')],columns=columns)
        # json_abac_adjudication = df_abac_adjudication.to_json(orient="records")
        # db_data.add_abac_data(json_abac_adjudication)

    print(array_of_abac_data)

    
    df_new_abac_adjudications = pd.DataFrame(array_of_abac_data,columns=columns)
    #TODO: remove temp column
    print(df_new_abac_adjudications)

    df_updated_abac_adjudications = pd.concat([df_new_abac_adjudications,df_existing_abac_data],ignore_index=True)

    json_abac_adjudications = df_updated_abac_adjudications.to_json(orient="records")
    print(json_abac_adjudications)
    db_data.set_abac_data(json_abac_adjudications)

    #write_primary_results_csv_file(abac_adjudications_pages_urls)

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    #pd.set_option('display.max_colwidth', 10)

    #write_final_results_csv_file()

    #print(abac_adjudications_pages_urls)

    #for url in abac_adjudications_pages_urls:
        #print(url)
        #print(ar.scrape_adjudication_page(url))
else:
    logging.debug("There are no new adjudications.")
