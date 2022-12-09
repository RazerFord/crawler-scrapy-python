FROM postgres:15.1
ENV POSTGRES_PASSWORD=postgres
ENV POSTGRES_USER=postgres
ENV POSTGRES_DB=netology
COPY create_fixtures.sql /docker-entrypoint-initdb.d/create_fixtures.sql
