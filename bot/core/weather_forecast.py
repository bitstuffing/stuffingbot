from bot.core.config import Config
from bot.core.decoder import Decoder
import logger
import requests
import json

config = Config.getConfig()
ACUWEATHER_API = config["ACUWEATHER_API"]

class WeatherForecast():

    API_CITY = "https://api.accuweather.com/locations/v1/cities/autocomplete?q=%s&apikey=%s&language=es&get_param=value"
    HTML_FORECAST = "https://www.accuweather.com/es/es/%s/%s/%s/%s?day=1"

    HEADERS = {
        'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language' : 'es-ES,es;q=0.5',
        'Referer': 'https://www.accuweather.com/'
    }

    @staticmethod
    def getWeather(place):
        city = place.replace(" ","+")
        preparedUrl = WeatherForecast.API_CITY%(city,ACUWEATHER_API)
        logger.debug("prepared1 %s"%preparedUrl)
        jsonApi = requests.get(url=preparedUrl,headers=WeatherForecast.HEADERS).text
        logger.debug("json: %s"%jsonApi)
        jsonLoaded = json.loads(jsonApi)
        cityCode = jsonLoaded[0]["Key"]
        cityName = jsonLoaded[0]["LocalizedName"].lower().replace(" ","-")

        command = 'daily-weather-forecast' #weather-forecast, current-weather
        preparedUrl = WeatherForecast.HTML_FORECAST%(cityName,cityCode,command,cityCode)
        logger.debug("prepared2 %s"%preparedUrl)
        htmlWeather = requests.get(url=preparedUrl,headers=WeatherForecast.HEADERS).text
        tableWeather = Decoder.extract('<!-- /.feed-controls -->','<!-- /.feed-tabs -->',htmlWeather)
        i=0
        forecast = []
        for fieldWeather in tableWeather.split('<div class="bg bg-su">'):
            if i>0:
                weather = {}
                day = Decoder.extract('<h3><a href="#">','</a></h3>',fieldWeather)
                date = Decoder.extract('<h4>','</h4>',fieldWeather)
                max = Decoder.extract('<span class="large-temp">','</span>',fieldWeather).replace("/","")
                min = Decoder.extract('<span class="small-temp">','</span>',fieldWeather).replace("/","")
                summary = Decoder.extract('<span class="cond">','</span>',fieldWeather)
                weather["day"] = day
                weather["date"] = date
                weather["max"] = max
                weather["min"] = min
                weather["summary"] = summary
                forecast.append(weather)
            i+=1

        return forecast
