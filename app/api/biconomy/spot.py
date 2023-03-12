# -*- encoding: utf-8 -*-
'''
@File    :   spot.py
@Time    :   2023/03/12 21:47:27
@Author  :   Claysome 
@Contact :   claysomes@outlook.com
'''

"""
Biconomy api
"""

import time
from enum import Enum
from threading import Lock

import requests
from urllib3 import encode_multipart_formdata

from utils.utility import get_md5_32
from app.utils.loggingtool import get_logger

class OrderStatus(Enum):
    NEW = "NEW"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    PENDING_CANCEL = "PENDING_CANCEL"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class OrderType(Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP = "STOP"


class RequestMethod(Enum):
    """
    请求的方法.
    """
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'


class Interval(Enum):
    """
    请求的K线数据..
    """
    MINUTE_1 = '1min'
    MINUTE_5 = '5min'
    MINUTE_15 = '15min'
    MINUTE_30 = '30min'
    HOUR_1 = 'hour'
    DAY_1 = 'day'
    WEEK_1 = 'week'


class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"


class BiconomyHttp(object):
    def __init__(self, api_key=None, secret=None, host=None, proxy_host=None, proxy_port=0, timeout=5, try_counts=2):
        self.api_key = api_key
        self.secret = secret
        # http://www.biconomy.com
        self.host = host if host else "http://47.245.25.143:8883"
        # self.host = host if host else "https://www.biconomy.com"
        self.recv_window = 10000
        self.timeout = timeout
        self.order_count_lock = Lock()
        self.order_count = 1_000_000
        self.try_counts = try_counts  # 失败尝试的次数.
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.logger = get_logger("biconomy_api.log")

    @property
    def proxies(self):
        if self.proxy_host and self.proxy_port:
            proxy = f"http://{self.proxy_host}:{self.proxy_port}"
            return {"http": proxy, "https": proxy}

        return None

    def build_parameters(self, params: dict):
        keys = list(params.keys())
        keys.sort()
        return '&'.join([f"{key}={params[key]}" for key in params.keys()])

    def request(self, req_method: RequestMethod, path: str, requery_dict=None, verify=False):
        url = self.host + path
        if verify:
            query_str = self._sign(requery_dict)
            url += '?' + query_str
        elif requery_dict:
            url += '?' + self.build_parameters(requery_dict)
        headers = {"X-SITE-ID": "127"}
        for i in range(0, self.try_counts):
            try:
                response = requests.request(req_method.value, url=url, headers=headers, timeout=self.timeout,
                                            proxies=self.proxies)
                if response.status_code == 200:
                    return response.json()
                else:
                    self.logger.info(f"{response.status_code}-{response.reason}")
            except Exception as error:
                self.logger.info(f"请求:{path}, 发生了错误: {repr(error)}")
                time.sleep(1)
        return None

    def post_bico(self, path: str, param_dict=None):
        """
        :param path: the url
        :param param_dict: the params
        :return:
        """
        url = self.host + path
        headers = {
            "X-SITE-ID": "127",
            "Content-Type": "multipart/form-data"
        }
        for i in range(0, self.try_counts):
            try:
                encode_dict = encode_multipart_formdata(param_dict)
                data = encode_dict[0]
                headers['Content-Type'] = encode_dict[1]
                response = requests.post(url=url, headers=headers, data=data)
                if response.status_code == 200:
                    return response.json()
                else:
                    self.logger.info(f"{response.status_code}-{response.reason}")
            except Exception as error:
                self.logger.info(f"请求:{path}, 发生了错误: {repr(error)}")
                time.sleep(1)
        return None

    def get_server_time(self):
        path = '/api/v1/time'
        return self.request(req_method=RequestMethod.GET, path=path)

    def get_exchange_info(self):

        """
        return:
         the exchange info in json format:
        {'timezone': 'UTC', 'serverTime': 1570802268092, 'rateLimits':
        [{'rateLimitType': 'REQUEST_WEIGHT', 'interval': 'MINUTE', 'intervalNum': 1, 'limit': 1200},
        {'rateLimitType': 'ORDERS', 'interval': 'MINUTE', 'intervalNum': 1, 'limit': 1200}],
         'exchangeFilters': [], 'symbols':
         [{'symbol': 'BTCUSDT', 'status': 'TRADING', 'maintMarginPercent': '2.5000', 'requiredMarginPercent': '5.0000',
         'baseAsset': 'BTC', 'quoteAsset': 'USDT', 'pricePrecision': 2, 'quantityPrecision': 3, 'baseAssetPrecision': 8,
         'quotePrecision': 8,
         'filters': [{'minPrice': '0.01', 'maxPrice': '100000', 'filterType': 'PRICE_FILTER', 'tickSize': '0.01'},
         {'stepSize': '0.001', 'filterType': 'LOT_SIZE', 'maxQty': '1000', 'minQty': '0.001'},
         {'stepSize': '0.001', 'filterType': 'MARKET_LOT_SIZE', 'maxQty': '1000', 'minQty': '0.001'},
         {'limit': 200, 'filterType': 'MAX_NUM_ORDERS'},
         {'multiplierDown': '0.8500', 'multiplierUp': '1.1500', 'multiplierDecimal': '4', 'filterType': 'PERCENT_PRICE'}],
         'orderTypes': ['LIMIT', 'MARKET', 'STOP'], 'timeInForce': ['GTC', 'IOC', 'FOK', 'GTX']}]}

        """
        path = '/api/v1/exchangeInfo'
        return self.request(req_method=RequestMethod.GET, path=path)

    def get_order_book(self, symbol, size=1):
        path = "/api/v1/depth"
        query_dict = {"symbol": symbol,
                      "size": size}

        return self.request(RequestMethod.GET, path, query_dict)

    def get_kline(self, symbol, interval: Interval, size=100, max_try_time=10):
        """
        获取K线数据.
        :param interval:
        :param symbol: BTC_USDT
        :param size:
        :param max_try_time:
        :return:
        """
        path = "/api/v1/kline"

        query_dict = {
            "symbol": symbol,
            "type": interval.value,
            "size": size
        }

        for i in range(max_try_time):
            data = self.request(RequestMethod.GET, path, query_dict)
            if isinstance(data, list) and len(data):
                return data

    def get_latest_price(self, symbol):
        """
        :param symbol: 获取最新的价格.
        :return: {'symbol': 'BTC_USDT', 'price': '9168.90000000'}
        """
        path = "/api/v1/ticker/price"
        query_dict = {"symbol": symbol}
        return self.request(RequestMethod.GET, path, query_dict)

    def get_ticker(self, symbol):
        """
        :param symbol: 交易对
        :return: 返回的数据如下:
        {
        'symbol': 'BTCUSDT', 'bidPrice': '9168.50000000', 'bidQty': '1.27689900',
        'askPrice': '9168.51000000', 'askQty': '0.93307800'
        }
        """

        path = "/api/v1/ticker/bookTicker"
        query_dict = {"symbol": symbol}
        return self.request(RequestMethod.GET, path, query_dict)

    def get_all_tickers(self):
        """
        :param symbol: 交易对
        :return: 返回的数据如下:
        {
        'symbol': 'BTCUSDT', 'bidPrice': '9168.50000000', 'bidQty': '1.27689900',
        'askPrice': '9168.51000000', 'askQty': '0.93307800'
        }
        """
        path = "/api/v1/ticker/bookTicker"
        return self.request(RequestMethod.GET, path)


    def get_client_order_id(self):
        """
        generate the client_order_id for user.
        :return:
        """

        with self.order_count_lock:
            self.order_count += 1
            return "x-A6SIDXVS" + str(self.get_current_timestamp()) + str(self.order_count)

    def get_current_timestamp(self):
        """
        获取系统的时间.
        :return:
        """

        return int(time.time() * 1000)

    def _sign(self, params):
        """
        签名的方法， signature for the private request.
        :param params: request parameters
        :return:
        """
        query_string = self.build_parameters(params)
        sign_string = query_string + '&signature=' + str.upper(str.upper(get_md5_32(query_string)))
        return sign_string

    def place_order(self, symbol: str, order_side: OrderSide, order_type: OrderType, quantity: float, price: float,
                    client_order_id: str = None, time_inforce="GTC", stop_price=0):
        """
        2022-02-10 by Edwin X
        :param symbol: 交易对名称
        :param order_side: 买或者卖， BUY or SELL
        :param order_type: 订单类型 LIMIT or other order type.
        :param quantity: 数量
        :param price: 价格.
        :param client_order_id: 用户的订单ID
        :param time_inforce:
        :param stop_price:
        :return:
        """
        path = '/api/v1/order'
        if client_order_id is None:
            client_order_id = self.get_client_order_id()

        params = {
            "symbol": symbol,
            "side": order_side.value,
            "type": order_type.value,
            "quantity": quantity,
            "price": price,
            "recvWindow": self.recv_window,
            "timestamp": self.get_current_timestamp(),
            "newClientOrderId": client_order_id
        }

        if order_type == OrderType.LIMIT:
            params['timeInForce'] = time_inforce

        if order_type == OrderType.MARKET:
            if params.get('price'):
                del params['price']

        if order_type == OrderType.STOP:
            if stop_price > 0:
                params["stopPrice"] = stop_price
            else:
                raise ValueError("stopPrice must greater than 0")

        return self.request(RequestMethod.POST, path=path, requery_dict=params, verify=True)

    def place_order_bico(self, market: str, amount: str = "0", side: str = "1", price: str = "0"):
        """
        2022-02-10 by Edwin X
        :param market: BTC_USDT
        :param amount: 10.0
        :param side: 1 ask, 2 bid
        :param price: 0.003 usdt
        :return:
        """
        path = "/api/v1/private/trade/market"
        params = {
            "amount": amount,
            "api_key": self.api_key,
            "market": market
        }
        if price != "0":
            params["price"] = price
            path = "/api/v1/private/trade/limit"
        params["side"] = side
        params["secret_key"] = self.secret

        md5_sign = str.upper(get_md5_32(self.build_parameters(params)))
        params.pop("secret_key")

        params["sign"] = md5_sign

        return self.post_bico(path=path, param_dict=params)

    def get_order(self, symbol: str, client_order_id: str = ""):
        """
        获取订单状态.
        :param symbol:
        :param client_order_id:
        :return:
        """
        path = "/api/v1/order"
        prams = {"symbol": symbol, "timestamp": self.get_current_timestamp()}
        if client_order_id:
            prams["origClientOrderId"] = client_order_id

        return self.request(RequestMethod.GET, path, prams, verify=True)

    def get_all_orders(self, symbol: str):
        path = "/api/1/allOrders"
        prams = {"symbol": symbol, "timestamp": self.get_current_timestamp()}

        return self.request(RequestMethod.GET, path, prams, verify=True)

    def cancel_order(self, symbol, client_order_id):
        """
        撤销订单.
        :param symbol:
        :param client_order_id:
        :return:
        """
        path = "/api/v1/order"
        params = {"symbol": symbol, "timestamp": self.get_current_timestamp(),
                  "origClientOrderId": client_order_id
                  }

        for i in range(0, 3):
            try:
                order = self.request(RequestMethod.DELETE, path, params, verify=True)
                return order
            except Exception as error:
                print(f'cancel order error:{error}')
        return

    def cancel_all_order(self):
        return

    def get_open_orders(self, symbol=None):
        """
        获取所有的订单.
        :param symbol: BNBUSDT, or BTCUSDT etc.
        :return:
        """
        path = "/api/v1/openOrders"

        params = {"timestamp": self.get_current_timestamp()}
        if symbol:
            params["symbol"] = symbol

        return self.request(RequestMethod.GET, path, params, verify=True)

    def cancel_open_orders(self, symbol):
        """
        撤销某个交易对的所有挂单
        :param symbol: symbol
        :return: return a list of orders.
        """
        path = "/api/v1/openOrders"

        params = {"timestamp": self.get_current_timestamp(),
                  "recvWindow": self.recv_window,
                  "symbol": symbol
                  }

        return self.request(RequestMethod.DELETE, path, params, verify=True)

    def get_account_info(self):
        """
        {'feeTier': 2, 'canTrade': True, 'canDeposit': True, 'canWithdraw': True, 'updateTime': 0, 'totalInitialMargin': '0.00000000',
        'totalMaintMargin': '0.00000000', 'totalWalletBalance': '530.21334791', 'totalUnrealizedProfit': '0.00000000',
        'totalMarginBalance': '530.21334791', 'totalPositionInitialMargin': '0.00000000', 'totalOpenOrderInitialMargin': '0.00000000',
        'maxWithdrawAmount': '530.2133479100000', 'assets':
        [{'asset': 'USDT', 'walletBalance': '530.21334791', 'unrealizedProfit': '0.00000000', 'marginBalance': '530.21334791',
        'maintMargin': '0.00000000', 'initialMargin': '0.00000000', 'positionInitialMargin': '0.00000000', 'openOrderInitialMargin': '0.00000000',
        'maxWithdrawAmount': '530.2133479100000'}]}
        :return:
        """
        path = "/api/v1/account"
        params = {"timestamp": self.get_current_timestamp(),
                  "recvWindow": self.recv_window
                  }
        return self.request(RequestMethod.GET, path, params, verify=True)

    def get_user_assets(self):
        """
        :return: assets json
        """
        path = '/api/v1/private/user'
        params = {"api_key": self.api_key,
                  "secret_key": self.secret
                  }
        params_string = self.build_parameters(params)

        params_sign = {
            "api_key": self.api_key,
            "sign": str.upper(get_md5_32(params_string))
        }
        return self.request(RequestMethod.POST, path, params_sign)

    def get_unfilled_all(self, symbol: str):
        orders = []
        pos = 0
        while True:
            temp_orders = self.get_unfilled_orders(symbol, offset=pos)
            orders.extend(temp_orders)
            if len(temp_orders) < 100:
                break
            pos += 100
        return orders

    def get_unfilled_orders(self, symbol: str, offset=100):
        """
        :return: assets json
        """
        path = '/api/v1/private/order/pending'
        params = {
            "api_key": self.api_key,
            "limit": 100,
            "market": symbol,
            "offset": offset,
            "secret_key": self.secret
        }
        params_string = self.build_parameters(params)

        params_sign = {
            "api_key": self.api_key,
            "limit": 100,
            "market": symbol,
            "offset": offset,
            "sign": str.upper(get_md5_32(params_string))
        }
        return self.post_bico(path, params_sign)["result"]["records"]

    def delete_orders_all(self, symbol:str):
        try:
            orders = self.get_unfilled_all(symbol)
            print(len(orders))
            for order in orders:
                path = '/api/v1/private/trade/cancel'
                params = {
                    "api_key": self.api_key,
                    "market": symbol,
                    "order_id": order["id"],
                    "secret_key": self.secret
                }
                params_string = self.build_parameters(params)

                params_sign = {
                    "api_key": self.api_key,
                    "market": symbol,
                    "order_id": order["id"],
                    "sign": str.upper(get_md5_32(params_string))
                }
                self.logger.info(self.post_bico(path, params_sign))
        except Exception as ex:
            self.logger.info(ex)

    def delete_orders(self, symbol: str):
        try:
            orders = self.get_unfilled_all(symbol)
            # orders.sort(key=lambda x: float(x['ctime']), reverse=True)  # from high to low

            sell_orders = [order for order in orders if order["side"] == 1]
            buy_orders = [order for order in orders if order["side"] == 2]

            self.logger.info(f"sell orders:{len(sell_orders)}, buy orders:{len(buy_orders)}")

            if len(sell_orders) > 7000:

                sell_orders.sort(key=lambda x: float(x['price']), reverse=False)
                for order in sell_orders[7000:]:
                    # order = orders[i]
                    path = '/api/v1/private/trade/cancel'
                    params = {
                        "api_key": self.api_key,
                        "market": symbol,
                        "order_id": order["id"],
                        "secret_key": self.secret
                    }
                    params_string = self.build_parameters(params)

                    params_sign = {
                        "api_key": self.api_key,
                        "market": symbol,
                        "order_id": order["id"],
                        "sign": str.upper(get_md5_32(params_string))
                    }
                    self.logger.info(self.post_bico(path, params_sign))

            if len(buy_orders) > 7000:

                buy_orders.sort(key=lambda x: float(x['price']), reverse=True)  # from high to low
                for order in buy_orders[7000:]:
                    # order = orders[i]
                    path = '/api/v1/private/trade/cancel'
                    params = {
                        "api_key": self.api_key,
                        "market": symbol,
                        "order_id": order["id"],
                        "secret_key": self.secret
                    }
                    params_string = self.build_parameters(params)

                    params_sign = {
                        "api_key": self.api_key,
                        "market": symbol,
                        "order_id": order["id"],
                        "sign": str.upper(get_md5_32(params_string))
                    }
                    self.logger.info(self.post_bico(path, params_sign))
        except Exception as ex:
            print(repr(ex))
        else:
            return True



