# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import traceback
from .helpers.clear import clear
from .helpers.database_queries import DatabaseQueries

"""Обрабатывает дубликаты
"""
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

"""Сохранение информации в БД
"""
class DatabasePipeline:
    """Создает объект для взаимодействия с БД, инициализирует вспомогательные структуры данных

    Args:
        self   (DatabasePipeline): экземпляр класса
        spider (netology.spiders.programs.ProgramsSpider): паук

    Returns:
        None
    """
    def open_spider(self, spider):
        self.levelIds = set()
        self.courseIds = set()

        paramsDb = spider.settings.attributes

        host = paramsDb["HOSTNAME"].value
        user = paramsDb["USERNAME"].value
        passw = paramsDb["PASSWORD"].value
        dbname = paramsDb["DBNAME"].value

        self.dbQuery = DatabaseQueries(host, user, passw, dbname)

        url = "netology"
        self.source_id = self.dbQuery.getSourceId(url)

        data = self.dbQuery.getCourseMetadataIds(self.source_id)

        self.allCourseId = {id: False for id, _ in data}
        self.allCourseSourceIdToId = {
            source_couse_id: id for id, source_couse_id in data
        }
        self.levelWebsiteToLevelBd = {}

    """Удаляет курсы, которых нет на интернет ресурсе

    Args:
        self   (DatabasePipeline): экземпляр класса
        spider (netology.spiders.programs.ProgramsSpider): паук

    Returns:
        None
    """
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

    """Возвращает значение по-умолчанию, если значение None

    Args:
        self    (DatabasePipeline): экземпляр класса
        value   (type): значение
        default (type): значение по-умолчанию

    Returns:
        type: значение или значение по-умолчанию
    """
    def ifExists(self, value, default):
        return default if value is None else value

    """Возвращает значение по-умолчанию, если ключа не существует

    Args:
        self    (DatabasePipeline): экземпляр класса
        value   (dict): словарь значений
        key     (str): ключ
        default (type): значение по-умолчанию

    Returns:
        type: значение или значение по-умолчанию
    """
    def ifKeyExists(self, value, key, default):
        if value is not None and key in value:
            return value[key]
        return default

    """Сохраняет сложности курсов

    Args:
        self    (DatabasePipeline): экземпляр класса
        adapter (itemadapter.adapter.ItemAdapter): информация о курсе

    Returns:
        None
    """
    def saveLevel(self, adapter):
        # Проверка, что уровень сложности еще не сохранен
        if (
            "program_level_of_training" in adapter
            and adapter["program_level_of_training"] is not None
            and adapter["program_level_of_training"]["id"] not in self.levelIds
        ):
            name = adapter["program_level_of_training"]["name"]
            
            self.dbQuery.insertIntoLevelIfNotExists(
                level=name,
            )

            self.levelWebsiteToLevelBd[adapter["program_level_of_training"]["id"]] = self.dbQuery.selectLevelWhereText(name)[0]

            self.levelIds.add(adapter["program_level_of_training"]["id"])

    """Сохраняет запись о курсе в таблице course_metadata

    Args:
        self    (DatabasePipeline): экземпляр класса
        adapter (itemadapter.adapter.ItemAdapter): информация о курсе

    Returns:
        None
    """
    def saveMetadata(self, adapter):
        # Проверка, что курс еще не сохранен
        if (
            "program_id" in adapter
            and adapter["program_id"] is not None
            and adapter["program_id"] not in self.courseIds
        ):
            self.courseIds.add(adapter["program_id"])
            self.dbQuery.insertOrUpdateIntoMetaData(
                source_couse_id=adapter["program_id"],
                source_id=self.source_id,
                url=adapter["program_url"],
                duration=self.ifKeyExists(adapter["program_duration"], "duration", 0),
                level_id=self.levelWebsiteToLevelBd[self.ifKeyExists(
                    adapter["program_level_of_training"], "id", 1
                )],
                price=adapter["program_cost"]["current_price"],
                price_other=adapter["program_cost"]["initial_price"],
            )

    """Сохраняет запись о курсе в таблице course_raw. Форматирует ячейки превью и программы

    Args:
        self    (DatabasePipeline): экземпляр класса
        adapter (itemadapter.adapter.ItemAdapter): информация о курсе

    Returns:
        None
    """
    def saveCourseRaw(self, adapter):
        # Проверка, что существует описание модулей у данного курса
        if "program_modules" not in adapter:
            return

        courseId = self.dbQuery.selectCourseMetadataWhereUrl(adapter["program_url"])[0]

        sections = ""

        # Объединение всех направлений в одну строку
        for section in adapter["program_directions"]:
            if "name" in section:
                sections += section["name"] + ". "

        indexModule = 1
        indexLesson = 1

        previews = ""
        lessons = ""
        # Объединение всех модулей в одну строку и форматирование
        for module in adapter["program_modules"]:
            previews += f"{indexModule}. {module['description']}\n"
            lessons += f"{indexModule}. {module['title']}\n"
            for lesson in module["lessons"]:
                if "title" in lesson:
                    lessons += f"{indexModule}.{indexLesson}. {clear(lesson['title'])}{clear(lesson['description']) if 'description' in lesson else ''}\n"
                    indexLesson += 1
            indexModule += 1

        # Удаление лишних переносов строки
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

    """Сохраняет отзывы о курсе в таблцу reviews

    Args:
        self    (DatabasePipeline): экземпляр класса
        adapter (itemadapter.adapter.ItemAdapter): информация о курсе

    Returns:
        None
    """
    def saveReview(self, adapter):
        # Проверка, что существует описание модулей у данного курса
        if "program_reviews" not in adapter:
            return

        courseId = self.dbQuery.selectCourseMetadataWhereUrl(adapter["program_url"])[0]

        for review in adapter["program_reviews"]:
            self.dbQuery.insertIntoReviewIfNotExists(
                course_id=courseId, text=review["text"], author=review["name"]
            )

    """Сохраняет отзывы о курсе в таблцу reviews

    Args:
        self    (DatabasePipeline): экземпляр класса
        item (NetologyItem): информация о курсе
        spider (netology.spiders.programs.ProgramsSpider): паук

    Returns:
        NetologyItem: элемент с информацией о курсе
    """
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        try:
            # Если курс, который есть в БД присутствует в ответе, то пометить это. 
            # Необходимо для удаления курсов, которые были удалены с интернет-ресурса
            if adapter["program_id"] in self.allCourseSourceIdToId:
                self.allCourseId[
                    self.allCourseSourceIdToId[adapter["program_id"]]
                ] = True

            # Сохранить уровень курса
            self.saveLevel(adapter)

            # Сохранить метаинформацию о курсе
            self.saveMetadata(adapter)

            # Сохранить информацию о курсе
            self.saveCourseRaw(adapter)

            # Сохранить отзыв
            self.saveReview(adapter)

        except Exception as error:
            traceback.print_exc()
            print(error)
            print(adapter["program_id"], adapter["program_name"], "not save")
            self.dbQuery.rollback()

        return item
