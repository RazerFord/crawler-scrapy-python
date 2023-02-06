# crawler-scrapy-python
`Crawler` на `Python` с помощью библиотеки `Scrapy`

# Netology API
|URL                                                  |Параметры|Пример|Описание |
|-----------------------------------------------------|---------|------|---------|
|`https://netology.ru/backend/api/programs`           |         |      |Краткая информация о всех курсах|
|`https://netology.ru/backend/api/page_contents/{name}`| `name` - имя курса|`qa`|Подробная информация о каждом курсе|


# Запустить паука
> `scrapy runspider ./netology/netology/spiders/programs.py -o prog.csv`
> Из папки `netology` написать в консоли `scrapy crawl programs`
