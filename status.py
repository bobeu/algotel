#!/usr/bin/env python
# -*- coding: utf-8 -*-

from waitforconfirmation import algod_client
import time
from telegram.ext import ConversationHandler


def account_status(update, context):
    """
    :param update: Telegram's default param
    :param context: Telegram's default param
    :param address: 32 bytes Algorand's compatible address
    :return: Address's full information
    """
    try:
        pk = context.user_data['default_pk']
        status = algod_client.account_info(pk)
        for key, value in status.items():
            update.message.reply_text("{} : {}".format(key, value))
        return ConversationHandler.END
    except Exception as e:
        update.message.reply_text("Something went wrong.\nProbably I cannot find any key.\n"
                                  "Re /start and create an account or supply your public key"
                                  "if you have one.")