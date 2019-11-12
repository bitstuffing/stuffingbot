import requests
import logger
from bot.core.decoder import Decoder
from bot.core.config import Config

class Flipax():

    MAIN = 'https://www.flipax.net/'

    FLIPAX_PASSWORD = Config.getConfig()["FLIPAX_PASSWORD"]
    FLIPAX_USERNAME = Config.getConfig()["FLIPAX_USERNAME"]

    session = ''

    @staticmethod
    def getSection(section):
        if Flipax.session == '':
            Flipax.session = requests.get(Flipax.MAIN).cookies
            logger.debug("Cookie %s"%str(Flipax.session))
            requests.post(Flipax.MAIN+"login",data={
                'username':Flipax.FLIPAX_USERNAME,
                'password':Flipax.FLIPAX_PASSWORD,
                'autologin':'on',
                'redirect':'',
                'query':'',
                'login':'Conectarse',
            })
        
        session = Flipax.session
        logger.debug("Using session %s "%str(session))
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:54.0) Gecko/20100101 Firefox/58.0','Connection': 'keep-alive'}
        html = requests.get(Flipax.MAIN, headers=headers, cookies=session, verify=True).text
        elements = []
        for block in html.split('<ul class="topiclist forums">'):
            i=0
            for field in block.split('<li class="row">'):
                if i>0:
                    element = {}
                    title = Decoder.extract('class="forumtitle">','</a>',field)
                    link = Flipax.MAIN+Decoder.extract('a href="','"',field)
                    element["title"] = title
                    element["link"] = link
                    logger.debug(title+'.-.'+link)
                    elements.append(element)
                i+=1
        return elements
