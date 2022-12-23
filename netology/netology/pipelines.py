# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import psycopg2


class NetologyPipeline:
    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter["program_id"] in self.ids_seen:
            raise DropItem(f"Duplicate item found: {item!r}")
        else:
            self.ids_seen.add(adapter["program_id"])
        return item

class DatabasePipeline:
    def open_spider(self, spider):
        hostname = "db"
        username = "postgres"
        password = "postgres"
        database = "netology"
        try:
            self.connection = psycopg2.connect(
                host=hostname, user=username, password=password, dbname=database
            )
            self.cur = self.connection.cursor()
            print("open database connection")
        except Exception:
            print("error database connection")

    def close_spider(self, spider):
        if self.cur is not None:
            self.cur.close()
            self.connection.close()
            print("close database connection")

    def process_item(self, item, spider):
        pass