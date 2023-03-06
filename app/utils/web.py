# -*- encoding: utf-8 -*-
'''
@File    :   web.py
@Time    :   2023/03/06 11:42:31
@Author  :   Claysome 
@Contact :   claysomes@outlook.com
'''

"""Websocket connection based on binance connector"""


import time
import logging
from binance.lib.utils import config_logging
from binance.websocket.spot.websocket_stream import SpotWebsocketStreamClient as Client

config_logging(logging, logging.DEBUG)

def message_handler(_, message):
    logging.info(message)

my_client = Client(on_message=message_handler)

my_client.ticker(symbol="bnbusdt")

time.sleep(30)

logging.debug("closing ws connection")
my_client.stop()