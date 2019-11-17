# encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import base64
import urllib
import logging
import sys
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram.ext.dispatcher import run_async
from content import Content
import time
from datetime import datetime
import os
import json
import logger
from bot.core.config import Config

config = Config.getConfig()

TOKEN = config["TOKEN"]
DOWNLOAD_PATH = config["DOWNLOAD_PATH"]
HTTP_URI = config["HTTP_URI"]
TELEGRAM_CLI = config["TELEGRAM_CLI"]
BOT_NAME = config["BOT_NAME"]

bot = telegram.Bot(TOKEN)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Bienvenido.\nPara solicitar ayuda escriba /help')

@run_async
def help(update, context):
    text = ('Listado de comandos:'
        '\n/decode (link)'
        '\n/exvagos (seccion)'
        '\n/flipax '
        '\n/habla (frase)'
        '\n/torrent [url|status|remove id|pause id|resume id|delete id]'
        '\n/pronostico (ciudad)')
    update.message.reply_text(text)

@run_async
def echo(update, context):
    telegram.ReplyKeyboardRemove()
    """Echo the user message."""
    logger.debug("UPDATE: %s"%str(update))
    logger.debug("CONTEXT: %s"%str(context))
    message = "No message"
    try:
        message = update.message.text
    except:
        logger.error("no message in context")
    update.message.reply_text("echo: %s"%message)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.error('Update "%s" caused error "%s"', update, context.error)

@run_async
def decode(update,context):
    message = update.message.text
    params = message.split(" ")
    logger.debug("request: %s"%message)
    text = Content.decodeWithImportedEngine(targetUrl=params[1])
    logger.debug('response: %s'%text)
    update.message.reply_text(text)
    Content.downloadVideo(text)

@run_async
def exvagos(update,context):
    message = update.message.text
    params = message.split(" ")
    logger.debug("request: %s"%message)
    text = Content.getExvagos(params)
    logger.debug('response: %s'%text)
    update.message.reply_text(text)

@run_async
def buttons(update,context):
    logger.debug(str(update))
    logger.debug(str(context))
    query = update.callback_query.data
    if " " in query:
        queries = query.split(" ")
        if "/flipax" in queries[0]:
            query = update.callback_query.data
            logger.debug("calling flipax with %s "%query)
            flipax_callback(update,query)

@run_async
def flipax(update,context):
    message = update.message.text

    flipax_callback(update,message)

def flipax_callback(update,message):
    params = []
    if " " in message:
        params.append(message[:message.find(" ")-1])
        if " - " in message[message.find(" ")+1:]:
            logging.debug("message: %s"%message)
            section = message[message.find(" ")+1:].split(" - ")[0]
            content = message[message.find(" ")+1:].split(" - ")[1]
            params.append(section)
            params.append(content)
        else:
            params.append(message[message.find(" ")+1:])
    logger.debug(str(params))
    logger.debug("request: %s"%message)
    entries = Content.getFlipax(params)
    keyboard = []
    for entry in entries:
        text = "/flipax"
        if len(params)<=2:
            text+=" - "+entry["title"]
        else: #if len(params)==3:
            uri = Decoder.extract('.net/','-',entry["url"])
            text+=" url "+uri
        logging.debug("calback"+text)
        title = entry["title"]
        logger.debug("button: %s , callback: %s" % (title,text))
        key = [InlineKeyboardButton(text=title,callback_data=text)] #please take into account that callback_data couldn't be higher than 64 characters
        keyboard.append(key)
    reply_markup = InlineKeyboardMarkup(keyboard,resize_keyboard=True)
    text = 'please select an option from command %s'%message
    logger.debug('response: %s'%text)
    if 'reply_text' in dir(update.message):
        update.message.reply_text(text,reply_markup=reply_markup,parse_mode=telegram.ParseMode.HTML)
    else:
        #update.callback_query.edit_message_text(text,reply_markup=reply_markup)
        #update.callback_query.edit_message_reply_markup(reply_markup=reply_markup)
        bot.send_message(chat_id=update.callback_query.message.chat.id,text=text,reply_markup=reply_markup)

@run_async
def habla(update,context):
    message = update.message.text
    params = message.split(" ")
    logger.debug("request: %s"%message)
    chatId = update.message.chat.id
    text = Content.speech(params,bot,chatId)
    logger.debug('response: %s'%text)
    update.message.reply_text(text)

@run_async
def torrent(update,context):
    message = update.message.text
    chatId = update.message.chat.id
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
    update.message.reply_text(text)
    logger.debug('response: %s'%text)

@run_async
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
    if file_id and bot and voice:
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

@run_async
def pronostico(update,context):
    message = update.message.text
    chatId = update.message.chat.id
    params = message.split(" ")
    logger.debug("request: %s"%message)
    message = message[message.find(" ")+1:]
    text = Content.weather(message)

    update.message.reply_text(text)
    logger.debug("response: %s"%text)

@run_async
def upload(update,context):
    logger.debug("upload!")
    message = update.message.text
    chatId = update.message.chat.id
    #botName, file, telegramCli
    params = message.split(" ")
    file = params[1]
    logger.debug("target file: %s"%file)
    if os.path.exists(DOWNLOAD_PATH+file) and os.path.isfile(DOWNLOAD_PATH+file):
    	Content.upload(BOT_NAME,DOWNLOAD_PATH+file,TELEGRAM_CLI)
    update.message.reply_text("uploaded file %s"%file)


def main():
    logger.info("Initting bot...")
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(token=TOKEN,use_context=True,workers=99)

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
    dp.add_handler(CommandHandler("flipax", flipax))
    dp.add_handler(CommandHandler("habla", habla))
    dp.add_handler(CommandHandler("torrent", torrent))
    dp.add_handler(CommandHandler("pronostico", pronostico))
    dp.add_handler(CommandHandler("upload",upload))
    #end old commands migration

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    #handler of query_data in buttons
    dp.add_handler(CallbackQueryHandler(buttons))

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
