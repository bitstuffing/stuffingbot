import requests
import logger
from bot.core.decoder import Decoder
from bot.core.config import Config

class Flipax():

    MAIN = 'https://www.flipax.com/'

    FLIPAX_PASSWORD = Config.getConfig()["FLIPAX_PASSWORD"]
    FLIPAX_USERNAME = Config.getConfig()["FLIPAX_USERNAME"]

    session = ''

    @staticmethod
    def getSection(section):
        if Flipax.session == '':
            Flipax.session = requests.get(Flipax.MAIN)['headers']['Cookie']
            logger.debug("Cookie %s"%Flipax.session)
            request.post(Flipax.MAIN+"login",data={
                'username':Flipax.FLIPAX_USERNAME,
                'password':Flipax.FLIPAX_PASSWORD,
                'autologin':'on',
                'redirect':'',
                'query':'',
                'login':'Conectarse',
            })
        session = Exvagos.session
        logger.debug("Using session %s "%str(session))
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:54.0) Gecko/20100101 Firefox/58.0','Connection': 'keep-alive','Cookie':session}
        html = requests.get(Exvagos.MAIN, headers=headers, verify=True).text
        elements = []
        for block in html.split('<ul class="topiclist forums">'):
            i=0
            for field in block.split('<li class="row">'):
                if i>0:
                    element = {}
                    title = Decoder.rExtract('>','</a>',field)
                    link = Flipax.MAIN+'showthread.php?t='+Decoder.extract('a href="','"',field)
                    element["title"] = title
                    element["link"] = link
                    elements.append(element)
                i+=1
        return elements
