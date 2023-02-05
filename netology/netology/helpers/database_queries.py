import psycopg2
from .clear import clear


class DatabaseQueries:
    def __init__(self, hostname, username, password, dbname):
        try:
            self.connection = psycopg2.connect(
                host=hostname, user=username, password=password, dbname=dbname
            )
            self.cur = self.connection.cursor()
            print("open database connection")
        except Exception:
            print("error database connection")

    def __del__(self):
        if self.cur is not None:
            self.cur.close()
            self.connection.close()
            print("close database connection")

    def getSourceId(self, source):
        SQL = """SELECT id FROM source
        WHERE url ILIKE %s"""

        self.cur.execute(SQL, [source])

        return self.cur.fetchone()[0]

    def getCourseMetadataIds(self):
        SQL = """SELECT id, source_couse_id FROM course_metadata"""

        self.cur.execute(SQL)

        return self.cur.fetchall()

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
        self.connection.commit()

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

    def deleteIn(self, courseIds):
        print(courseIds)
        SQL = "DELETE FROM course_metadata WHERE id IN %(list_course)s"
        
        self.cur.execute(
            SQL,
            {"list_course": tuple(courseIds)},
        )
        
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()
