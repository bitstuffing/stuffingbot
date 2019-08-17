import logging
import sys
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from content import Content
import time
import os
import logger
from bot.core.config import Config

TOKEN = Config.getConfig()["TOKEN"]
bot = telegram.Bot(TOKEN)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    context.message.reply_text('Hi!')


def help(update, context):
    """Send a message when the command /help is issued."""
    context.message.reply_text('Help!')


def echo(update, context):
    """Echo the user message."""
    logger.debug(str(update))
    logger.debug(str(context))
    context.message.reply_text("echo: "+context.message.text)


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


def main():
    logger.info("Initting bot...")
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    #start old commands migration
    dp.add_handler(CommandHandler("decode", decode))
    dp.add_handler(CommandHandler("exvagos", exvagos))
    dp.add_handler(CommandHandler("habla", habla))
    dp.add_handler(CommandHandler("torrent", torrent))
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
