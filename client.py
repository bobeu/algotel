#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from algosdk.v2client import algod
from telegram import ReplyKeyboardMarkup

reply_keyboard = [
    ['/GetAlc', '/GetPhrase'],
    ['/Buy_DMT2', '/AlcStatus', '/GetBal'],
    ['/About', '/Help', '/Cancel'],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def connect(update, context):
    url = os.environ.get(
        'API_URL_V2'
    )  # Serve the endpoint to client node (https://purestake.com)
    algod_token = os.environ.get(
        'ALGODTOKEN')  # Your personal token (https://purestake.com)
    headers = {"X-API-Key": algod_token}
    try:
        return algod.AlgodClient(algod_token, url, headers)
    except Exception as e:
        update.message.reply_text("Something went wrong.")
