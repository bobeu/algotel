#!/usr/bin/env python
# -*- coding: utf-8 -*-

from algosdk.future.transaction import transaction
from algosdk import mnemonic
from waitforconfirmation import wait_for_confirmation, algod_client
from algosdk.future.transaction import AssetTransferTxn
from client import markup
from optIn import optin
import logging
import os
from telegram.ext import ConversationHandler
import time

# startTTime = int(round(time.time() * 345600))
startTime = 1609395714
price_progress = [30000,] # Tracks price change
current_price = price_progress[-1]
saleable = 5000000
total_buy = 0
tokenBalance = None
asset_id = 13251912
TO = os.environ.get("DEFAULT2_ACCOUNT")
AUTH = os.environ.get("DEFAULT2_MNEMONIC")
accountInfo = algod_client.account_info(TO)
max_buy = 100000
successful = None
countdown = 0


def getAssetBalance():
    global tokenBalance
    for i in accountInfo['assets']:
        if i['asset-id'] == asset_id:
            tokenBalance = i['amount']
            break


def transfer(update, context, sender, receiver, amount):
    global total_buy
    params = algod_client.suggested_params()
    params.fee = 1000
    params.flat_fee = True
    assert amount <= max_buy, response_end(update, context, "Max purchase cannot exceed 100000 DMT2")
    assert saleable >= total_buy, response_end(update, context, "Sales for the period is exhausted")

    txn = AssetTransferTxn(
        sender=sender,  # asset_manage_authorized,
        sp=params,
        receiver=receiver,
        amt=amount,
        index=asset_id
    )
    # Sign the transaction
    sk = mnemonic.to_private_key(AUTH)
    signedTrxn = txn.sign(sk)

    # Submit transaction to the network
    tx_id = algod_client.send_transaction(signedTrxn)
    message = "Successful! Transaction hash: {}.".format(tx_id)
    total_buy += amount
    wait_for_confirmation(update, context, algod_client, tx_id)
    logging.info("...##Asset Transfer... \nReceiving account: {}.\nMessage: {}\nOperation: {}\nTxn Hash: {}".format(
        receiver,
        message,
        transfer.__name__,
        tx_id
    ))

    update.message.reply_text(message)
    # context.user_data.clear()
    print(price_progress)
    print(current_price)
    print(tokenBalance)
    return markup


def priceSelfRoll(update, context):
    global current_price
    if startTime:
        new_increment_time = 86400
        if int(round(time.time())) == (startTime + new_increment_time):
            new_price = current_price + (current_price // 2)
            price_progress.append(new_price)
            update.message.reply_text("Current price per DMT2: {} Algo".format(new_price))


def response_end(update, context, message):
    update.message.reply_text(message)
    return ConversationHandler.END


def buy_token(update, context):
    global max_buy
    global successful
    global current_price
    global startTime
    global countdown

    update.message.reply_text("Broadcasting transaction...")
    user_data = context.user_data
    buyer = user_data["Public_key"]
    qty = user_data["Quantity"]
    sk = user_data["Secret_Key"]
    note = user_data["Note"]

    optin(update, context, buyer, sk)
    max_buy = 200000
    try:

        if int(round(time.time())) >= startTime and countdown == 0:
            current_price = price_progress[0]
            startTime += 180 # 86400
            countdown += 1
        elif int(round(time.time())) >= startTime and countdown > 0:
            current_price = price_progress[-1]
            new_price = current_price + (current_price / 2)
            price_progress.append(new_price)
            update.message.reply_text("Current price per DMT2: {} Algo".format(new_price))
        if int(round(time.time())) >= startTime:
            # assert int(round(time.time())) > startTime, "Countdown for sale is behind"
            assert qty >= 500, response_end(update, context, "Minimum buy is 500 DMT2.\n Session ended.")
            assert len(buyer) == 58, response_end(update, context, "Incorrect address")
            params = algod_client.suggested_params()
            fee = params.fee = 1000
            flat_fee = params.flat_fee = True
            receiver = TO
            note = note.encode()
            amount = int(current_price * int(qty))
            assert qty < max_buy, response_end(update, context, "Amount per buy is restricted to 200000 max.")

            raw_trxn = transaction.PaymentTxn(
                sender=buyer,
                fee=fee,
                first=params.first,
                last=params.last,
                gh=params.gh,
                receiver=TO,
                amt=amount,
                close_remainder_to=None,
                note=note,
                gen=params.gen,
                flat_fee=flat_fee,
                lease=None,
                rekey_to=None

            )

            # Sign the transaction
            signedTrxn = raw_trxn.sign(sk)
            update.message.reply_text("Just a second.....")
            # Submit transaction to the network
            tx_id = algod_client.send_transaction(signedTrxn)
            message = "Transaction hash: {}.".format(tx_id)
            wait = wait_for_confirmation(update, context, algod_client, tx_id)
            logging.info("...##Asset Transfer... \nReceiving account: {}.\nMessage: {}\nOperation: {}\n".format(
                receiver,
                message,
                buy_token.__name__
            ))
            successful = bool(wait is not None)

            if successful:
                update.message.reply_text(f"Payment success...\nTransferring token to address... --> {buyer}")
                transfer(update, context, TO, buyer, qty)
            else:
                response_end(update, context, "Transaction is unsuccessful")
        else:
            update.message.reply_text("Countdown for sale is behind")
            return

    except Exception as err:
        logging.info("Error encountered: ".format(err))
        update.message.reply_text("Unsuccessful")

