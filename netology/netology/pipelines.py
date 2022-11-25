# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class NetologyPipeline:
    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['program_id'] in self.ids_seen:
            raise ItemAdapter("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['program_id'])
        return item
