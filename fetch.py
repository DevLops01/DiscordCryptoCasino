import requests
import json
from data import *
import threading


NODE_URL = "http://127.0.0.1:YOUR_RPC_PORT"  # Enter port number for coins rpc port
NODE_USER = "YOUR_USERNAME"
NODE_PASSWORD = "YOUR_PASSWORD"

# Makes rpc connection


def rpc(method, params=[]):
    payload = json.dumps({
        "jsonrpc": "1.0",
        "method": method,
        "params": params,
    })
    response = requests.post(NODE_URL, auth=(
        NODE_USER, NODE_PASSWORD), data=payload).json()
    return response

# Gets a new address


def getAddress():
    WalletResponse = rpc('getnewaddress')
    print(WalletResponse)
    return WalletResponse

# Gets user balance


def getBalance(userId):
    WalletBalance = rpc('getbalance', [""+userId+""])
    print(WalletBalance)
    return WalletBalance

# Assigns an address to an account based on discord ID


def getNewAddy(userId):
    NewAddy = rpc('getaccountaddress', [""+str(userId)+""])
    print(NewAddy)
    return NewAddy

# Send coins functionality


def sendCoins(uid, toAddress, amount):
    sendTx = rpc('sendfrom', [uid, toAddress, amount])
    # sendTx = rpc('sendfrom', [""+str(uid) + ' ' + str(toAddress) + ' ' + str(amount) + ""])
    print(sendTx)
    return sendTx

# Updates balances


def updateBalances():
    updateWallets = rpc('listaccounts')
    # print(json.dumps(updateWallets['result'], indent=4))
    newBalance = updateWallets['result']
    for i in updateWallets['result']:
        c.execute("SELECT * FROM users WHERE userid=:i",
                  {'i': i})
        getWallets = c.fetchall()
        if getWallets != []:
            c.execute("UPDATE users SET balance=:b WHERE userid=:i",
                      {'i': i, 'b': newBalance[i]})
            con.commit()
    print("balances updated")

# Updates data to database


def sendToDB():
    updateBalances()

# Gets value of cards for blackjack


def getCardValue(Draw):
    global cardValue
    if Draw.startswith("Ace"):
        cardValue = 1
    elif Draw.startswith("Two"):
        cardValue = 2
    elif Draw.startswith("Three"):
        cardValue = 3
    elif Draw.startswith("Four"):
        cardValue = 4
    elif Draw.startswith("Five"):
        cardValue = 5
    elif Draw.startswith("Six"):
        cardValue = 6
    elif Draw.startswith("Seven"):
        cardValue = 7
    elif Draw.startswith("Eight"):
        cardValue = 8
    elif Draw.startswith("Nine"):
        cardValue = 9
    elif Draw.startswith("Ten"):
        cardValue = 10
    elif Draw.startswith("Jack"):
        cardValue = 10
    elif Draw.startswith("Queen"):
        cardValue = 10
    elif Draw.startswith("King"):
        cardValue = 10
    return cardValue

# Set interval function


def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


# set_interval(sendToDB, 60)
# getAddress()
# getBalance("417504362231758858")
