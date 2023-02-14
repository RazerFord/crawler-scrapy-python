# crawler-scrapy-python
`Crawler` на `Python` с помощью библиотеки `Scrapy`

## Netology API
|URL                                                   |Параметры         |Описание                               |
|------------------------------------------------------|------------------|---------------------------------------|
|`https://netology.ru/backend/api/programs`            |                  |Краткая информация о всех курсах       |
|`https://netology.ru/backend/api/page_contents/{name}`|`name` - имя курса|Подробная информация о конкретном курсе|

|Пример                                            |Описание                               |
|--------------------------------------------------|---------------------------------------|
|`https://netology.ru/backend/api/page_contents/qa`|Подробная информация о конкретном курсе|

## Запуск `Crawler`
Достаточно запустить контейнер командой `docker-compose up -d`

## Управление расписанием работы `Crawler`
В файле `docker-compose.yml` в `environment` контейнера `app` добавить параметр `EXACT_TIME` или `TIME_BREAK`.


> `EXACT_TIME=00:27` - запускать `Crawler` в определенное время

> `TIME_BREAK=1000` - запускать `Crawler` каждые `1000` секунд

## Отключение записи в БД
### Через контейнер
Для отключения записи в БД необходимо: в файле `docker-compose.yml` в `environment` контейнера `app` параметр `SAVEINDB` изменить на `0`. Чтобы включить запись в БД, то необходимо параметр `SAVEINDB` изменить на `1`.

### Через файл настроек
Найти файл `./netology/netology/settings.py`. В найденном файле найти строки:
```Python
ITEM_PIPELINES = {
    "netology.pipelines.NetologyPipeline": 300,
    "netology.pipelines.DatabasePipeline": 350
    if "SAVEINDB" not in environ or int(environ["SAVEINDB"]) == 1
    else None,
}
```

Изменить на

```Python
ITEM_PIPELINES = {
    "netology.pipelines.NetologyPipeline": 300,
    "netology.pipelines.DatabasePipeline": 350,
}
```
в этом же файле найти параметры подключения к базе данных: `HOSTNAME`, `USERNAME`, `PASSWORD`, `DBNAME` - и закомментировать.

## Ручной запуск парсера

Найти файл `./netology/netology/settings.py`. Найти и изменить параметры подключения к базе данных: `HOSTNAME`, `USERNAME`, `PASSWORD`, `DBNAME`.

Запустить паука одним из следующих способов:

> `scrapy runspider ./netology/netology/spiders/programs.py -o items.csv` - данные сохранится в `csv` и в БД

> `scrapy runspider ./netology/netology/spiders/programs.py -o items.json` - данные сохранится в `json` и в БД

> Из папки `netology` в консоли написать `scrapy crawl programs -o items.csv` - данные сохранится в `csv` и в БД

> Из папки `netology` в консоли написать `scrapy crawl programs -o items.json` - данные сохранится в `json` и в БД
