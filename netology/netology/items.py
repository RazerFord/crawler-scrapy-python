# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NetologyItem(scrapy.Item):
    program_id = scrapy.Field()
    program_name = scrapy.Field()
    program_url = scrapy.Field()
    program_reviews = scrapy.Field(serializer=str)

class NetologyItemReview(scrapy.Item):
    review_id = scrapy.Field()
    review = scrapy.Field(serializer=str)
