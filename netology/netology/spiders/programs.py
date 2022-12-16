import scrapy
import json
from netology.items import NetologyItem
from urllib.parse import urlencode
from scrapy import Selector
import html2text


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
            item["program_level_of_training"] = program["rank"]
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
        raw_data = response.body

        if len(raw_data) == 0:
            yield item
            return

        data = json.loads(raw_data)

        if (
            data is None
            or data["content"] is None
            or "_componentOrders" not in data["content"]
        ):
            yield item
            return

        components = data["content"]["_componentOrders"]

        reviews_id, descriptions_id, course_features_id = self.getComponentsId(
            components
        )

        contents = data["content"]

        item["program_reviews"] = self.getReviews(reviews_id, contents)

        item["program_description"] = self.getDescriptions(
            item["program_description"], descriptions_id, contents
        )

        item["program_programs"] = self.getCourseFeatures(course_features_id, contents)

        if (
            "coursePresentation" in contents
            and "stats" in contents["coursePresentation"]
        ):
            stats = contents["coursePresentation"]["stats"]
            for stat in stats:
                if "Уровень" in stat["title"]:
                    item["program_level_of_training"] = clear(stat["value"])

        yield item

    def getComponentsId(self, components):
        reviews_id = []
        descriptions_id = []
        course_features_id = []

        for component in components:
            if "studentsReviews" in component:
                reviews_id.append(component)
            if "courseDescriptionText" in component:
                descriptions_id.append(component)
            if "courseFeaturesWithImages" in component:
                course_features_id.append(component)

        return reviews_id, descriptions_id, course_features_id

    def getReviews(self, reviews_id, contents):
        reviews = []
        for review in reviews_id:
            if review in contents:
                reviews.append(
                    [
                        {
                            "name": clear(x["name"]),
                            "text": clear(x["text"]),
                        }
                        for x in contents[review]["reviews"]
                    ]
                )
        return reviews

    def getDescriptions(self, descriptions, descriptions_id, contents):
        for description in descriptions_id:
            if description in contents:
                text = clear(
                    contents[description]["text"] + contents[description]["title"]
                )
                if text is None:
                    continue
                descriptions.append(text)
        return descriptions

    def getCourseFeatures(self, course_features_id, contents):
        course_features = []
        for course_feature in course_features_id:
            if course_feature in contents:
                course_features.append(
                    [
                        {
                            "title": clear(item["title"]),
                            "description": clear(item["description"]),
                        }
                        for item in contents[course_feature]["items"]
                    ]
                )
        return course_features
