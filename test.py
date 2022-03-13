import modules.abac_data as ad
import modules.abac_scraped_list_pages as aslp
import modules.redis_connector as rc
import modules.abac_scraped_content as asc

RC = rc.RedisConnector()

AD = ad.AbacData(RC)
ASC = asc.AbacScrapedContent(RC)
ASLP = aslp.AbacScrapedListPages(RC)

url = 'https://www.abac.org.au/adjudication/11-22/'
url = 'https://www.abac.org.au/adjudication/129-18/'

#print(ASLP.get_content_list())

#print(ASC.get_content_list())

#ASC.drop_duplicates()

#AD.sort_data('date')
AD.sort_data(['year','month','day'])

#print(AD.get_most_recent_adjudication_url())

#print(AD.is_adjudication_page_in_data(url))