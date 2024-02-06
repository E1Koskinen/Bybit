import json
import websocket
import threading
import time

TRADE_PAIR = 'BTCUSDT'


# Linear & inverse:
# Level 1 data, push frequency: 10ms
# Level 50 data, push frequency: 20ms
# Level 200 data, push frequency: 100ms
# Level 500 data, push frequency: 100ms

# Spot:
# Level 1 data, push frequency: 10ms
# Level 50 data, push frequency: 20ms

# Option:
# Level 25 data, push frequency: 20ms
# Level 100 data, push frequency: 100ms

DEPTH = 50


ifAnyPriceReceivedFromBybit = False


bybit_api_url = "wss://stream.bybit.com/v5/public/spot"


def bybit_on_message(ws, message):
    global current_bybit_price
    global ifAnyPriceReceivedFromBybit

    #print("got msg from bybit")
    #print(str(message))
    data = json.loads(message)

    if 'ret_msg' in data and 'success' in data:
        print('websocket open is success')
        return
    
    if 'ret_msg' in data:
        print("pong received from bybit")
        print("-------------------------------")
        print(str(data))
        print("-------------------------------")
        return

def bybit_on_error(ws, error):
    print("WebSocket error:", error)

def bybit_on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")

def bybit_on_open(ws):
    print("opening bybit ws... ", end="")
    # Subscribe to the trade data stream for a specific symbol (e.g., BTCUSD)
    subscribe_msg = {
        "op": "subscribe",
        #"args": ["publicTrade.BTCUSDT"]
        "args": ['orderbook.'+ str(DEPTH) + '.' + TRADE_PAIR]
        
    }
    ws.send(json.dumps(subscribe_msg))
    print("done")



def pingBybitInBackground(ws):
    while True:
        time.sleep(15)
        if ifAnyPriceReceivedFromBybit:
            print("ping bybit")
            ws.send(json.dumps({"op": "ping"}))


if __name__ == "__main__":
    
    ws = websocket.WebSocketApp(bybit_api_url, on_message=bybit_on_message, on_error=bybit_on_error, on_close=bybit_on_close)
    ws.on_open = bybit_on_open

    # start checking sell orders amount in background thread
    t = threading.Thread(target=pingBybitInBackground, kwargs={'ws': ws})
    t.daemon = True
    t.start()

    ws.run_forever()


    
        