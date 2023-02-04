# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import psycopg2
import traceback
from .helper.clear import clear


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

        self.allCourseId, self.allCourseSourceIdToId = self.getCourseMetadataIds()

    def getCourseMetadataIds(self):
        SQL = """SELECT id, source_couse_id FROM course_metadata"""

        self.cur.execute(SQL)
        data = self.cur.fetchall()

        allCourseId = {id: False for id, _ in data}
        allCourseSourceIdToId = {source_couse_id: id for id, source_couse_id in data}

        return allCourseId, allCourseSourceIdToId

    def getSourceId(self):
        SQL = """SELECT * FROM source
        WHERE url ILIKE %s"""

        url = "netology"

        self.cur.execute(SQL, [url])

        return self.cur.fetchone()[0]

    def close_spider(self, spider):
        try:
            courseIds = [
                id for id, exists in self.allCourseId.items() if exists == False
            ]
            if len(courseIds) > 0:
                self.deleteIn(courseIds)
                print("courses with next id deleted: ", courseIds)

        except Exception as error:
            traceback.print_exc()
            print(error)
            self.connection.rollback()

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
        course_metadata(source_couse_id, source_id,url,duration,level_id,price,price_other) 
        select %s, %s, %s, %s, %s, %s, %s where not exists 
        (select id from course_metadata where url ILIKE %s)"""

        data = (
            kwargs["source_couse_id"],
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
                source_couse_id=adapter["program_id"],
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

    def insertIntoCourseRaw(self, **kwargs):
        SQL = """DO $$
                 BEGIN
                 IF EXISTS(SELECT * FROM course_raw WHERE course_id=%s) THEN
                 	UPDATE course_raw SET title=%s, 
                                               section_title=%s, 
                                               preview=%s, 
                                               description=%s, 
                                               program=%s 
                                               WHERE course_id=%s;
                 ELSE
                 	INSERT INTO course_raw(course_id,title,section_title,preview,description,program)
                    SELECT %s, %s, %s, %s, %s, %s;
                 END IF;
                 END $$;"""
        data = (
            kwargs["course_id"],
            kwargs["title"],
            kwargs["section_title"],
            kwargs["preview"],
            kwargs["description"],
            kwargs["program"],
            kwargs["course_id"],
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
        if "program_modules" not in adapter:
            return

        courseId = self.selectCourseMetadataWhereUrl(adapter["program_url"])[0]

        sections = ""

        for section in adapter["program_directions"]:
            if "name" in section:
                sections += section["name"] + ". "

        indexModule = 1
        indexLesson = 1

        previews = ""
        lessons = ""
        for module in adapter["program_modules"]:
            previews += f"{indexModule}. {module['description']}\n"
            lessons += f"{indexModule}. {module['title']}\n"
            for lesson in module["lessons"]:
                if "title" in lesson:
                    lessons += f"{indexModule}.{indexLesson}. {clear(lesson['title'])}{clear(lesson['description']) if 'description' in lesson else ''}\n"
                    indexLesson += 1
            indexModule += 1

        previews = "\n".join([s for s in previews.split("\n") if s != ""])
        lessons = "\n".join([s for s in lessons.split("\n") if s != ""])
        description = "\n".join(
            s for s in "".join(adapter["program_description"]).split("\n") if s != ""
        )

        self.insertIntoCourseRaw(
            course_id=courseId,
            title=adapter["program_name"],
            section_title=sections,
            preview=previews,
            description=description,
            program=lessons,
        )

    def insertIntoReviewIfNotExists(self, **kwargs):
        SQL = """insert into 
        reviews(course_id,text,author) 
        select %s, %s, %s where not exists
        (select * from reviews
        where course_id = %s and text ILIKE %s and author ILIKE %s)"""
        data = (
            kwargs["course_id"],
            kwargs["text"],
            kwargs["author"],
            kwargs["course_id"],
            kwargs["text"],
            kwargs["author"] + "%",
        )
        self.cur.execute(SQL, data)
        self.connection.commit()

    def saveReview(self, adapter):
        if "program_reviews" not in adapter:
            return

        courseId = self.selectCourseMetadataWhereUrl(adapter["program_url"])[0]

        for review in adapter["program_reviews"]:
            self.insertIntoReviewIfNotExists(
                course_id=courseId, text=review["text"], author=review["name"]
            )

    def deleteIn(self, courseIds):
        self.cur.execute(
            "DELETE FROM course_metadata WHERE id IN %(list_course)s",
            {"list_course": tuple(courseIds)},
        )
        self.connection.commit()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        try:
            if adapter["program_id"] in self.allCourseSourceIdToId:
                self.allCourseId[
                    self.allCourseSourceIdToId[adapter["program_id"]]
                ] = True

            # Save level course
            self.saveLevel(adapter)

            # Save metadata of course
            self.saveMetadata(adapter)

            # Save course raw
            self.saveCourseRaw(adapter)

            # Save review
            self.saveReview(adapter)

        except Exception as error:
            traceback.print_exc()
            print(error)
            print(adapter["program_id"], adapter["program_name"], "not save")
            self.connection.rollback()

        return item
