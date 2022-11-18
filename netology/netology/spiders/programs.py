import scrapy
import json
from netology.items import NetologyItem
from urllib.parse import urlencode

API_KEY = '6a3fe92755c2709ff62efb276f01821c'

def get_scraperapi_url(url):
    if url == "":
        return
    payload = {'api_key': API_KEY, 'url': url}
    proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
    return proxy_url

class ProgramsSpider(scrapy.Spider):
    name = "programs"
    
    allowed_domains = ["netology.ru"]

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
        for program in data:
            item = NetologyItem()
            item["program_id"] = program["id"]
            item["program_name"] = program["name"]
            item["program_url"] = "https:" + program["url"]
            item["program_reviews"] = self.test()
            yield item

    def test(self):
        return [1, 2, 3, 4, 5, 6]