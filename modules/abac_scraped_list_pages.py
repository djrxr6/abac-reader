from modules.scraped_content import ScrapedContent


class AbacScrapedListPages(ScrapedContent):

    redis_key: str = "abac_data:scraped_adjudication_list_pages"
