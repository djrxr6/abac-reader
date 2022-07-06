from modules import redis_connector, abac_data, abac_data_vars
from modules import scraped_content

RC = redis_connector.RedisConnector()

ASC = scraped_content.ScrapedContent(RC)
ASC.set_redis_key("abac_data:scraped_content_from_adjudication_pages")


# -----------------------------------------------------------------
ADVARS = abac_data_vars.AbacDataVars(RC)


def test_get_base_url():
    assert ADVARS.get_base_url() == "https://www.abac.org.au/adjudication/page/"


def test_get_last_page_index():
    ADVARS.set_last_page_index(1)
    assert ADVARS.get_last_page_index() == 1


# -----------------------------------------------------------------
AD = abac_data.AbacData(RC)


def test_adjudication_url_in_database():
    url = "https://www.abac.org.au/adjudication/11-22/"
    assert AD.is_adjudication_page_in_data(url)


def test_adjudication_url_not_in_database():
    url = "https://www.abac.org.au/adjudication/129-188/"
    assert not AD.is_adjudication_page_in_data(url)


# -----------------------------------------------------------------

ASLP = scraped_content.ScrapedContent(RC)
ASLP.set_redis_key("abac_data:scraped_adjudication_list_pages")


def test_adjudication_index_page_url_in_database():
    url = "https://www.abac.org.au/adjudication/page/1"
    assert ASLP.is_adjudication_page_in_scraped_data(url)


def test_adjudication_index_page_url_not_in_database():
    url = "https://www.abac.org.au/adjudication/page/A/"
    assert not ASLP.is_adjudication_page_in_scraped_data(url)


print(ASLP.get_content_list())

print(ASC.get_content_list())

# ASC.drop_duplicates()

# AD.sort_data('date')
# AD.sort_data(['year','month','day'])

# print(AD.get_most_recent_adjudication_url())

# print(AD.is_adjudication_page_in_data(url))
