import logging
import sys
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from content import Content
import time
from datetime import datetime
import os
import json
import logger
from bot.core.config import Config

TOKEN = Config.getConfig()["TOKEN"]
DOWNLOAD_PATH = Config.getConfig()["DOWNLOAD_PATH"]
bot = telegram.Bot(TOKEN)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    context.message.reply_text('Bienvenido.\nPara solicitar ayuda escriba /help')


def help(update, context):
    """Send a message when the command /help is issued."""
    context.message.reply_text('Listado de comandos:\n/decode (link)\n/exvagos (seccion)\n/habla (frase)\n/torrent (url)\n/pronostico (ciudad)')

def echo(update, context):
    """Echo the user message."""
    logger.debug("UPDATE: %s"%str(update))
    logger.debug("CONTEXT: %s"%str(context))
    message = "No message"
    try:
        message = context.message.text
    except:
        logger.error("no message in context")
    context.message.reply_text("echo: %s"%message)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.error('Update "%s" caused error "%s"', update, context.error)

def decode(update,context):
    message = context.message.text
    params = message.split(" ")
    logger.debug("request: %s"%message)
    text = Content.decodeWithImportedEngine(targetUrl=params[1])
    logger.debug('response: %s'%text)
    context.message.reply_text(text)

def exvagos(update,context):
    message = context.message.text
    params = message.split(" ")
    logger.debug("request: %s"%message)
    text = Content.getExvagos(params)
    logger.debug('response: %s'%text)
    context.message.reply_text(text)

def habla(update,context):
    message = context.message.text
    params = message.split(" ")
    logger.debug("request: %s"%message)
    chatId = context.message.chat.id
    text = Content.speech(params,bot,chatId)
    logger.debug('response: %s'%text)
    context.message.reply_text(text)

def torrent(update,context):
    message = context.message.text
    chatId = context.message.chat.id
    params = message.split(" ")
    logger.debug("request: %s"%message)
    if '.torrent' in params[1] or 'magnet:' in params[1]:
        text = str(Content.downloadTorrent(params,bot,chatId))
    else:
        command = params[1]
        id = None
        if len(params)>2:
            id = params[2]
        if command=="delete":
            text = Content.deleteTorrent(id,delete=True)
        elif command == "remove":
            text = Content.deleteTorrent(id,delete=False)
        elif command == "pause":
            text = Content.pauseTorrent(id)
        elif command=="resume":
            text = Content.resumeTorrent(id)
        elif command == "status":
            text = Content.status(id)
    context.message.reply_text(text)
    logger.debug('response: %s'%text)

def got_file(bot, update):
    """Handle files. Code by https://pbaumgarten.com/python/telegram/"""
    global folder  # eg, folder = "downloads/"
    file_id = None
    bot = None
    # user object contains {'first_name':, 'is_bot':, 'id':, 'language_code':}
    # username: is optional, thus by default None!
    sender = update.message.from_user.first_name + " (" + str(update.message.from_user.id) + ")"
    voice = False
    if update.message.audio:
        voice = True
        logger.debug(sender + ": Sent an audio message")
        file_id = update.message.audio.file_id
        bot = update.message.audio.bot
    elif update.message.document:
        logger.debug(sender + ": Sent a document")
        file_id = update.message.document.file_id
        bot = update.message.document.bot
    elif update.message.photo:
        logger.debug(sender + ": Sent a photo")
        file_id = update.message.photo[-1].file_id
        bot = update.message.photo[-1].bot
    elif update.message.video:
        logger.debug(sender + ": Sent a video")
        file_id = update.message.video.file_id
        bot = update.message.video.bot
    elif update.message.video_note:
        logger.debug(sender + ": Sent a video note")
        file_id = update.message.video_note.file_id
        bot = update.message.video_note.bot
    elif update.message.voice:
        voice = True
        logger.debug(sender + ": Sent a voice message")
        file_id = update.message.voice.file_id
        bot = update.message.voice.bot
    if file_id and bot:
        new_file = bot.get_file(file_id)
        extension = new_file.file_path.split(".")[-1]  # get file extension of received file
        datetime_str = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        file_name = DOWNLOAD_PATH + datetime_str + "-" + str(update.message.chat_id) + "." + extension
        new_file.download(file_name)
        logger.debug("Downloaded file: {}".format(file_name))
        if voice:
            logger.debug("voice detected, launching transcription service...")
            text = Content.transcribe(file_name) #TODO: json -> results[0].alternative[0].transcript
            jsonLoaded = json.loads(text)
            text = ""
            for content in jsonLoaded["results"]:
                text += content["alternatives"][0]["transcript"]+"\n"
            logger.debug("returned text: %s"%text)
            update.message.reply_text(text)
    else:
        logger.debug("Unable to download file")

def pronostico(update,context):
    message = context.message.text
    chatId = context.message.chat.id
    params = message.split(" ")
    logger.debug("request: %s"%message)
    message = message[message.find(" ")+1:]
    text = Content.weather(message)

    context.message.reply_text(text)
    logger.debug("response: %s"%text)


def main():
    logger.info("Initting bot...")
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    updater.dispatcher.add_handler(MessageHandler(Filters.audio, got_file))
    updater.dispatcher.add_handler(MessageHandler(Filters.document, got_file))
    updater.dispatcher.add_handler(MessageHandler(Filters.photo, got_file))
    updater.dispatcher.add_handler(MessageHandler(Filters.voice, got_file))
    updater.dispatcher.add_handler(MessageHandler(Filters.video, got_file))
    updater.dispatcher.add_handler(MessageHandler(Filters.video_note, got_file))

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    #start old commands migration
    dp.add_handler(CommandHandler("decode", decode))
    dp.add_handler(CommandHandler("exvagos", exvagos))
    dp.add_handler(CommandHandler("habla", habla))
    dp.add_handler(CommandHandler("torrent", torrent))
    dp.add_handler(CommandHandler("pronostico", pronostico))
    #end old commands migration

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
