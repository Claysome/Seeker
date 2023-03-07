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

        self.url = "wss://stream.binance.com:9443/ws"
        self.socket = None

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

    def on_close(self):
      print("Disconnected.")

    def on_message(self, _, message):
        print(json.loads(message))

    def connect(self):
        self.socket = websocket.WebSocketApp(self.url,
                                             on_open=self.on_open,
                                             on_close=self.on_close,
                                             on_message=self.on_message)
        self.socket.run_forever()


if __name__ == "__main__":
    connector = WebsocketConnector()
    connector.connect()  