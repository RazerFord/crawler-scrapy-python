# crawler-scrapy-python
`Crawler` на `Python` с помощью библиотеки `Scrapy`

## Netology API
|URL                                                   |Параметры         |Описание                           |
|------------------------------------------------------|------------------|-----------------------------------|
|`https://netology.ru/backend/api/programs`            |                  |Краткая информация о всех курсах   |
|`https://netology.ru/backend/api/page_contents/{name}`|`name` - имя курса|Подробная информация о каждом курсе|

|Пример                                            |Описание                    |
|--------------------------------------------------|----------------------------|
|`https://netology.ru/backend/api/page_contents/qa`|Подробная информация о курсе|


## Запуск `Crawler`
Достаточно запустить контейнер командой `docker-compose up -d`

## Управление расписанием работы `Crawler`
В файле `docker-compose.yml` в `environment` контейнера `app` добавить параметр `EXACT_TIME` или `TIME_BREAK`.

> `EXACT_TIME=00:27` - запускать `Crawler` в определенное время

> `TIME_BREAK=1000` - запускать `Crawler` каждые `1000` секунд

## Ручной запуск парсера

> `scrapy runspider ./netology/netology/spiders/programs.py -o prog.csv`

> Из папки `netology` в консоли написать `scrapy crawl programs`
