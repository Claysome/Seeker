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


class WebsocketConnectorAggTrade:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
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
        data = {
            "symbol": json_message["s"],
            "price": json_message["p"],
            "quantity": json_message["q"],
            "trade_id": json_message["a"],
            "time": json_message["T"]
        }
        # 将数据存入 MongoDB
        result = self.collection.insert_one(data)
        print(f"Inserted document with ID {result.inserted_id}")

    def connect(self):
        self.socket = websocket.WebSocketApp(self.url,
                                             on_open=self.on_open,
                                             on_close=self.on_close,
                                             on_message=self.on_message)
        self.socket.run_forever()

if __name__ == "__main__":
    trade = WebsocketConnectorAggTrade()
    trade.connect()