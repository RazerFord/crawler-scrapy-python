import scrapy
import json
from netology.items import NetologyItem
from urllib.parse import urlencode
from scrapy import Selector
import html2text
from .parse_course_json import CourseJson


API_KEY = "6a3fe92755c2709ff62efb276f01821c"


def clear(text_):
    if text_ is None:
        return ""
    h = html2text.HTML2Text()
    h.ignore_links = True
    return h.handle(text_)


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
            "items.json": {
                "format": "json",
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
            item["program_duration"] = {
                "duration": program["duration"],
                "projects_amount": program["projects_amount"],
            }
            item["program_cost"] = {
                "initial_price": program["initial_price"],
                "current_price": program["current_price"],
            }
            item["program_directions"] = program["directions"]
            item["program_level_of_training"] = program["educational_level"]
            item["program_description"] = [clear(program["description"])]
            item["program_url"] = "https:" + program["url"]

            items.append(item)

        for item in items:
            url = (
                "https://netology.ru/backend/api/page_contents/"
                + item["program_url"].split("/")[-1]
            )
            request = scrapy.Request(url, callback=self.getInformation)
            request.cb_kwargs["item"] = item
            yield request

    def getInformation(self, response, item):
        try:
            courseJson = CourseJson(response)

            item["program_reviews"] = courseJson.getReviews()

            item["program_description"] = courseJson.getDescriptions(
                item["program_description"]
            )

            item["program_programs"] = courseJson.getCourseFeatures()

            item["program_modules"] = courseJson.getProgramModules()
        except ValueError as error:
            print(error)

        yield item
