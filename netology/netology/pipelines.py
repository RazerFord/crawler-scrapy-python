# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import psycopg2
import traceback
from .helpers.clear import clear
from .helpers.database_queries import DatabaseQueries


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

        host = "db"
        user = "postgres"
        passw = "postgres"
        dbname = "netology"
        self.dbQuery = DatabaseQueries(host, user, passw, dbname)

        url = "netology"
        self.source_id = self.dbQuery.getSourceId(url)

        data = self.dbQuery.getCourseMetadataIds(self.source_id)

        self.allCourseId = {id: False for id, _ in data}
        self.allCourseSourceIdToId = {
            source_couse_id: id for id, source_couse_id in data
        }

    def close_spider(self, spider):
        try:
            courseIds = [
                id for id, exists in self.allCourseId.items() if exists == False
            ]
            if len(courseIds) > 0:
                self.dbQuery.deleteIn(courseIds)
                print("courses with next id deleted: ", courseIds)

        except Exception as error:
            traceback.print_exc()
            print(error)
            self.dbQuery.rollback()

    def ifExists(self, value, default):
        return default if value is None else value

    def ifKeyExists(self, value, key, default):
        if value is not None and key in value:
            return value[key]
        return default

    def saveLevel(self, adapter):
        if (
            "program_level_of_training" in adapter
            and adapter["program_level_of_training"] is not None
            and adapter["program_level_of_training"]["id"] not in self.levelIds
        ):
            self.levelIds.add(adapter["program_level_of_training"]["id"])
            self.dbQuery.insertIntoLevelIfNotExists(
                id=adapter["program_level_of_training"]["id"],
                level=adapter["program_level_of_training"]["name"],
            )

    def saveMetadata(self, adapter):
        if (
            "program_id" in adapter
            and adapter["program_id"] is not None
            and adapter["program_id"] not in self.courseIds
        ):
            self.courseIds.add(adapter["program_id"])
            self.dbQuery.insertIntoCourseMetaDataIfNotExists(
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

    def saveCourseRaw(self, adapter):
        if "program_modules" not in adapter:
            return

        courseId = self.dbQuery.selectCourseMetadataWhereUrl(adapter["program_url"])[0]

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

        self.dbQuery.insertOrUpdateIntoCourseRaw(
            course_id=courseId,
            title=adapter["program_name"],
            section_title=sections,
            preview=previews,
            description=description,
            program=lessons,
        )

    def saveReview(self, adapter):
        if "program_reviews" not in adapter:
            return

        courseId = self.dbQuery.selectCourseMetadataWhereUrl(adapter["program_url"])[0]

        for review in adapter["program_reviews"]:
            self.dbQuery.insertIntoReviewIfNotExists(
                course_id=courseId, text=review["text"], author=review["name"]
            )

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
            self.dbQuery.rollback()

        return item
