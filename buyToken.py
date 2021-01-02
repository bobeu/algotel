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
tokenSale = None
price_progress = [0.0002]  # Tracks price change
current_price = price_progress[-1]
# lastTime = 0
saleable = 6000000
total_buy = 0
assetBalance = 0
asset_id = 13251912
TO = os.environ.get("DEFAULT2_ACCOUNT")
AUTH = os.environ.get("DEFAULT2_MNEMONIC")
# startTime = int(round(time.time()))  # 1609543075
# current_time = 0
# timeFrame = {
#     'currentTime': 0,
# }
rate = 30

accountInfo = algod_client.account_info(TO)
successful = None
if saleable > 0:
    tokenSale = True
else:
    tokenSale = False


def updatePrice(update, context):
    if total_buy in range(500, 2000001):
        rate -= 10
        current_price = current_price
        print(price_progress)
        update.message.reply_text(
            "Current price per DMT2: {} MicroAlgo".format(current_price))
    elif total_buy in range(2000000, 4000001):
        rate -= 10
        newPrice = int(current_price + (current_price / 2))
        price_progress.append(newPrice)
        print(price_progress)
        update.message.reply_text(
            "Current price per DMT2: {} MicroAlgo".format(newPrice))
    elif total_buy > 4000000:
        rate -= 10
        newPrice = int(current_price + (current_price / 2))
        price_progress.append(newPrice)
        print(price_progress)
        update.message.reply_text(
            "Current price per DMT2: {} MicroAlgo".format(newPrice))

        price_progress.append(current_price)
        rate = rate
        update.message.reply_text(
            "Current price per DMT2: {} MicroAlgo".format(current_price))


def updateAssetBalance(update, context):
    global assetBalance
    for i in accountInfo['assets']:
        if i['asset-id'] == asset_id:
            assetBalance = i['amount']
            break


def transfer(update, context, sender, receiver, amount):
    global total_buy
    global saleable
    params = algod_client.suggested_params()
    params.fee = 1000
    params.flat_fee = True

    print(amount)
    print(receiver)
    assert saleable >= total_buy, response_end(
        update, context, "Sales for the period is exhausted")

    txn = AssetTransferTxn(
        sender=sender,  # asset_manage_authorized,
        sp=params,
        receiver=receiver,
        amt=int(amount),
        index=asset_id)
    # Sign the transaction
    sk = mnemonic.to_private_key(AUTH)
    signedTrxn = txn.sign(sk)

    # Submit transaction to the network
    tx_id = algod_client.send_transaction(signedTrxn)
    message = "Successful! Transaction hash: {}.".format(tx_id)
    total_buy += amount
    wait_for_confirmation(update, context, algod_client, tx_id)
    logging.info(
        "...##Asset Transfer... \nReceiving account: {}.\nMessage: {}\nOperation: {}\nTxn Hash: {}"
        .format(receiver, message, transfer.__name__, tx_id))

    update.message.reply_text(message)
    total_buy += amount
    saleable -= total_buy
    # context.user_data.clear()
    print(price_progress)
    print(current_price)
    print(saleable)
    return markup


# def priceSelfRoll(update, context):
#     global current_price
#     if startTime:
#         new_increment_time = 86400
#         if int(round(time.time())) == (startTime + new_increment_time):
#             new_price = current_price + (current_price // 2)
#             price_progress.append(new_price)
#             update.message.reply_text("Current price per DMT2: {} Algo".format(new_price))


def response_end(update, context, message):
    update.message.reply_text(message)
    return ConversationHandler.END


def buy_token(update, context):
    global max_buy
    global successful
    global current_price
    global startTime
    global countdown
    global tokenSale
    global price_progress
    global current_time
    global rate

    updatePrice(update, context)
    updateAssetBalance(update, context)

    update.message.reply_text("Broadcasting transaction...")
    user_data = context.user_data
    buyer = user_data["Public_key"]
    qty = user_data["Quantity"]
    sk = user_data["Secret_Key"]
    note = user_data["Note"].encode()

    optin(update, context, buyer, sk)
    time.sleep(3)
    max_buy = 2000000

    try:
        params = algod_client.suggested_params()
        fee = params.fee = 1000
        flat_fee = params.flat_fee = True
        amountToPay = int(current_price * int(qty))
        alcBal = algod_client.account_info(buyer)['amount']
        assert alcBal > amountToPay, response_end(update, context,
                                                  "Not enough balance.")
        assert qty <= max_buy, response_end(
            update, context, "Max purchase cannot exceed 100000 DMT2")
        assert tokenSale == True, response_end(update, context,
                                               "Token Sale has ended")
        assert qty < max_buy, response_end(
            update, context, "Max mount per buy is restricted to 200000 DMT2.")
        assert qty >= 500, response_end(
            update, context, "Minimum buy is 500 DMT2.\n Session ended.")
        assert len(buyer) == 58, response_end(update, context,
                                              "Incorrect address")

        raw_trxn = transaction.PaymentTxn(sender=buyer,
                                          fee=fee,
                                          first=params.first,
                                          last=params.last,
                                          gh=params.gh,
                                          receiver=TO,
                                          amt=amountToPay,
                                          close_remainder_to=None,
                                          note=note,
                                          gen=params.gen,
                                          flat_fee=flat_fee,
                                          lease=None,
                                          rekey_to=None)

        # Sign the transaction
        signedTrxn = raw_trxn.sign(sk)
        update.message.reply_text("Just a second.....")
        # Submit transaction to the network
        tx_id = algod_client.send_transaction(signedTrxn)
        message = "Transaction hash: {}.".format(tx_id)
        wait = wait_for_confirmation(update, context, algod_client, tx_id)
        logging.info(
            "...##Asset Transfer... \nReceiving account: {}.\nMessage: {}\nOperation: {}\n"
            .format(buyer, message, buy_token.__name__))
        successful = bool(wait is not None)

        if successful:
            amountToSend = int(qty + (qty * (rate / 100)))
            update.message.reply_text(
                "Payment received!\nSending you {} DMT2 Token".format(
                    amountToSend))
            update.message.reply_text(
                f"Payment success...\nTransferring token to address... --> {buyer}"
            )
            transfer(update, context, TO, buyer, amountToSend)
        else:
            response_end(update, context, "Transaction was not successful")

    except Exception as err:
        logging.info("Error encountered: ".format(err))
        update.message.reply_text("Unsuccessful")
