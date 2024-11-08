import requests
import logging
from bs4 import BeautifulSoup
from modules.abac_scraped_content import AbacScrapedContent
from modules.abac_scraped_list_pages import AbacScrapedListPages
from modules.abac_data import AbacData
from modules.abac_data_vars import AbacDataVars
from icecream import ic

filename = 'abac-adjudications.csv'

class ABACScraper:
    ASC: AbacScrapedContent
    ASLP: AbacScrapedListPages
    ADVARS: AbacDataVars
    db_data: AbacData

    def __init__(self, ASC: AbacScrapedContent, ASLP: AbacScrapedListPages, ADVARS: AbacDataVars, db_data: AbacData):
        self.ASC = ASC
        self.ASLP = ASLP
        self.ADVARS = ADVARS
        self.db_data = db_data
        pass

    def check_for_more_entries(self,li,i) -> int:
        entries: int = 0
        if i < len(li):
            if li[i].name == "dd":
                entries += 1
                entries += self.check_for_more_entries(li,i+1)
        return entries

    #def read_urls_list(self, url: str) -> str:

        #page = requests.get(url)
        #soup = BeautifulSoup(page.content, "html.parser")

        #title = soup.find("h1").text
        #element_list = soup.find_all(["dt","dd"])

        ##Field Separator
        #fs: str = ";"

        ##Variable for building output line
        #output_line = title + fs + url + fs

        #list_iterator: int = 0
        #while list_iterator < len(element_list):
        ##for list_iterator, element in enumerate(element_list):
            #if element_list[list_iterator].name == "dt":
                #if (
                    #(   element_list[list_iterator].text in ["Brand Involved"] 
                        #and element_list[list_iterator + 2].text in ["Company"])
                    #or
                    #(   element_list[list_iterator].text in ["Outcome"] 
                        #and element_list[list_iterator + 2].text in ["Nature of Breach"])
                    #):
                    #output_line += element_list[list_iterator + 1].text + fs + element_list[list_iterator + 3].text + fs
                    #list_iterator += 4
                #elif (
                    #element_list[list_iterator].text in ["Brand Involved"] 
                    #or element_list[list_iterator].text in ["Outcome"]
                    #):
                    #output_line += element_list[list_iterator + 1].text +fs + "" + fs
                    #list_iterator += 2 
                #else:
                    #list_iterator += 1
            #elif element_list[list_iterator].name == "dd":
                #if list_iterator < len(element_list)-1:
                    #number = self.check_for_more_entries(element_list, list_iterator)
                    #if number > 1:
                        #x = 0
                        #while x < number:
                            #output_line += element_list[list_iterator+x].text + ","
                            #x += 1
                    #else:
                        #output_line += element_list[list_iterator].text
                    #output_line += fs
                    #list_iterator += number
                #else:
                    #output_line += element_list[list_iterator].text
                    #list_iterator += 1
        #return output_line


