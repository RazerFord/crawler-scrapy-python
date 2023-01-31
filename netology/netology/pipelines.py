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
        self.levelIds = set()
        self.courseIds = set()
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

    def ifExists(self, value, default):
        return default if value is None else value

    def ifKeyExists(self, value, key, default):
        if hasattr(value, key):
            return value[key]
        return default

    def insertIntoLevelIfNotExists(self, **kwargs):
        SQL = """insert into level(id,text) 
        select %s, %s where not exists 
        (select id from level where id = %s)"""
        data = (
            kwargs["id"],
            kwargs["level"],
            kwargs["id"],
        )
        self.cur.execute(SQL, data)

    def saveLevel(self, adapter):
        if (
            adapter["program_level_of_training"] is not None
            and adapter["program_level_of_training"]["id"] not in self.levelIds
        ):
            self.levelIds.add(adapter["program_level_of_training"]["id"])
            self.insertIntoLevelIfNotExists(
                id=adapter["program_level_of_training"]["id"],
                level=adapter["program_level_of_training"]["name"],
            )
            self.connection.commit()

    def insertIntoCourseMetaDataIfNotExists(self, **kwargs):
        SQL = """insert into 
        course_metadata(id,source_id,url,duration,level_id,price,price_other) 
        select %s, %s, %s, %s, %s, %s, %s where not exists 
        (select id from course_metadata where id = %s)"""
        data = (
            kwargs["id"],
            kwargs["source_id"],
            kwargs["url"],
            kwargs["duration"],
            kwargs["level_id"],
            kwargs["price"],
            kwargs["price_other"],
            kwargs["id"],
        )
        self.cur.execute(SQL, data)

    def saveMetadata(self, adapter):
        if (
            adapter["program_id"] is not None
            and adapter["program_id"] not in self.courseIds
        ):
            self.courseIds.add(adapter["program_id"])
            self.insertIntoCourseMetaDataIfNotExists(
                id=adapter["program_id"],
                source_id="1",
                url=adapter["program_url"],
                duration=self.ifKeyExists(adapter["program_duration"], "duration", 0),
                level_id=self.ifKeyExists(
                    adapter["program_level_of_training"], "id", 1
                ),
                price=adapter["program_cost"]["current_price"],
                price_other=adapter["program_cost"]["initial_price"],
            )
            self.connection.commit()

    def insertIntoCourseRowIfNotExists(self, **kwargs):
        SQL = """insert into 
        course_metadata(id,course_id,title,section_title,preview,description,program) 
        select %s, %s, %s, %s, %s, %s, %s where not exists
        (select id from course_metadata where id = %s)"""
        data = (
            kwargs["id"],
            kwargs["id"],
            kwargs["title"],
            kwargs["section_title"],
            kwargs["preview"],
            kwargs["description"],
            kwargs["program"],
            kwargs["id"],
        )
        self.cur.execute(SQL, data)

    def saveCourseRow(self, adapter):
        sections = ""
        for section in adapter["program_directions"]:
            if "name" in section:
                sections += section["name"] + ". "
        self.insertIntoCourseRowIfNotExists(
            id=adapter["program_id"],
            title=adapter["program_name"],
            section_title=sections,
            
        )
        print(adapter["program_id"], adapter["program_name"], "save course row")
        self.connection.commit()

        pass

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        try:
            # Save level course
            self.saveLevel(adapter)

            # Save metadata of course
            self.saveMetadata(adapter)

            # Save course row
            # self.saveCourseRow(adapter)

        except Exception as error:
            print(error)
            print(adapter["program_id"], adapter["program_name"], "not save")
            self.connection.rollback()
        return item
