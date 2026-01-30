import ccxt.async_support as ccxt
import asyncio

PAIRS = [
'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'XRP/USDT', 'TRX/USDT', 'ADA/USDT', 'DOGE/USDT',
'PEPE/USDT', 'FIL/USDT', 'SOL/USDT', 'TRUMP/USDT', 'SHIB/USDT',
'SUI/USDT', 'HBAR/USDT', 'AVAX/USDT', 'MNT/USDT', 'TON/USDT',
'ARB/USDT', 'LTC/USDT', 'NEAR/USDT', 'HYPE/USDT', 'LINK/USDT',
'BCH/USDT', 'XLM/USDT', 'LEO/USDT', 'XMR/USDT', 'DOT/USDT',
'BSV/USDT', 'ETC/USDT', 'S/USDT', 'APE/USDT', 'BONK/USDT',
'UNI/USDT', 'ATOM/USDT', 'BTT/USDT', 'AAVE/USDT'
]

# most popular excanges
EXCHANGES = [
'binance', 'bitget', 'bitmart', 'bybit', 
'gate', 'htx', 'kucoin','mexc', 'okx', 'xt'
]

min_asks = {} # {PAIR : [price, exchange_id]}
max_bids = {}

lock = asyncio.Lock()

def add_to_min_asks(symbol, price, exchange_id):
    if symbol not in min_asks or price < min_asks[symbol][0]:
        min_asks[symbol] = [price, exchange_id]

def add_to_max_bids(symbol, price, exchange_id):
    if symbol not in max_bids or price > max_bids[symbol][0]:
        max_bids[symbol] = [price, exchange_id]

async def fetch_from_exchange(exchange_id):
    exchange = getattr(ccxt, exchange_id)()
    try:
        await exchange.load_markets()
    except Exception as e:
        print(f"loading markets {exchange_id}: {e}")
        return

    for symbol in PAIRS:
        if not exchange.markets.get(symbol):
            continue
        try:
            order_book = await exchange.fetch_order_book(symbol)
            bids = order_book.get('bids', [])
            asks = order_book.get('asks', [])

            if not bids or not asks:
                continue

            top_bid = bids[0]
            top_ask = asks[0]

            i = 1
            while (i < len(bids) and top_bid[1] * top_bid[0] < 500):
                top_bid = bids[i]
                i += 1

            i = 1
            while (i < len(bids) and top_ask[1] * top_ask[0] < 500):
                top_ask = asks[i]
                i += 1

            add_to_min_asks(symbol, top_ask[0], exchange_id)
            add_to_max_bids(symbol, top_bid[0], exchange_id)

        except Exception as ex:
            print(f"[{exchange_id}] Error fetching {symbol}: {ex}")

    await exchange.close()

async def scan_exchanges():
    min_asks.clear()
    max_bids.clear()
    tasks = [fetch_from_exchange(exchange_id) for exchange_id in EXCHANGES]
    await asyncio.gather(*tasks)

    found = {} # {PAIR : [price, exchange_id]}

    for symbol in PAIRS:
        if symbol in max_bids and symbol in min_asks:
            bid_price = max_bids[symbol][0]
            ask_price = min_asks[symbol][0]
            if bid_price > ask_price:
                diff_in_per = (bid_price - ask_price) / bid_price * 100
                if diff_in_per > 0.59:
                    print(f"{symbol} {max_bids[symbol]} {min_asks[symbol]} diff {diff_in_per:.2f}%")
                    found[symbol] = [max_bids[symbol], min_asks[symbol], round(diff_in_per, 2)]

    return found
