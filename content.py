import logger
import requests
import cfscrape
import re
import time
import os
import subprocess #syscalls
from pytg import Telegram
from config import Config

session = requests.session()
scraper = cfscrape.create_scraper(sess=session)

config = Config.getConfig()
DOWNLOAD_PATH = config["DOWNLOAD_PATH"]
HTTP_URI = config["HTTP_URI"]
TELEGRAM_CLI = config["TELEGRAM_CLI"]
BOT_NAME = config["BOT_NAME"]

class Content():

    @staticmethod
    def manageText(text):
        #get command/s
        if " " in text:
            params = text.split(" ")
            #continue analysing commands
            switcher = {
                "hola" : Content.greetings
            }
            func = switcher.get(params[0], lambda: "Invalid argument")
            text = func()
            if text == "Invalid argument" and len(params)>1:
                command = params[0]
                if "decode" == command:
                    text = Content.decodeWithImportedEngine(targetUrl=params[1])
        return text

    @staticmethod
    def greetings():
        return "hola"

    @staticmethod
    def decodeWithImportedEngine(targetUrl):
        logger.debug("started import...")
        from alfa.core.servertools import get_servers_list, get_server_parameters
        from alfa.platformcode import config
        logger.debug("finished import!")
        finalLink = ""
        links = []
        if str(len(targetUrl)) > 0:
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
    def downloadVideo(chatId,text,bot):
        headers = {}
        url = text
        logger.debug("decoding text to download... %s" % text)
        if "|" in text:
            url = text[:text.find("|")]
            header = text[text.find("|")+1:]
            key = header[:header.find("=")]
            value = header[header.find("=")+1]
            headers[key] = value
        bot.sendMessage(chatId,"downloading...")
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
            bot.sendMessage(chatId,"not uploading video with bot, is too big (limited to 50 MB) %s MB sized, access with next url:"% str(size))
            bot.sendMessage(chatId,"%s%s"%(HTTP_URI,videoFile))
            bot.sendMessage(chatId,"uploading with telegram-cli... %s" % (DOWNLOAD_PATH+videoFile))
            bashCommand = '(sleep 1;echo "dialog_list";sleep 2; echo "send_file %s \'%s\'") | %s -W -v -k server.pub' % (BOT_NAME,DOWNLOAD_PATH+videoFile,TELEGRAM_CLI)
            bot.sendMessage(chatId,bashCommand)
            #os.popen(bashCommand).read() #launch the command quiet (sync)
            return_code = subprocess.call(bashCommand,shell=True) #launch the command and shows output in main console (sync)
            bot.sendMessage(chatId,"upload has finished")
        else:
            bot.sendMessage(chatId,"uploading with bot... %s MB sized"% str(size))
            bot.sendChatAction(chatId, 'upload_video')
            bot.sendVideo(chatId,open(DOWNLOAD_PATH+videoFile,'rb'))
