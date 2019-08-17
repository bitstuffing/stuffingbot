import requests
from bot.core.decoder import Decoder
import urllib
import logger

class KickAssTorrent():

    URL = 'https://kickasstorrents.to'
    SEARCH = 'https://kickasstorrents.to/usearch/%s/'

    @staticmethod
    def getPage(page=''):
        if page == '':
            page = KickAssTorrent.URL
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0','Connection': 'keep-alive'}
        html = requests.get(page, headers=headers, verify=True).text
        return html

    @staticmethod
    def getLinksFromHtml(html):
        table = Decoder.extract('<table cellpadding="0" cellspacing="0" class="data frontPageWidget" style="width: 100%">','</table>',html)
        i=0
        links = []
        for field in table.split('<div class="markeredBlock torType filmType">'):
            if i>0:
                link = {}
                logger.debug(field)
                href = Decoder.extract('href="','"',field)
                title = Decoder.extract('">','</a>',field)
                link["title"] = title
                if "://" not in href:
                    href = KickAssTorrent.URL+href
                link["link"] = href
                links.append(link)
            i+=1
        return links

    @staticmethod
    def getMagnetFromLink(link):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0','Connection': 'keep-alive'}
        html = requests.get(page, headers=headers, verify=True).text
        link = Decoder.extract('title="Magnet link" href="','"',html)
        return link

    @staticmethod
    def search(term):
        searchUrl = KickAssTorrent.SEARCH % urllib.parse.quote(term)
        html = KickAssTorrent.getPage(searchUrl)
        return KickAssTorrent.getLinksFromHtml(html)
