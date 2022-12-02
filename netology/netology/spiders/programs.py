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

            item["program_duration"] = {
                "duration": program["duration"],
                "projects_amount": program["projects_amount"],
            }

            item["program_cost"] = {
                "initial_price": program["initial_price"],
                "current_price": program["current_price"],
            }

            item["program_directions"] = program["directions"]

            item["program_level_of_training"] = {"rank": program["rank"]}

            item["program_description"] = [program["description"]]

            item["program_url"] = "https:" + program["url"]
            items.append(item)

        # for item in items:
        url = "https://netology.ru/backend/api/page_contents/" + items[0]["program_url"].split('/')[-1]
        request = scrapy.Request(url, callback=self.getReviews)
        request.cb_kwargs["item"] = items[0]
        yield request

    def getReviews(self, response, item):
        raw_data = response.body
        data = json.loads(raw_data)
        if data["content"] is None:
            yield item

        components = data["content"]["_componentOrders"]

        reviews_id = []
        description_id = []
        course_features_id = []
        for component in components:
            if "studentsReviews" in component:
                reviews_id.append(component)
            if "courseDescriptionText" in component:
                description_id.append(component)
            if "courseFeaturesWithImages" in component:
                course_features_id.append(component)

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
        item["program_reviews"] = reviews

        descriptions = item["program_description"]
        for description in description_id:
            if description in contents:
                descriptions.append(
                    contents[description]["text"] + contents[description]["title"]
                )
        item["program_description"] = descriptions

        course_features = []
        for course_feature in course_features_id:
            if course_feature in contents:
                course_features.append(
                    [
                        {"title": item["title"], "description": item["description"]}
                        for item in contents[course_feature]["items"]
                    ]
                )
        item["program_programs"] = course_features

        if (
            "coursePresentation" in contents
            and "stats" in contents["coursePresentation"]
        ):
            stats = contents["coursePresentation"]["stats"]
            for stat in stats:
                if "Уровень" in stat["title"]:
                    item["program_level_of_training"] = stat["value"]

        yield item
