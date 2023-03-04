import ccxt

binance = ccxt.binance({
    'proxies': {'http': '127.0.0.1:7890', 'https': '127.0.0.1:7890'},
    'timeout': 30000 # increase the timeout value to 30 seconds
})

symbol = 'BTC/USDT'
balance = binance.fetch_bids_asks()

print(balance)

# change the above function to asynchronous function
async def connect(symbol, balance):
    await binance.fetch_bids_asks()

async def main():
    client = await connect(symbol, balance)
    print(client)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())