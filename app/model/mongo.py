# -*- encoding: utf-8 -*-
'''
@File    :   mongo.py
@Time    :   2023/03/07 23:37:09
@Author  :   Claysome 
@Contact :   claysomes@outlook.com
'''

"""MongoDB motor module"""

import json
from pymongo import MongoClient
import websocket


class WebsocketConnector:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client["binance"]
        self.collection = self.db["btcusdt_aggtrades"]
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
        json_message = json.loads(message)
        trade_info = json_message["data"]
        # 将数据存入 MongoDB
        result = self.collection.insert_one(trade_info)
        print(f"Inserted document with ID {result.inserted_id}")

    def connect(self):
        self.socket = websocket.WebSocketApp(self.url,
                                             on_open=self.on_open,
                                             on_close=self.on_close,
                                             on_message=self.on_message)
        self.socket.run_forever()


if __name__ == "__main__":
    connector = WebsocketConnector()
    connector.connect()  