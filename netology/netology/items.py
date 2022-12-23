# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import Join, MapCompose
from w3lib.html import remove_tags
import unicodedata

def clear(text):
    unicodedata.normalize('NFKD', remove_tags(text))

class NetologyItem(scrapy.Item):
    program_id = scrapy.Field()
    program_name = scrapy.Field()
    program_url = scrapy.Field()
    program_description = scrapy.Field(input_processor=MapCompose(clear), output_processor=Join())
    program_programs = scrapy.Field(input_processor=MapCompose(clear), output_processor=Join())
    program_modules = scrapy.Field(input_processor=MapCompose(clear), output_processor=Join())
    program_directions = scrapy.Field(input_processor=MapCompose(clear), output_processor=Join())
    program_duration = scrapy.Field(input_processor=MapCompose(clear), output_processor=Join())
    program_cost = scrapy.Field(input_processor=MapCompose(clear), output_processor=Join())
    program_level_of_training = scrapy.Field(input_processor=MapCompose(clear), output_processor=Join())
    program_reviews = scrapy.Field(input_processor=MapCompose(clear), output_processor=Join())
