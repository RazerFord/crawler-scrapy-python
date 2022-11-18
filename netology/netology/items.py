# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NetologyItem(scrapy.Item):
    program_id = scrapy.Field()
    program_name = scrapy.Field()
    program_url = scrapy.Field()
