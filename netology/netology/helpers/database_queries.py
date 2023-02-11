import psycopg2
from .singleton import Singleton


class DatabaseQueries(metaclass=Singleton):
    """Открывает соединение с БД

    Args:
        self     (DatabaseQueries): экземпляр класса
        hostname (str): имя хоста
        username (str): имя пользователя
        password (str): пароль
        dbname   (str): имя БД

    Returns:
        None
    """
    def __init__(self, hostname, username, password, dbname):
        try:
            self.connection = psycopg2.connect(
                host=hostname, user=username, password=password, dbname=dbname
            )
            self.cur = self.connection.cursor()
            print("open database connection")
        except Exception:
            print("error database connection")

    """Закрывает соединение с БД

    Args:
        self     (DatabaseQueries): экземпляр класса

    Returns:
        None
    """
    def __del__(self):
        if self.cur is not None:
            self.cur.close()
            self.connection.close()
            print("close database connection")

    """Возвращает id источника в БД по URL

    Args:
        self   (DatabaseQueries): экземпляр класса
        source (str): URL источника

    Returns:
        int: id источника
    """
    def getSourceId(self, source):
        SQL = """SELECT id FROM source
        WHERE url ILIKE %s"""

        self.cur.execute(SQL, [source])

        return self.cur.fetchone()[0]

    """Возвращает записи из таблицы course_metadata в БД, отфильтрованные по source_id

    Args:
        self      (DatabaseQueries): экземпляр класса
        source_id (int): id источника

    Returns:
        [(int, int)]: массив пар (id, source_couse_id)
    """
    def getCourseMetadataIds(self, source_id):
        SQL = """SELECT id, source_couse_id FROM course_metadata WHERE source_id=%s"""

        self.cur.execute(SQL, [source_id])

        return self.cur.fetchall()

    """Возвращает запись из таблицы course_metadata в БД, отфильтрованные по URL

    Args:
        self (DatabaseQueries): экземпляр класса
        url  (str): url источника

    Returns:
        (int, int, int, str, str, str, int, int, int, str): кортеж с информацией о курсе
    """
    def selectCourseMetadataWhereUrl(self, url):
        SQL = """select * from course_metadata
        where url = %s"""

        self.cur.execute(SQL, [url])

        return self.cur.fetchone()

    """Получить уровень сложности

    Args:
        self (DatabaseQueries): экземпляр класса
        text  (str): уровень сложности

    Returns:
        (int, int, int, str, str, str, int, int, int, str): кортеж с информацией о курсе
    """
    def selectLevelWhereText(self, text):
        SQL = """select * from level
        where text = %s"""

        self.cur.execute(SQL, [text])

        return self.cur.fetchone()

    """Вставляет уровень сложности в таблицу level БД, если запись о сложности отсутствует

    Args:
        self            (DatabaseQueries): экземпляр класса
        kwargs["id"]    (int): id для проверки существования
        kwargs["level"] (str): уровень сложности

    Returns:
        None
    """
    def insertIntoLevelIfNotExists(self, **kwargs):
        SQL = """insert into level(text) 
        select %s where not exists 
        (select * from level where text = %s)"""
        data = (
            kwargs["level"],
            kwargs["level"],
        )
        self.cur.execute(SQL, data)
        self.connection.commit()

    """Всталяет или обновляет запись в таблице course_metadata БД, если переданный URL найден, то обновляет 

    Args:
        self                      (DatabaseQueries): экземпляр класса
        kwargs["source_couse_id"] (int): id в источнике
        kwargs["source_id"]       (int): id источника
        kwargs["url"]             (str): URL
        kwargs["duration"]        (str): длительность
        kwargs["level_id"]        (int): id уровня сложности
        kwargs["price"]           (int): стоимость
        kwargs["price_other"]     (int): другая стоимость

    Returns:
        None
    """
    def insertOrUpdateIntoMetaData(self, **kwargs):
        SQL = """DO $$
                 BEGIN
                 IF EXISTS(SELECT * FROM course_metadata WHERE url ILIKE %s) THEN
                 	UPDATE course_metadata SET source_couse_id=%s, 
                                               source_id=%s, 
                                               url=%s, 
                                               duration=%s, 
                                               level_id=%s,
                                               price=%s,
                                               price_other=%s 
                                         WHERE url ILIKE %s;
                 ELSE
                 	INSERT INTO course_metadata(source_couse_id, source_id,url,duration,level_id,price,price_other)
                    select %s, %s, %s, %s, %s, %s, %s;
                 END IF;
                 END $$;"""

        data = (
            kwargs["url"],
            kwargs["source_couse_id"],
            kwargs["source_id"],
            kwargs["url"],
            kwargs["duration"],
            kwargs["level_id"],
            kwargs["price"],
            kwargs["price_other"],
            kwargs["url"],
            kwargs["source_couse_id"],
            kwargs["source_id"],
            kwargs["url"],
            kwargs["duration"],
            kwargs["level_id"],
            kwargs["price"],
            kwargs["price_other"],
        )

        self.cur.execute(SQL, data)
        self.connection.commit()

    """Всталяет или обновляет запись в таблице course_raw БД, если переданный course_id совпадает, то обновляет 

    Args:
        self                    (DatabaseQueries): экземпляр класса
        kwargs["course_id"]     (int): id курса в таблице course_metadata
        kwargs["title"]         (str): название
        kwargs["section_title"] (str): направления
        kwargs["preview"]       (str): превью
        kwargs["description"]   (int): описание
        kwargs["program"]       (int): программа

    Returns:
        None
    """
    def insertOrUpdateIntoCourseRaw(self, **kwargs):
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

    """Всталяет отзыв в таблицу reviews БД, если данная запись не существует 

    Args:
        self                (DatabaseQueries): экземпляр класса
        kwargs["course_id"] (int): id курса в таблице course_metadata
        kwargs["text"]      (str): текст отзыва
        kwargs["author"]    (str): ФИО автора

    Returns:
        None
    """
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

    """Удаляет записи из таблицы course_metada по id 

    Args:
        self      (DatabaseQueries): экземпляр класса
        courseIds ([int]): id курсов в таблице course_metadata

    Returns:
        None
    """
    def deleteIn(self, courseIds):
        print(courseIds)
        SQL = "DELETE FROM course_metadata WHERE id IN %(list_course)s"

        self.cur.execute(
            SQL,
            {"list_course": tuple(courseIds)},
        )

        self.connection.commit()

    """Откатывает изменения 

    Args:
        self      (DatabaseQueries): экземпляр класса
        courseIds ([int]): id курсов в таблице course_metadata

    Returns:
        None
    """
    def rollback(self):
        self.connection.rollback()
