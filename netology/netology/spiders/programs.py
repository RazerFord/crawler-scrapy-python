import scrapy
import json
from netology.items import NetologyItem
from urllib.parse import urlencode

API_KEY = "6a3fe92755c2709ff62efb276f01821c"


def get_scraperapi_url(url):
    if url == "":
        return
    payload = {"api_key": API_KEY, "url": url}
    proxy_url = "http://api.scraperapi.com/?" + urlencode(payload)
    return proxy_url


class ProgramsSpider(scrapy.Spider):
    name = "programs"

    allowed_domains = ["api.scraperapi.com", "netology.ru"]

    custom_settings = {
        "FEEDS": {
            "items.csv": {
                "format": "csv",
                "store_empty": False,
            }
        }
    }

    start_urls = [get_scraperapi_url("https://netology.ru/backend/api/programs")]

    def parse(self, response):
        raw_data = response.body
        data = json.loads(raw_data)
        items = []
        for program in data:
            item = NetologyItem()
            item["program_id"] = program["id"]
            item["program_name"] = program["name"]
            item["program_url"] = "https:" + program["url"]
            item["program_reviews"] = program["url"].split("/")[-1]
            items.append(item)

        # for item in items:
        url = "https://netology.ru/backend/api/page_contents/marketing-director"
        request = scrapy.Request(url, callback=self.getReviews)
        request.cb_kwargs["item"] = items[0]
        yield request

    def getReviews(self, response, item):
        raw_data = response.body
        data = json.loads(raw_data)
        components = data["content"]["_componentOrders"]
        reviews_id = []
        for component in components:
            if "studentsReviews" in component:
                reviews_id.append(component)
        contents = data["content"]
        reviews = []
        for review in reviews_id:
            if review in contents:
                reviews.append(
                    [
                        {"name": x["name"], "text": x["text"]}
                        for x in contents[review]["reviews"]
                    ]
                )

        yield item
