# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NetologyItem(scrapy.Item):
    program_id = scrapy.Field()
    program_name = scrapy.Field()
    program_url = scrapy.Field()
    program_description = scrapy.Field(serializer=str)
    program_key_skills = scrapy.Field(serializer=str)
    program_programs = scrapy.Field(serializer=str)  # courseFeaturesWithImages
    program_duration = scrapy.Field(serializer=str)
    program_cost = scrapy.Field(serializer=str)
    program_level_of_training = scrapy.Field(serializer=str)  # coursePresentation
    program_reviews = scrapy.Field(serializer=str)


# 1. название курса ++
# 1. url ++
# 1.1 название поставщика --
# 2. описание,
# 2.1. ключевые скилы
# 3. программа (самая подробная)
# 4. срок (длительность)
# 5. стоимость
# 6. уровень подготовки (базовый, средний, продвинутый)
# 7. отзывы и оценка слушателей
