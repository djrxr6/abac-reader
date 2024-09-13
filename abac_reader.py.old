import requests
from bs4 import BeautifulSoup

filename = 'abac-adjudications.csv'

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


def scrape_abac():
    #Set a temporary iterator to prevent reading of every url
    i = 0

    #Open a file (existing) to write output to. (will overwrite)
    output_file = open("abac-adjudications-detailed.txt", "w")
    output_file.write("title;url;date;decision;brand;company;outcome;nature;medium;code_section\n")
    output_file.close()

    output_file = open("abac-adjudications-detailed.txt", "a")

    with open(filename) as file:
        for line in file:
            url = line.split(";")[0]
            output_line = read_urls_list(url)
            output_file.write(output_line + "\n")
            print(i)

            i += 1
            if i == 2:
                break
    output_file.close()
def sanitise_data():
    input_file = "abac-adjudications"

########
# Start
########
#scrape_abac()
#sanitise_data()
