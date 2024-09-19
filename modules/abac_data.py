import redis

from modules.redis_connector import RedisConnector
from modules.scraped_content import ScrapedContent


class AbacData(ScrapedContent):

    redis_key: str = "abac_data"

    def get_most_recent_adjudication_url(self) -> str:
        try:
            last_index = self.rd.execute_command("JSON.ARRLEN", self.redis_key, "$")
        except redis.exceptions.ResponseError:
            url_at_index = ""
        else:
            last_record_position = last_index[0] - 1
            url_at_index = self.rd.execute_command(
                "JSON.GET", self.redis_key, f"[{last_record_position}].url"
            )
        return url_at_index
