import requests
import urllib
import logger
from bot.core.config import Config

TOKEN = Config.getConfig()["TOKEN_WITAI"]

class Witai():

    cookies = ''

    API = 'https://api.wit.ai/message?explain=true&junk=true&v=20190814&q='
    HEADERS = {
        'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
        'Accept' : '*/*',
        'Accept-Language' : 'es-ES,es;q=0.5',
        'Refeerer' : 'https://wit.ai/',
        'Origin' : 'https://wit.ai',
        'Connection' : 'keep-alive',
        'Authorization' : 'Bearer %s'%TOKEN
    }

    @staticmethod
    def query(text):
        query = urllib.quote_plus(text)
        logger.debug("query: %s" % query)
        response = requests.get(url=Witai.API+query,headers=Witai.HEADERS)
        logger.debug(response.text)
        return response.text
