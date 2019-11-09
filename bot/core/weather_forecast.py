from bot.core.config import Config
from bot.core.decoder import Decoder
import logger
import requests
import json

config = Config.getConfig()
ACUWEATHER_API = config["ACUWEATHER_API"]

class WeatherForecast():

    API_CITY = "https://api.accuweather.com/locations/v1/cities/autocomplete?q=%s&apikey=%s&language=es&get_param=value"
    HTML_FORECAST = "https://www.accuweather.com/es/es/%s/%s/%s/%s"

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
        #logger.debug("html is: %s"%htmlWeather)
        tableWeather = Decoder.extract('var dailyForecast = ','];',htmlWeather)+"]"
        logger.debug("json is: %s"%tableWeather)
        jsonWeather = json.loads(tableWeather)
        forecast = []
        for fieldWeather in jsonWeather:
            weather = {}
            day = fieldWeather["lDOW"]
            date = fieldWeather["date"]
            max = fieldWeather["day"]["temp"]
            min = fieldWeather["night"]["temp"]
            summary = fieldWeather["day"]["longPhrase"]
            weather["day"] = day
            weather["date"] = date
            weather["max"] = max
            weather["min"] = min
            weather["summary"] = summary
            forecast.append(weather)

        return forecast
