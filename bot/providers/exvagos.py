import requests
from alfa.lib import cloudscraper
import logger
from bot.core.decoder import Decoder
import re

class Exvagos():

    MAIN = 'https://www.exvagos2.com/'
    session = ''

    @staticmethod
    def getSection(section):
        if Exvagos.session == '':
            Exvagos.session = cloudscraper.create_scraper()
        session = Exvagos.session
        logger.debug("Using session %s "%str(session))
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0','Connection': 'keep-alive'}
        html = session.get(Exvagos.MAIN, headers=headers, verify=True).text
        link = Exvagos.MAIN+Decoder.rExtract('<a href="','">'+section+"<",html)
        html = session.get(link, headers=headers, verify=True).text
        table = Decoder.extract('<td class="thead" colspan="7">&nbsp;</td>',"</tbody>",html)
        i=0
        elements = []
        for field in table.split('<td class="alt2" align="center" valign="middle">'):
            if i>0:
                element = {}
                if 'style="color:navy;">' in field:
                    title = Decoder.extract('style="color:navy;">','</a>',field)
                else:
                    title = Decoder.extract('style="color:;">','</a>',field)
                link = Exvagos.MAIN+'showthread.php?t='+Decoder.extract('a href="showthread.php?t=','"',field)
                element["title"] = re.sub(r'\W+', ' ', title)#str(title.encode('utf-8','ignore'))
                element["link"] = link
                elements.append(element)
            i+=1
        return elements
