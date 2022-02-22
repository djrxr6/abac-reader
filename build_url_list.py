import requests
from bs4 import BeautifulSoup

import abac_reader as ar

def get_urls_from_abac_page(page_url,results_data_frame):
    page = requests.get(page_url)
    soup=BeautifulSoup(page.content, "html.parser")

    main_article_element = soup.find("article", {"class":"archive", "id":"content"})

    list_of_headings = main_article_element.find_all('h2')

    urls_array = []

    for count, heading in enumerate(list_of_headings):
        anchor_element = heading.a 
        url = anchor_element.get('href')
        #urls_array.append(anchor_element.get('href'))
        print(ar.read_urls_list(url))


    return urls_array

if __name__ == "__main__":
    print('build_url_list.py loaded')