#    def scrape_abac(self) -> None:
#        #Set a temporary iterator to prevent reading of every url
#        i = 0
#
#        #Open a file (existing) to write output to. (will overwrite)
#        output_file = open("abac-adjudications-detailed.txt", "w")
#        output_file.write("title;url;date;decision;brand;company;outcome;nature;medium;code_section\n")
#        output_file.close()
#
#        output_file = open("abac-adjudications-detailed.txt", "a")
#
#        with open(filename) as file:
#            for line in file:
#                url = line.split(";")[0]
#                output_line = self.read_urls_list(url)
#                output_file.write(output_line + "\n")
#                print(i)
#
#                i += 1
#                if i == 2:
#                    break
#        output_file.close()

    def get_urls_from_abac_page(self, page_url: str) -> list:

        logging.debug(f"Page Index URL:{page_url}")

        if self.ASLP.is_adjudication_page_in_scraped_data(page_url):
            logging.debug(f"Index page cached.")
            article = self.ASLP.fetch_audjdication_page_content(page_url)
            article = BeautifulSoup(article, "html.parser")
        else:
            logging.debug(f"Index page not cached. Adding to DB.")
            page = requests.get(page_url)
            soup = BeautifulSoup(page.content, "html.parser")
            article = soup.find("article", {"class": "archive", "id": "content"})
            self.ASLP.insert_scraped_content(page_url, str(article))

        list_of_headings = article.find_all("h2")

        urls_array = []
        logging.debug(f"Parsing adjudications...")
        for heading in list_of_headings:
            anchor_element = heading.a
            url = anchor_element.get("href")
            logging.debug(f"Parsing adjudication {url}...")
            if not self.db_data.is_adjudication_page_in_scraped_data(url):
                logging.debug(f"Adjudication {url} not in DB.")
                urls_array.append(self.scrape_adjudication_page(url, page_url))
            else:
                logging.debug(f"Adjudication {url} already in DB.")
        logging.debug(f"Parsing of adjudications complete...")
        ic(urls_array)
        return urls_array

    def scrape_adjudication_page(self, url: str, index_page: str) -> str:

        if self.ASC.is_adjudication_page_in_scraped_data(url):
            article = self.ASC.fetch_audjdication_page_content(url)
            article = BeautifulSoup(article, "html.parser")
        else:
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")
            article = soup.find("article")
            self.ASC.insert_scraped_content(url, str(article))

        title = article.find("h1")
        dt_elements = article.find_all("dt")

        dictionary_object = {
            'title': title.get_text(strip=True),
            'url': url,
            'index_page_url': index_page 
        }

        dt_dd_dict = {}
        # Iterate over all dt elements
        for dt in dt_elements:
            # Get the text for the current dt
            dt_text = dt.get_text(strip=True)
    
            # Collect all dd elements that follow the current dt until the next dt
            dd_texts = []
            for sibling in dt.find_next_siblings():
                if sibling.name == "dt":
                    break
                if sibling.name == "dd":
                    dd_texts.append(sibling.get_text(strip=True))
    
            # Join the dd texts into a comma-separated string and add to the dictionary
            dt_dd_dict[dt_text] = ", ".join(dd_texts)

        # Update the main dictionary object with the dt/dd pairs
        dictionary_object.update(dt_dd_dict)

        key_mapping = {
            'title': 'title',
            'url': 'url',
            'index_page': 'index_page_url',
            'Date of determination': 'date',
            'Determination number' : 'determination_number',
            'Decision': 'decision',
            'Brand Involved': 'brand',
            'Company': 'company',
            'Outcome': 'outcome',
            'Medium': 'medium',
            'Media': 'medium',
            'Nature of Breach': 'nature_of_breach',

        }
        
        dictionary_object = self.update_keys(dictionary_object, key_mapping)

        return dictionary_object
        ### END

    def is_new_adjudications(self ) -> bool:
        logging.debug("CALL: is_new_adjudications()")
        
        #Check for increase to pagination pages.
#        if self.get_current_final_page_index() > self.ADVARS.get_last_page_index():
#            logging.debug("Pagination pages have increased.")
#            logging.debug(f"New final page index is {self.get_current_final_page_index()}")
#            self.ADVARS.set_last_page_index(self.get_current_final_page_index())
#            self.ADVARS.update_db()
#            return True
#



        ic(self.get_current_final_page_index())
        ic(self.get_current_final_page_index == self.ADVARS.get_last_page_index())

        oldest_adjudications_page_index_url = f"{self.ADVARS.get_base_url()}{self.ADVARS.get_last_page_index()}/"
        ic(oldest_adjudications_page_index_url)
        # get the total number of records in the adjucations list pages and multiply it by ten
        #ic(self.ASLP.get_record_count() /10 % 10 )
        #ic(self.ASLP.get_record_count() )
        #get the total number of adjudications and get the remainder of the division by ten.
        #ic(self.ASC.get_record_count() % 10)
        # get the total number of records and modulo by the previous    number. taking the remainder.
        # get the number of urls on the final list page
        # compare the modulod result to the numbe of urls on the final list page.


        
        newest_adjudications_page_index_url = f"{self.ADVARS.get_base_url()}1/"

        page = requests.get(newest_adjudications_page_index_url)
        soup = BeautifulSoup(page.content, "html.parser")

        main_article_element = soup.find("article", {"class": "archive", "id": "content"})
        list_of_headings = main_article_element.find_all("h2")

        anchor_element = list_of_headings[0].a
        url = anchor_element.get("href")
        logging.debug(f"Most recent adjudication URL is {url}")

        db_url = self.db_data.get_most_recent_adjudication_url().strip('"')
        logging.debug(f"Most recent adjudication URL in DB is {db_url}")

        logging.debug(f"New adjudications? {url != db_url}")

        logging.debug("EXIT: is_new_adjudications()")
        return url != db_url


    def get_current_final_page_index(self) -> int:

        logging.debug("CALL: get_current_final_page_index()")
        logging.debug(f"Final page number from DB is: {self.ADVARS.get_last_page_index()}")
        logging.debug("Checking final page url")

        final_page_number = self.ADVARS.get_last_page_index()
        code = 200

        while code == 200:
            final_page_number += 1
            print(final_page_number)
            url_to_test = f"{self.ADVARS.get_base_url()}{final_page_number}/"
            response = requests.get(url_to_test)
            logging.debug(f"Final page URL response {response}")
            code = response.status_code

        current_final_page_number = final_page_number - 1

        ic(f"Has the final page index changed? {current_final_page_number != self.ADVARS.get_last_page_index()}")

        return current_final_page_number

    def update_keys(self, dictionary_object, key_mapping) -> dict:
        return {key_mapping.get(key, key): value for key, value in dictionary_object.items()}
