import requests
import logger
from bot.core.decoder import Decoder
from bot.core.config import Config

class Flipax():

    MAIN = 'https://www.flipax.net'

    FLIPAX_PASSWORD = Config.getConfig()["FLIPAX_PASSWORD"]
    FLIPAX_USERNAME = Config.getConfig()["FLIPAX_USERNAME"]

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:54.0) Gecko/20100101 Firefox/58.0','Connection': 'keep-alive'}

    session = ''

    @staticmethod
    def login():
        Flipax.session = requests.get(Flipax.MAIN).cookies
        logger.debug("Cookie %s"%str(Flipax.session))
        response = requests.post(Flipax.MAIN+"/login",data={
            'username':Flipax.FLIPAX_USERNAME,
            'password':Flipax.FLIPAX_PASSWORD,
            'autologin':'on',
            'redirect':'',
            'query':'',
            'login':'Conectarse',
        })
        logger.debug(str(response))

    @staticmethod
    def extractSection(link):
        logger.debug("found link!")
        html = requests.get(link, headers=Flipax.headers, cookies=Flipax.session, verify=True).text
        elements = []
        found = False
        for block in html.split('<ul class="topiclist topics bg_none">'):
            i=0
            for field in block.split('<li class="row '):
                if i>0:
                    element = {}
                    title = Decoder.extract('class="topictitle"','</a>',field)
                    title = title[title.find(">")+1:]
                    link = Flipax.MAIN+Decoder.extract(' href="','"',field)
                    element["title"] = title
                    element["link"] = link
                    logger.debug(title+'.-.'+link)
                    if len(title)>0 and len(content)==0:
                        elements.append(element)
                    elif content in element["title"]:
                        logger.debug("found link: %s"%content)
                        link = element["link"]
                        logger.debug("link is :%s"%link)
                        found = True
                        break
                    else:
                        logger.debug("not found: %s|%s"%(content,element["title"]))
                i+=1
        return link

    @staticmethod
    def extractLinks(link):
        html = requests.get(link, headers=Flipax.headers,cookies=Flipax.session, verify=True).text
        section = Decoder.extract('<div class="postbody"><div class="content"><div><div align="center">','</div></div></div>',html)
        logger.debug("html is: %s"%section)
        for link in section.split('target="_blank" rel="nofollow">'):
            link = link[:link.find('<')]
            element = {}
            element["title"] = link
            element["link"] = link
            elements.append(element)

    @staticmethod
    def extractSections():
        logger.debug("Using session %s "%str(Flipax.session))
        html = requests.get(Flipax.MAIN, headers=Flipax.headers, cookies=Flipax.session, verify=True).text
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
                    if len(title)>0:
                        elements.append(element)
                i+=1

        return elements

    @staticmethod
    def getSection(section='', content=''):
        elements = []

        if Flipax.session == '' and content != '':
            Flipax.login()

        elements = Flipax.extractSections()
        if len(section)>0:
            link = ''
            for element in elements:
                logger.debug(element["title"])
                if element["title"].lower() == section.lower():
                    link = element["link"]
                    break
            if len(link)>0:
                link2 = Flipax.extractSection(link)
                if link2 != link:
                    elements = Flipax.extractLinks(link2)
        return elements
