-- Active: 1671206514827@@localhost@5432@netology@public

CREATE TABLE
    IF NOT EXISTS source (
        id BIGINT PRIMARY KEY,
        url TEXT NOT NULL
    );

CREATE TABLE
    IF NOT EXISTS level (
        id BIGINT PRIMARY KEY,
        text TEXT NOT NULL
    );

CREATE TABLE
    IF NOT EXISTS course_metadata (
        id BIGINT PRIMARY KEY,
        source_id BIGINT REFERENCES source (id) ON UPDATE CASCADE,
        url TEXT NOT NULL,
        last_update TIMESTAMP NOT NULL,
        duration TEXT,
        level_id BIGINT REFERENCES level (id) ON UPDATE CASCADE,
        price NUMERIC DEFAULT 0,
        price_other NUMERIC DEFAULT 0,
        author VARCHAR(255)
    );

CREATE TABLE
    IF NOT EXISTS course_row (
        id BIGINT PRIMARY KEY,
        course_id BIGINT REFERENCES course_metadata (id) ON UPDATE CASCADE,
        title VARCHAR(255) DEFAULT NULL,
        section_title VARCHAR(255) DEFAULT NULL,
        preview TEXT DEFAULT NULL,
        description TEXT DEFAULT NULL,
        program TEXT DEFAULT NULL
    );

CREATE TABLE
    IF NOT EXISTS reviews (
        id BIGINT PRIMARY KEY,
        course_id BIGINT REFERENCES course_metadata (id) ON UPDATE CASCADE,
        text TEXT,
        author VARCHAR(255),
        date DATE
    );

-- DROP TABLE IF EXISTS level;
-- DROP TABLE IF EXISTS course_metadata;
-- DROP TABLE IF EXISTS reviews;
-- DROP TABLE IF EXISTS course_row;
-- DROP TABLE IF EXISTS source;