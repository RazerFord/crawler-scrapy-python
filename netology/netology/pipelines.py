# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import psycopg2
import traceback


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

        self.source_id = self.getSourceId()

    def getSourceId(self):
        SQL = """SELECT * FROM source
        WHERE url ILIKE %s"""

        url = "netology"

        self.cur.execute(SQL, [url])

        return self.cur.fetchone()[0]

    def close_spider(self, spider):
        if self.cur is not None:
            self.cur.close()
            self.connection.close()
            print("close database connection")

    def ifExists(self, value, default):
        return default if value is None else value

    def ifKeyExists(self, value, key, default):
        if value is not None and key in value:
            return value[key]
        return default

    def selectCourseMetadataWhereUrl(self, url):
        SQL = """select * from course_metadata
        where url = %s"""
        self.cur.execute(SQL, [url])
        return self.cur.fetchone()

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
            "program_level_of_training" in adapter
            and adapter["program_level_of_training"] is not None
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
        course_metadata(source_id,url,duration,level_id,price,price_other) 
        select %s, %s, %s, %s, %s, %s where not exists 
        (select id from course_metadata where url ILIKE %s)"""
        data = (
            kwargs["source_id"],
            kwargs["url"],
            kwargs["duration"],
            kwargs["level_id"],
            kwargs["price"],
            kwargs["price_other"],
            kwargs["url"],
        )

        self.cur.execute(SQL, data)

    def saveMetadata(self, adapter):
        if (
            "program_id" in adapter
            and adapter["program_id"] is not None
            and adapter["program_id"] not in self.courseIds
        ):
            self.courseIds.add(adapter["program_id"])
            self.insertIntoCourseMetaDataIfNotExists(
                id=adapter["program_id"],
                source_id=self.source_id,
                url=adapter["program_url"],
                duration=self.ifKeyExists(adapter["program_duration"], "duration", 0),
                level_id=self.ifKeyExists(
                    adapter["program_level_of_training"], "id", 1
                ),
                price=adapter["program_cost"]["current_price"],
                price_other=adapter["program_cost"]["initial_price"],
            )
            self.connection.commit()

    def insertIntoCourseRawIfNotExists(self, **kwargs):
        SQL = """insert into 
        course_raw(course_id,title,section_title,preview,description,program) 
        select %s, %s, %s, %s, %s, %s"""
        data = (
            kwargs["course_id"],
            kwargs["title"],
            kwargs["section_title"],
            kwargs["preview"],
            kwargs["description"],
            kwargs["program"],
        )
        self.cur.execute(SQL, data)
        self.connection.commit()

    def saveCourseRaw(self, adapter):
        courseId = self.selectCourseMetadataWhereUrl(adapter["program_url"])[0]

        sections = ""
        for section in adapter["program_directions"]:
            if "name" in section:
                sections += section["name"] + ". "

        if "program_modules" not in adapter:
            return

        for module in adapter["program_modules"]:
            self.insertIntoCourseRawIfNotExists(
                course_id=courseId,
                title=adapter["program_name"],
                section_title=sections,
                preview="",
                description=module["description"],
                program=module["lessons"],
            )

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        try:
            # Save level course
            self.saveLevel(adapter)

            # Save metadata of course
            self.saveMetadata(adapter)

            # Save course raw
            self.saveCourseRaw(adapter)
        except Exception as error:
            traceback.print_exc()
            print(error)
            print(adapter["program_id"], adapter["program_name"], "not save")
            self.connection.rollback()
        return item
