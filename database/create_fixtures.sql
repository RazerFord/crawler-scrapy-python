-- Active: 1671206514827@@localhost@5432@netology@public

CREATE TABLE
    IF NOT EXISTS source (
        id BIGINT PRIMARY KEY,
        url TEXT NOT NULL
    );

INSERT INTO source (id, url)
SELECT 1, 'netology'
WHERE NOT EXISTS (
        SELECT id
        FROM source
        WHERE id = 1
    );

CREATE TABLE
    IF NOT EXISTS level (
        id SERIAL PRIMARY KEY,
        text TEXT NOT NULL
    );

CREATE TABLE
    IF NOT EXISTS course_metadata (
        id SERIAL PRIMARY KEY,
        source_couse_id BIGINT,
        source_id BIGINT REFERENCES source (id) ON UPDATE CASCADE ON DELETE CASCADE,
        url TEXT NOT NULL,
        last_update TIMESTAMP DEFAULT NOW(),
        duration TEXT,
        level_id BIGINT REFERENCES level (id) ON UPDATE CASCADE,
        price NUMERIC DEFAULT 0,
        price_other NUMERIC DEFAULT 0,
        author VARCHAR(255)
    );

CREATE TABLE
    IF NOT EXISTS course_raw (
        id SERIAL PRIMARY KEY,
        course_id BIGINT REFERENCES course_metadata (id) ON UPDATE CASCADE ON DELETE CASCADE,
        title VARCHAR(255) DEFAULT NULL,
        section_title VARCHAR(255) DEFAULT NULL,
        preview TEXT DEFAULT NULL,
        description TEXT DEFAULT NULL,
        program TEXT DEFAULT NULL
    );

CREATE TABLE
    IF NOT EXISTS reviews (
        id SERIAL PRIMARY KEY,
        course_id BIGINT REFERENCES course_metadata (id) ON UPDATE CASCADE ON DELETE CASCADE,
        text TEXT,
        author VARCHAR(255),
        date DATE
    );

-- DROP TABLE IF EXISTS level;

-- DROP TABLE IF EXISTS course_metadata;

-- DROP TABLE IF EXISTS reviews;

-- DROP TABLE IF EXISTS course_raw;

-- DROP TABLE IF EXISTS source;
