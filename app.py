from os import sep
from posixpath import split
from bs4 import BeautifulSoup

import requests
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

def read_urls_list(url):

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
        urls_array.append(read_urls_list(url))
        print(read_urls_list(url))


    return urls_array

def write_csv_file(lines_array):
    #Open a file (existing) to write output to. (will overwrite)
    output_file = open("abac-adjudications-detailed.txt", "w")
    output_file.write("title;url;date;decision;brand;company;outcome;nature;medium;code_section\n")
    output_file.close()

    output_file = open("abac-adjudications-detailed.txt", "a")
    for line in lines_array:
        output_file.write(line + "\n")
    output_file.close()
########################################
# Begin
########################################



last_page_number = 2

abac_adjudications_pages_urls = []

#get_urls_from_abac_page('https://www.abac.org.au/adjudication/page/1')

#print(results)

#abac_adjudications_pages_urls.extend(get_urls_from_abac_page('https://www.abac.org.au/adjudication/page/1'))
#abac_adjudications_pages_urls.extend(get_urls_from_abac_page('https://www.abac.org.au/adjudication/page/2'))


#write_csv_file(abac_adjudications_pages_urls)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', 10)

results = pd.read_csv("abac-adjudications-detailed.txt",sep=";",index_col=False)

print(results)

new_column_names = [
"M-Dig",
"M-TV",
"M-NP",
"M-R",
"M-C",
"M-O",
"M-POS",
"M-P",
"C-ai",
"C-aii",
"C-aiii",
"C-aiv",
"C-bi",
"C-bii",
"C-biii",
"C-biv",
"C-ci",
"C-cii",
"C-ciii",
"C-civ",
"C-d",
"Month",
"Year"
]

for column_name in new_column_names:
    results[column_name] = 0

results.to_csv('abac-adjudications-full-NEW.txt')


#print(abac_adjudications_pages_urls)

#for url in abac_adjudications_pages_urls:
    #print(url)
    #print(ar.read_urls_list(url))
