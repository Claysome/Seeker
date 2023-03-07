# -*- encoding: utf-8 -*-
'''
@File    :   web_connection.py
@Time    :   2023/03/07 23:06:18
@Author  :   Claysome 
@Contact :   claysomes@outlook.com
'''

"""Websocket connector"""


import websocket
import json


class WebsocketConnector:

    def __init__(self):
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(
            "wss://stream.binance.com:9443/ws/",
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )

    def on_message(self, ws, message):
        json_message = json.loads(message)
        print(json_message)

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws):
        print("### closed ###")

    def on_open(self, ws):
        sub_data = {
        "method": "SUBSCRIBE",
        "params":
        [
            "btcusdt@aggTrade"
        ],
        "id": 1
        }
        ws.send(json.dumps(sub_data))

    def connect(self):
        self.ws.on_open = self.on_open
        self.ws.run_forever()


if __name__ == "__main__":
    connector = WebsocketConnector()
    connector.connect()