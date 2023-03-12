# -*- encoding: utf-8 -*-
'''
@File    :   maker.py
@Time    :   2023/03/12 23:15:35
@Author  :   Claysome 
@Contact :   claysomes@outlook.com
'''

import sys
from os.path import abspath, dirname

BASE_DIR = abspath(dirname(__file__))
sys.path.append('{}/../'.format(BASE_DIR))

from app.api.biconomy.spot import BiconomyHttp
from app.api.binance.spot import BinanceSpotHttp, OrderSide, OrderType

from app.utils.loggingtool import get_logger
from app.utils.tools import round_to
from app.utils.tools import to_symbol
from app.utils.tools import random_int_list
import random
import time


class Maker:
    def __init__(self, pair: str, symbol: str, bico_key: str, bico_secret: str, total_assets: float, times=1):
        self.logger = get_logger(pair, + ".log")
        self.bico = BiconomyHttp(bico_key, bico_secret)
        self.binance = BinanceSpotHttp()
        self.pair = pair
        self.symbol = symbol
        self.total_assets = total_assets
        self.pair_info = self.binance.get_pair_info(to_symbol(pair))

    @staticmethod
    def get_price_list(base_price: float, count: int, step_size: float, side: int):
        floats = []
        for i in range(0, 30):
            floats.append(base_price + step_size * i * side)
        ints = random_int_list(-3, 500, count-30)
        for item in ints:
            floats.append(base_price + step_size * item * side)
        return floats
    
    def get_bid_prices(self):
        try:
            prices = []
            binance_pair = to_symbol(self.pair)
            buy_price = self.binance.get_latest_price(binance_pair)
            prices.append(buy_price)
            prices.append(self.get_price_list(buy_price, 60, self.pair_info['min_price'], -1))
            return prices
        
        except Exception as e:
            self.logger.error(f"%s: %s" % (self.pair, repr(e)))
            return None
        
    def get_ask_prices(self):
        try:
            prices = []
            binance_pair = to_symbol(self.pair)
            sell_price = self.binance.get_latest_price(binance_pair)
            prices.append(sell_price)
            prices.append(self.get_price_list(sell_price, 60, self.pair_info['min_price'], 1))
            return prices
        
        except Exception as e:
            self.logger.error(f"%s: %s" % (self.pair, repr(e)))
            return None
                              
    def get_order_depth(self, direction: str):
        order_list = self.bico.get_order_book(symbol="BTC_USDT", size=100)
        if direction == "asks" and order_list is not None:
            return len(order_list["asks"])
        elif direction == "bids" and order_list is not None:
            return len(order_list["bids"])
        else:
            return 0
        
    def get_binance_asset(self, symbol: str):
        try:
            account = self.bico.get_account_info()
            asset_balance = 0
            for asset in account["balances"]:
                if asset["asset"] == symbol:
                    asset_balance = float(asset["free"])
                    return asset_balance
        except Exception as e:
            self.logger.error(f"%s: %s" % (self.pair, repr(e)))
            return -1
        
    def get_bico_asset_inorder(self, symbol: str):
        asset = self.bico.get_user_assets()
        return float(asset["result"]["BTC"]["freeze"])
    
    def get_bico_asset(self, symbol: str):
        try:
            asset = self.bico.get_user_assets()
            btc_num = float(asset["result"]["BTC"]["available"]) + float(asset["result"]["BTC"]["freeze"]) + float(asset["result"]["BTC"]["other_freeze"])
        except Exception as e:
            self.logger.error(f"%s: %s" % (self.pair, repr(e)))
            return -1
        else:  
            return btc_num
        
    def is_bico_symbo(self, symbol: str):
        try:
            pairs = self.bico.get_exchange_info()
            for pair in pairs:
                if pair["baseAsset"] == symbol:
                    return True
        except Exception as e:
            self.logger.error(f"%s: %s" % (self.pair, repr(e)))
            return False
        
    def get_binance_asks(self, symbol):
        asks = self.binance.get_order_book(symbol, 20)["asks"]
        prices = []
        for ask in asks:
            prices.append(ask[0])
        return prices
    
    def get_binance_bids(self, symbol):
        bids = self.binance.get_order_book(symbol, 20)["bids"]
        prices = []
        for bid in bids:
            prices.append(bid[0])
        return prices
    
    def get_price_faster(self, base_price: float, step_price: float, begin: int, end: int, side):
        floats = []
        for i in range(begin, end+1):
            floats.append(base_price + step_price * i * side)
        return floats
    
    def auto_ask(self):
        try:
            ask_prices = self.get_ask_prices()
            for i in range(0, len(ask_prices)):
                ask_price = ask_prices[i]
                min_qty = round_to(self.pair_info["min_notional"] / ask_prices[0], self.pair_info["min_qty"])
                ask_amount = round_to((random.randint(1, 10) + min_qty) * self.times, self.pair_info["min_qty"])
                min_price = self.pair_info["min_price"]
                ask_price = round_to(ask_price, min_price)
                info = self.bico.place_order_bico(market=self.pair, amount=str(ask_amount), side="1", price=str(ask_price))

                self.logger.info(info)
                time.sleep(0.3)
        except Exception as e:
            self.logger.error(f"%s: %s" % (self.pair, repr(e)))

    def auto_ask_faster(self):
        try:
            binance_pair = to_symbol(self.pair)
            base_price = self.binance.get_latest_price(binance_pair)
            step_price = self.pair_info["min_price"]
            ask_prices = self.get_price_faster(base_price, step_price, 0, 5, 1)
            for i in range(0, len(ask_prices)):
                ask_price = ask_prices[i]
                min_qty = round_to(self.pair_info["min_notional"] / ask_prices[0], self.pair_info["min_qty"])
                ask_amount = round_to((random.randint(1, 30) + min_qty) * self.times, self.pair_info["min_qty"])
                min_price = self.pair_info["min_price"]
                ask_price = round_to(ask_price, min_price)
                info = self.bico.place_order_bico(market=self.pair, amount=str(ask_amount), side="1", price=str(ask_price))

                self.logger.info(info)
                time.sleep(0.3)
        except Exception as e:
            self.logger.error(f"%s: %s" % (self.pair, repr(e)))

    def auto_bid(self):
        try:
            buy_prices = self.get_bid_prices()
            for i in range(0, len(buy_prices)):
                buy_price = buy_prices[i]
                min_qty = round_to(self.pair_info["min_notional"] / buy_prices[0], self.pair_info["min_qty"])
                buy_amount = round_to((random.randint(1, 10) + min_qty) * self.times, self.pair_info["min_qty"])
                min_price = self.pair_info["min_price"]
                buy_price = round_to(buy_price, min_price)
                info = self.bico.place_order_bico(market=self.pair, amount=str(buy_amount), side="2", price=str(buy_price))

                self.logger.info(info)
                time.sleep(0.05)

        except Exception as e:
            self.logger.error(f"%s: %s" % (self.pair, repr(e)))

    def auto_bid_faster(self):
        try:
            binance_pair = to_symbol(self.pair)
            base_price = self.binance.get_latest_price(binance_pair)
            step_price = self.pair_info["min_price"]
            buy_prices = self.get_price_faster(base_price, step_price, 0, 5, -1)
            for i in range(0, len(buy_prices)):
                buy_price = buy_prices[i]
                min_qty = round_to(self.pair_info["min_notional"] / buy_prices[0], self.pair_info["min_qty"])
                buy_amount = round_to((random.randint(1, 30) + min_qty) * self.times, self.pair_info["min_qty"])
                min_price = self.pair_info["min_price"]
                buy_price = round_to(buy_price, min_price)
                info = self.bico.place_order_bico(market=self.pair, amount=str(buy_amount), side="2", price=str(buy_price))

                self.logger.info(info)
                time.sleep(0.3)
        except Exception as e:
            self.logger.error(f"%s: %s" % (self.pair, repr(e)))

    def del_orders(self):
        self.bico.delete_orders(self.pair)

    def auto_hedging(self):
        while True:
            try:
                binance_asset = self.get_binance_asset(self.symbol)
                bico_asset = self.get_bico_asset(self.symbol)
                min_qty = round_to(self.pair_info["min_notional"] / self.binance.get_latest_price(to_symbol(self.pair)),
                                   self.pair_info["min_qty"])
                if (self.total_assets - binance_asset - bico_asset) >= min_qty:

                    hedging_asset = round_to(self.total_assets - binance_asset - bico_asset, min_qty)
                    price = self.binance.get_ticker(to_symbol(self.pair))["bidPrice"]
                    order_id = self.binance.place_order(to_symbol(self.pair), OrderSide.BUY, OrderType.MARKET, hedging_asset, price)["clientOrderId"]
                    self.logger.info(f"buy successfully from binance, order id: %s, quantity: %s" % (order_id, hedging_asset))

                elif (binance_asset + bico_asset - self.total_assets) >= min_qty:
                    hedging_asset = round_to(binance_asset + bico_asset - self.total_assets, min_qty)
                    price = self.binance.get_ticker(to_symbol(self.pair))["askPrice"]
                    order_id = self.binance.place_order(to_symbol(self.pair), OrderSide.SELL, OrderType.MARKET, hedging_asset, price)["clientOrderId"]
                    self.logger.info(f"sell successfully from binance, order id: %s, quantity: %s" % (order_id, hedging_asset))

            except Exception as e:
                self.logger.error(f"%s: %s" % (self.pair, repr(e)))