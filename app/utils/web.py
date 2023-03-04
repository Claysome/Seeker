"""
@author: Claysome
@email: claysomes@outlook.com
"""

import ccxt.async_support as ccxt
import asyncio
import json
import websockets


class WebSocketClient:
    def __init__(self, exchange, symbol):
        self.exchange = exchange
        self.symbol = symbol
        self.url = None
        self.orderbook = {'bids': {}, 'asks': {}}
        self.ws = None

    async def load_markets(self):
        await self.exchange.load_markets()

    async def on_message(self, message):
        data = json.loads(message)
        if 'bids' in data:
            self.orderbook['bids'] = dict(data['bids'])
        if 'asks' in data:
            self.orderbook['asks'] = dict(data['asks'])
        print(f"Orderbook updated for {self.symbol}: {self.orderbook}")

    async def subscribe(self):
        if self.exchange.has['fetchOrderBook']:
            await self.load_markets()
            symbol = self.exchange.market(self.symbol)['id']
            self.url = self.exchange.urls['api']['ws']
            self.url += f"/ws/{symbol.lower()}@depth"
            self.ws = await websockets.connect(self.url)
            await self.ws.send('{"method": "SUBSCRIBE", "params": ["' + symbol.lower() + '@depth"], "id": 1}')
            async for message in self.ws:
                await self.on_message(message)
            await self.exchange.close()
            await self.ws.close()
            await self.exchange.asyncio_session.close()

    async def close(self):
        await self.exchange.close()
        if self.ws is not None:
            await self.ws.close()


if __name__ == '__main__':
    exchange = ccxt.binance({
        'proxies': {'http': '127.0.0.1:7890', 'https': '127.0.0.1:7890'},
        'timeout': 30000  # increase the timeout value to 30 seconds
    })
    symbol = 'BTC/USDT'
    client = WebSocketClient(exchange, symbol)
    try:
        async with exchange, client.ws:
            await client.subscribe()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await client.close()
