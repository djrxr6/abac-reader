import modules.abac_data as ad
import modules.abac_data_vars as advars
import modules.abac_scraped_list_pages as aslp
import modules.redis_connector as rc
import modules.abac_scraped_content as asc

RC = rc.RedisConnector()

AD = ad.AbacData(RC)
ADVARS = advars.AbacDataVars(RC)
ASC = asc.AbacScrapedContent(RC)
ASLP = aslp.AbacScrapedListPages(RC)

url = 'https://www.abac.org.au/adjudication/11-22/'
url = 'https://www.abac.org.au/adjudication/129-18/'

def test_get_base_url():
    assert ADVARS.get_base_url() == 'https://www.abac.org.au/adjudication/page/'

def test_get_last_page_index():
    ADVARS.set_last_page_index(1)
    assert ADVARS.get_last_page_index() == 1

def test_url_in_database():
    url = 'https://www.abac.org.au/adjudication/11-22/'
    assert AD.is_adjudication_page_in_data(url)

def test_url_not_in_database():
    url = 'https://www.abac.org.au/adjudication/129-188/'
    assert not AD.is_adjudication_page_in_data(url)

print(ADVARS.get_last_page_index())
print(ADVARS.get_base_url())

#print(ASLP.get_content_list())

#print(ASC.get_content_list())

#ASC.drop_duplicates()

#AD.sort_data('date')
AD.sort_data(['year','month','day'])

#print(AD.get_most_recent_adjudication_url())

#print(AD.is_adjudication_page_in_data(url))