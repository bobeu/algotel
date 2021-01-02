#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from status import account_status
from buyToken import *
from getInput import *
from client import markup
from generateAccount import create_account, get_mnemonics_from_sk, query_balance
import os

from telegram.ext import (Updater, CommandHandler, Filters,
                          ConversationHandler, PicklePersistence,
                          CallbackContext, MessageHandler)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

# PORT = int(os.environ.get('PORT', 5000))
TOKEN = os.environ.get('BOT_TOKEN')  # Token from the bot father
updateAssetBalance(None, None)


def start(update, context: CallbackContext):
    user = update.message.from_user
    reply = "Hi {}! I am ALGOMessenger.".format(user['first_name'])
    reply += ("I can help you with a few things.\n"
              "Tell me what you need to do.\nThey should be from the menu.\n"
              "/GetAlc - Create an account.\n"
              "/GetPhrase - get Mnemonic words.\n"
              "/GetBal - account balance.\n"
              "/Buy_DMT2 - buy GMT2 Token.\n"
              "/AlcStatus - account information.\n"
              "/About - about us."
              "/Help if you need help."
              "/Cancel to end a conversation."
              "/Menu pops up the main menu.")
    update.message.reply_text(reply, reply_markup=markup)
    context.user_data.clear()


# Returns to main menu
def menuKeyboard(update, context):
    update.message.reply_text('Back to Menu', reply_markup=markup)


# Returns about us
def aboutUs(update, context):
    keyboard = [[
        InlineKeyboardButton("Website",
                             'https://algorand.com',
                             callback_data='1'),
        InlineKeyboardButton("Developer'site",
                             'https://developer.algorand.org',
                             callback_data='2')
    ],
                [
                    InlineKeyboardButton("Community",
                                         'https://community.algorand.com',
                                         callback_data='3')
                ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Learn more about Algorand:',
                              reply_markup=reply_markup)


def help_command(update, context):
    update.message.reply_text("Use /start to test this bot.")


def cancel(update, context):
    update.message.reply_text(f"Keys were removed:", reply_markup=markup)
    context.user_data.clear()
    return ConversationHandler.END


def main():
    # Create the Updater and pass it your bot's token.
    pp = PicklePersistence(filename='reloroboty')
    updater = Updater(TOKEN, persistence=pp, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('Buy_DMT2', args)],
        states={
            CHOOSING: [
                MessageHandler(
                    Filters.regex('^(Public_key|Quantity|Secret_Key|Note)$'),
                    regular_choice)
            ],
            TYPING_CHOICE: [
                MessageHandler(
                    Filters.text
                    & ~(Filters.command | Filters.regex('^Done$')),
                    regular_choice)
            ],
            TYPING_REPLY: [
                MessageHandler(
                    Filters.text
                    & ~(Filters.command | Filters.regex('^Done$')),
                    received_information,
                )
            ],
        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)],
    )

    dp.add_handler(conv_handler)

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('GetAlc', create_account))
    dp.add_handler(CommandHandler('GetPhrase', get_mnemonics_from_sk))
    dp.add_handler(CommandHandler('GetBal', query_balance))
    dp.add_handler(CommandHandler('AlcStatus', account_status))
    dp.add_handler(CommandHandler('Cancel', cancel))
    dp.add_handler(CommandHandler('About', aboutUs))
    dp.add_handler(CommandHandler('Done', buy_token))
    dp.add_handler(CommandHandler('Menu', menuKeyboard))
    dp.add_handler(CommandHandler('Help', help_command))

    # Start the Bot
    updater.start_polling()
    # updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=TOKEN)
    # updater.bot.setWebhook('https://algotelbot.herokuapp.com/' + TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
