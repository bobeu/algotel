#!/usr/bin/env python
# -*- coding: utf-8 -*-

from algosdk import account, mnemonic
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram.ext import ConversationHandler
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup
from client import connect
import time

algod_client = connect(None, None)

reply_keyboard = [
    ['/GetAlc', '/GetPhrase'],
    ['/Buy_DMT2', '/AlcStatus', '/GetBal'],
    ['/About', '/Help', '/Cancel'],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


# Create new public/private key pair
def create_account(update, context):
    """
    Returns the result of generating an account to user:
        - An Algorand address
        - A mnemonic seed phrase
    """
    update.message.reply_text("Hang on while I get you an account ...")
    time.sleep(1)
    sk, pk = account.generate_account()
    update.message.reply_text("Your address:   {}\nPrivate Key:    {}\n".format(pk, sk))
    update.message.reply_text(
        "Keep your mnemonic phrase from prying eyes.\n"
        "\nI do not hold or manage your keys."
    )
    context.user_data['default_sk'] = sk
    context.user_data['default_pk'] = pk
    if context.user_data.get('default_pk') == pk and context.user_data['default_sk'] == sk:
        update.message.reply_text("Account creation success.")
    else:
        update.message.reply_text('Account creation error\n.')
    time.sleep(1.5)
    update.message.reply_text('To test if your address works fine, copy your address, and visit:\n ')
    keyboard = [[InlineKeyboardButton(
        "DISPENSER", 'https://bank.testnet.algorand.network/', callback_data='1')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('the dispenser to get some Algos', reply_markup=reply_markup)

    update.message.reply_text("Session ended. Click /start to begin.")
    return ConversationHandler.END


# Generate mnemonic words - 25 Algorand-type seed phrase
def get_mnemonics_from_sk(update, context):
    """
    Takes in private key and converts to mnemonics
    :param context:
    :param update:
    :return: 25 mnemonic words
    # """
    try:
        # sk = update.message.reply_text("Enter secret key: ")
        if 'default_sk' in context.user_data:
            sk = context.user_data['default_sk']
            phrase = mnemonic.from_private_key(sk)
            update.message.reply_text(
                "Your Mnemonics:\n {}\n\nKeep your mnemonic phrase from prying eyes.\n"
                "\n\nI do not hold or manage your keys.".format(phrase), reply_markup=markup
            )
            update.message.reply_text('\nSession ended.')
            return ConversationHandler.END
        else:
            update.message.reply_text("Key erased")
    except Exception as err:
        update.message.reply_text("Cannot find any key.\nPlease create an account first")


# Check balance on an account's public key
def query_balance(update, context):
    try:
        if 'default_sk' in context.user_data:
            pk = context.user_data['default_pk']
            update.message.reply_text("Getting the balance on this address ==>   {}.".format(pk))
            if len(pk) == 58:
                account_bal = algod_client.account_info(pk)
                bal = account_bal['amount']
                update.message.reply_text("Balance on your account: {}".format(bal))
                for k in account_bal['assets']:
                    update.message.reply_text(f"Asset balance: {k['amount']}, Asset ID: {k['asset-id']}")
            else:
                update.message.reply_text("Wrong address supplied.\nNo changes has been made.")
                return ConversationHandler.END
        else:
            update.message.reply_text("Cannot find public key")
    except Exception as e:
        update.message.reply_text("Something went wrong.\n Click /start to restart the bot\nand create an account")
