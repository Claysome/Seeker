# -*- encoding: utf-8 -*-
'''
@File    :   web.py
@Time    :   2023/03/06 11:42:31
@Author  :   Claysome 
@Contact :   claysomes@outlook.com
'''

"""Websocket connection based on binance connector"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.api.test_api import TEST
api_key = TEST['api_key']
api_secret = TEST['api_secret']

import logging
import time
from binance.lib.utils import config_logging
from binance.websocket.spot.websocket_api import SpotWebsocketAPIClient
from binance.websocket.spot.websocket_stream import SpotWebsocketStreamClient
from binance.spot import Spot as Client


config_logging(logging, logging.DEBUG)

def on_close(_):
    logging.info("Do custom stuff when connection is closed")

def api_message_handler(_, message):
    logging.info("API: ")
    logging.info(message)

def stream_message_handler(_, message):
    logging.info("STREAM Hello server: ")
    logging.info(message)


my_api_client = SpotWebsocketAPIClient(
    api_key=api_key,
    api_secret=api_secret,
    on_message=api_message_handler,
    on_close=on_close,
)

my_stream_client = SpotWebsocketStreamClient(on_message=stream_message_handler)

spot_client = Client(api_key, api_secret)

my_stream_client.ticker(symbol="btcbusd")

my_api_client.account()
time.sleep(2)

logging.info(spot_client.account_snapshot("SPOT"))
my_api_client.account()
time.sleep(2)

logging.info("closing ws connection")
my_api_client.stop()
my_stream_client.stop()