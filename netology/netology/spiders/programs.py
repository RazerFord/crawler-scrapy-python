import scrapy
import json
from netology.items import NetologyItem

class ProgramsSpider(scrapy.Spider):
    name = "programs"
    allowed_domains = ["netology.ru"]
    start_urls = ["https://netology.ru/backend/api/programs"]

    headers = {
        """
        GET /backend/api/programs HTTP/2
        Host: netology.ru
        User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0
        Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
        Accept-Language: ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3
        Accept-Encoding: gzip, deflate, br
        Connection: keep-alive
        Cookie: _trq=; _trf=www.google.com; _tru=netology.ru%2Fblog%2Fbot-php1; _gcl_au=1.1.279139913.1667246532; mindboxDeviceUUID=12c248b6-697f-4575-bc7d-c34e0d9ba345; directCrm-session=%7B%22deviceGuid%22%3A%2212c248b6-697f-4575-bc7d-c34e0d9ba345%22%7D; _tm_lt_sid=1667246532072.186963; _ga=GA1.2.495666537.1667246532; _ym_uid=1667246532856676513; _ym_d=1667246532; _tt_enable_cookie=1; _ttp=07707991-5276-406d-8fe0-f1f160fcb275; popmechanic_sbjs_migrations=popmechanic_1418474375998%3D1%7C%7C%7C1471519752600%3D1%7C%7C%7C1471519752605%3D1; advcake_trackid=93b07881-3b2d-349d-6ec2-201aa35e3c59; advcake_session_id=d1e10264-1549-4960-0f10-40cfb1b0b98e; cto_bundle=8JLh419ra1pKSCUyQkZLOUg0UndZMHU1WjQ3Y0d0WUlEaGVuRzclMkJmSkV3NHRWdlpNZDZOM2h1MmVHQSUyQkJRaXJDWlpGcjVoWTA4cFpXYnEwWWFuS1JLQm9RZE1ycTJqWjNhJTJGeVRJcGV5cHQwZlYzN0kwSGtWRlU1TkdCOGpIZTdOaVJSajZoRzJYdEVoMGEyMGRBQVpLczhVZ3hzZyUzRCUzRA; gdeslon.ru.__arc_domain=gdeslon.ru; gdeslon.ru.user_id=cc8c299c-cd3e-46f2-a514-cc045a640cb0; tmr_reqNum=192; tmr_lvid=62fbac450b382270dd8528590fb414ac; tmr_lvidTS=1667246533711; flocktory-uuid=f9f8a964-f99f-46c4-a4eb-106c5d964998-1; adrcid=AAJgELNY1aETJABhmOVGC2A; _fbp=fb.1.1667246534745.1815894366; rees46_device_id=9If4DacWix; g4c_x=1; _ym_isad=2; _gid=GA1.2.634806718.1668755821; current_path=/navigation; tmr_detect=0%7C1668767474162; _gaexp=GAX1.2.bmtwj7gJR3aUrC7L4wXL1A.19375.1!ethjBZ_EQI20yOCeI2rN2w.19403.0!BAX8UBAxTIav2cEQRoRztg.19383.1; rees46_session_code=ahZ6quOeQH; rees46_session_last_act=1668764184257; rees46_lazy_recommenders=true; consultation_modal_shown=1; PHPSESSID=78tfhmt485egovcfu33pdmkf77; source_data=%5B%7B%22pid%22%3A%22%22%2C%22utm_source%22%3A%22%22%2C%22utm_medium%22%3A%22%22%2C%22utm_campaign%22%3A%22%22%2C%22utm_content%22%3A%22%22%2C%22utm_term%22%3A%22%22%2C%22timestamp%22%3A1668756468%7D%5D; referer=https%3A%2F%2Fwww.google.com%2F; actionBanner__179=true; _ym_visorc=w
        Upgrade-Insecure-Requests: 1
        Sec-Fetch-Dest: document
        Sec-Fetch-Mode: navigate
        Sec-Fetch-Site: none
        Sec-Fetch-User: ?1
        TE: trailers
        """
    }

    def parse(self, response):
        print(response)
        raw_data = response.body
        data = json.loads(raw_data)
        for program in data:
            item = NetologyItem()
            item['program_id'] = program["id"] 
            item['program_name'] = program["name"] 
            item['program_url'] = "https:" + program["url"] 
            yield item
