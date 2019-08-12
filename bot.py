import logging
import sys
import telepot
from telepot.loop import MessageLoop
from telepot.delegate import pave_event_space, per_chat_id, create_open
from content import Content
import time
import os
import logger
from config import Config

TOKEN = Config.getConfig()["TOKEN"]

logger.info("Initting bot...")

class MessageCounter(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(MessageCounter, self).__init__(*args, **kwargs)
        self._count = 0

    def on_chat_message(self, msg):
        self._count += 1
        logger.debug("Received message: %s" % str(msg))
        text = "working..."
        chatId = msg["chat"]["id"]
        if "text" in msg:
            try:
                text = Content.manageText(msg["text"])
                if ".mp4" in text: #could be a decoded line, needs a download
                    Content.downloadVideo(chatId,text,bot)
            except Exception as e:
                logger.error(str(e))
                bot.sendMessage(chatId, str(e))
        bot.sendMessage(chatId, text)
#        self.sender.sendMessage(self._count) #message for all

bot = telepot.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, MessageCounter, timeout=10),
])
MessageLoop(bot).run_as_thread()

while 1:
    time.sleep(10)
