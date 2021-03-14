# Python-telegram-bot libraries
import telegram
from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import Updater, InlineQueryHandler, CallbackContext

from uuid import uuid4

# Logging and requests libraries
import logging
from logging.handlers import RotatingFileHandler

# Importing token from config file
import config
from fidonetbot_db_helper import fidonetbot_db_helper


database = fidonetbot_db_helper()

# Logging module for debugging
log_format = '%(asctime)s %(filename)-12s %(funcName)s %(lineno)d %(message)s'
logging.basicConfig(handlers=[RotatingFileHandler('fidonet_bot.log',
                                                  maxBytes=500000,
                                                  backupCount=5)],
                    format=log_format,
                    level=config.LOGGER_LEVEL)

logger = logging.getLogger(__name__)  # this gets the root logger
logger.setLevel(config.LOGGER_LEVEL)


def inlinequery(update: Update, context: CallbackContext) -> None:
    """Handle the inline query."""
    query = update.inline_query.query

    # TODO: what if we asked for /7 ?
    # TODO: what if we asked 5011 ?
    if len(query) < config.inline_query_limit:
        return

    result_list = database.get_fidodata_by_text(query)

    logger.info(result_list)
    logger.info('len is %d', len(result_list))

    results = []
    # index = 0
    # paginator = 1

    for entry in result_list:
        # logger.info(entry)

        results.append(InlineQueryResultArticle(
                        id=uuid4(),
                        title=entry['title'],
                        input_message_content=InputTextMessageContent(entry['data'])
                        ))
        # index += 1

        logger.info('title is %s', entry['title'])

    update.inline_query.answer(results)
'''
        if index // config.page_limit == 1:
            logger.info('index: %d', index)
            logger.info('paginator %d: ', paginator)

            update.inline_query.answer(results,
                                       current_offset=config.page_limit * (paginator - 1),
                                       next_offset=config.page_limit * paginator,
                                       auto_pagination=True)
            results.clear()
            index = 0
            paginator += 1

    update.inline_query.answer(results,
                               current_offset=config.page_limit * (paginator - 1),
                               next_offset=config.page_limit * paginator,
                               auto_pagination=True)
'''


def main():
    bot = telegram.Bot(token=config.token)

    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(token=config.token, use_context=True)

    logger.info("Authorized on account %s. "
                "version is %s" % (bot.username, config.version))

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    dispatcher.add_handler(InlineQueryHandler(inlinequery))

    # log all errors
    # dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
