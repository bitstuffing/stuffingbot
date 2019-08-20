import logger
import requests
import cfscrape
import re
import time
import os
import subprocess #syscalls
from pytg import Telegram
from bot.core.config import Config
from bot.providers.exvagos import Exvagos
from bot.providers.witai import Witai
#from google_speech import Speech #has been ported to python2 and appended
from bot.core.torrent import Torrent
from bot.providers.kat import KickAssTorrent

from bot.core.decoder import Decoder
from bot.core.speech_to_text_v1 import SpeechToText
from bot.core.weather_forecast import WeatherForecast
import urllib

session = requests.session()
scraper = cfscrape.create_scraper(sess=session)

config = Config.getConfig()
DOWNLOAD_PATH = config["DOWNLOAD_PATH"]
HTTP_URI = config["HTTP_URI"]
TELEGRAM_CLI = config["TELEGRAM_CLI"]
BOT_NAME = config["BOT_NAME"]
DOWNLOAD_SPEECH = eval(config["DOWNLOAD_SPEECH"])

HEADERS = {
    'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
    'Accept' : '*/*',
    'Accept-Language' : 'es-ES,es;q=0.5'
}

class Content():

    @staticmethod
    def weather(city):
        response = WeatherForecast.getWeather(city)
        content = ""
        for line in response:
            parse = "%s %s Temp: %s %s - %s\n" % (str(line["date"]),str(line["day"]),str(line["min"]).replace('&deg;',' '),str(line["max"]).replace('&deg;',' '),str(line["summary"]).replace("&#243;","o"))
            logger.debug(parse)
            content += parse
        return content

    @staticmethod
    def transcribe(path):
        text = "None"
        speech = SpeechToText()
        extension = path[len(path)-4:]
        if ".mp3" == extension:
            path = Decoder.mp3ToWav(path)
        elif ".oga" == extension or ".ogg" == extension:
            path = Decoder.oggToWav(path)
        text = speech.transcribe(path)
        return text

    @staticmethod
    def searchKat(params,bot,chatId):
        term = params[2]
        entries = KickAssTorrent.search(term)
        text = ""
        for entry in entries:
            logger.debug(entry["title"])
            text+=entry["title"]+"\n"
        return text

    @staticmethod
    def deleteTorrent(id,delete=False):
        torrent = Torrent()
        status = torrent.delete(id,delete)
        return str(status)

    @staticmethod
    def pauseTorrent(id):
        torrent = Torrent()
        status = torrent.pause(id)
        return str(status)

    @staticmethod
    def resumeTorrent(id):
        torrent = Torrent()
        status = torrent.resume(id)
        return str(status)

    @staticmethod
    def status(id=None):
        torrent = Torrent()
        list = []
        if id is not None:
            status = torrent.status(id)
            list.append(status)
        else:
            list = torrent.allStatus()
        message = ""
        for status in list:
            logger.debug(str(dir(status)))
            seeders = 0
            try:
                seeders = status.seeders
            except:
                pass
            percent = 0
            try:
                percent = status.percentDone
            except:
                pass
            if status.totalSize>1073741824:
                size = "{0:.2f} GB".format(status.totalSize/1073741824)
            elif status.totalSize>1048576:
                size = "{0:.2f} MB".format(status.totalSize/1048576)
            elif status.totalSize>1024:
                size = "{0:.2f} KB".format(status.totalSize/1024)
            else:
                size = status.totalSize
            message += "%s :: %.0f%% P: %s S: %s Size: %s :T: %s \n"%(status.id,(percent*100),len(status.peers),seeders,size,status.name)
        return message

    @staticmethod
    def downloadTorrent(params,bot,chatId):
        torrentUrl = params[1]
        torrent = Torrent()
        status = torrent.add(torrentUrl)
        bot.sendMessage(chat_id=chatId,text="torrent %s with id %s."%(status.name,status.id))
        return status.id

    @staticmethod
    def getExvagos(params):
        entries = Exvagos.getSection(params[1])
        text = ""
        for entry in entries:
            logger.debug(entry["title"])
            text+=entry["title"]+"\n"
        return text

    @staticmethod
    def decodeWithImportedEngine(targetUrl):
        logger.debug("started import...")
        from alfa.core.servertools import get_servers_list, get_server_parameters
        from alfa.platformcode import config
        logger.debug("finished import!")
        finalLink = ""
        links = []
        if len(str(targetUrl)) > 0:
            for serverid in get_servers_list().keys():
                server_parameters = get_server_parameters(serverid)
                for pattern in server_parameters.get("find_videos", {}).get("patterns", []):
                    for match in re.compile(pattern["pattern"], re.DOTALL).finditer(targetUrl):
                        url = pattern["url"]
                        for x in range(len(match.groups())):
                            url = url.replace("\\%s" % (x + 1), match.groups()[x])
                            logger.debug("brute url is %s "%url)
                            #first call test_video_exists
                            scriptToInvoke = __import__("alfa.servers." + serverid, globals(), locals(),["test_video_exists"], 0)
                            logger.debug("Exists: %s"%str(scriptToInvoke))
                            #next call get_video_url
                            scriptToInvoke = __import__("alfa.servers." + serverid, globals(), locals(),["get_video_url"], 0)
                            logger.debug(str(scriptToInvoke))
                            links = scriptToInvoke.get_video_url(page_url=url)
        try:
            logger.debug(str(links))
            for link in links:
                if (str(type(link) == list)):
                    for linkC in link:
                        if "http" in linkC:
                            logger.debug("found link %s" % linkC)
                            finalLink = linkC
        except Exception as ex:
            if len(finalLink) == 0:
                finalLink = targetUrl
            logger.error(str(ex))
            logger.debug("link will be %s" % finalLink)
            pass
        return finalLink

    @staticmethod
    def downloadVideo(text):
        headers = {}
        url = text
        logger.debug("decoding text to download... %s" % text)
        if "|" in text:
            url = text[:text.find("|")]
            header = text[text.find("|")+1:]
            key = header[:header.find("=")]
            value = header[header.find("=")+1]
            headers[key] = value
        #bot.sendMessage(chat_id=chatId,text="downloading...")
        logger.debug("downloading with headers: %s"%str(headers))
        r = requests.get(url=url,headers=headers,stream=True)
        videoFile = "video_"+str(time.time())+".mp4"
        with open(DOWNLOAD_PATH+videoFile, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)
        logger.debug("download finished, trying to upload...")
        size = os.path.getsize(DOWNLOAD_PATH+videoFile)
        size = long(size)/1024/1024
        if size>50:
            #bot.sendMessage(chat_id=chatId,text="not uploading video with bot, is too big (limited to 50 MB) %s MB sized, access with next url:"% str(size))
            #bot.sendMessage(chat_id=chatId,text="%s%s"%(HTTP_URI,videoFile))
            #bot.sendMessage(chat_id=chatId,text="uploading with telegram-cli... %s" % (DOWNLOAD_PATH+videoFile))
            bashCommand = '(sleep 1;echo "dialog_list";sleep 2; echo "send_file %s \'%s\'") | %s -W -v -k server.pub' % (BOT_NAME,DOWNLOAD_PATH+videoFile,TELEGRAM_CLI)
            #bot.sendMessage(chat_id=chatId,text=bashCommand)
            #os.popen(bashCommand).read() #launch the command quiet (sync)
            return_code = subprocess.call(bashCommand,shell=True) #launch the command and shows output in main console (sync)
            #bot.sendMessage(chat_id=chatId,text="upload has finished")
        else:
            pass
            #bot.sendMessage(chat_id=chatId,text="uploading with bot... %s MB sized"% str(size))
            #bot.sendChatAction(chatId, 'upload_video')
            #bot.sendVideo(chatId,open(DOWNLOAD_PATH+videoFile,'rb'))

    @staticmethod
    def speech(params,bot,chatId,lang='es'):
        text = " ".join(params[1:])
        #speech = Speech(text, lang=lang)
        audioFile = "audio_"+str(time.time())+".mp3"
        #logger.debug("self url: %s"%str(dir(speech)))
        #speech.save(DOWNLOAD_PATH+audioFile)
        logger.debug(str(dir(urllib)))
        urlText = urllib.quote_plus(text)
        url = 'https://translate.google.com/translate_tts?client=tw-ob&ie=UTF-8&idx=0&total=1&textlen=%s&tl=%s&q=%s'%(len(text),lang,urlText)
        if DOWNLOAD_SPEECH:
            logger.debug("url: '%s'"%url)
            headers = {}
            r = requests.get(url=url,headers=HEADERS,stream=True)
            filePath = DOWNLOAD_PATH+audioFile
            with open(filePath, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=128):
                    fd.write(chunk)
            size = os.path.getsize(DOWNLOAD_PATH+videoFile)
            size = long(size)/1024/1024
            if size>50:
                bashCommand = '(sleep 1;echo "dialog_list";sleep 2; echo "send_file %s \'%s\'") | %s -W -v -k server.pub' % (BOT_NAME,DOWNLOAD_PATH+audioFile,TELEGRAM_CLI)
                return_code = subprocess.call(bashCommand,shell=True) #launch the command and shows output in main console (sync)
            else:
                try:
                    bot.sendAudio(chat_id=chatId,audio=file(DOWNLOAD_PATH+videoFile,'rb'),title=text,caption=text)
                except Exception as ex:
                    logger.error(str(ex))
        else:
            try:
                bot.sendAudio(chat_id=chatId,audio=url,title=text,caption=text)
            except Exception as ex:
                logger.error(str(ex))
        if DOWNLOAD_SPEECH:
            os.remove(DOWNLOAD_PATH+audioFile)
        return text
