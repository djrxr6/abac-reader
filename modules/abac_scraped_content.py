import json
import pandas as pd

from modules.scraped_content import ScrapedContent


class AbacScrapedContent(ScrapedContent):

    redis_key: str = 'abac_data:scraped_content_from_adjudication_pages'