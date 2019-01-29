import ccxt.kucoin
import ccxt.gateio
import json
import os
import time
from prettytable import PrettyTable
gate = ccxt.gateio({
    'apiKey':'xxxxx',
    'secret':'xxxxx'
})
kucoin = ccxt.kucoin({
    'apiKey':'xxxxx',
    'secret':'xxxxx'
})

#print (balanceA['GRIN'],balanceA['USDT'])
#print(balanceB['GRIN'],balanceB['USDT'])
balanceA = {}
balanceB = {}
initBalanceA = gate.fetch_balance()
initBalanceB = kucoin.fetch_balance()
buyA = sellA = buyB = sellB = buyAAmount = sellAAmount = buyBAmount = sellBAmount = 0
def leagalizeDepth():
    global buyA,sellA, buyB, sellB,buyAAmount , sellAAmount , buyBAmount , sellBAmount 
    buyA = sellA = buyB = sellB = buyAAmount = sellAAmount = buyBAmount = sellBAmount = 0
    #
    depthA = gate.fetch_order_book(symbol = 'GRIN/USDT',limit = None,params={})
    depthB = kucoin.fetch_order_book(symbol = 'GRIN/USDT',limit = None,params={})

    minAmount = 1
    for i in depthA['bids']:
        buyA = i[0]
        buyAAmount += i[1]
        if(buyAAmount > minAmount):
            break
        #print(i)
    
    for i in depthA['asks']:
        sellA = i[0]
        sellAAmount += i[1]
        if(sellAAmount > minAmount):
            break
    
    for i in depthB['bids']:
        buyB = i[0]
        buyBAmount += i[1]
        if(buyBAmount > minAmount):
            break
    for i in depthB['asks']:
        sellB = i[0]
        sellBAmount += i[1]
        if(sellBAmount > minAmount):
            break
    buyA = round(buyA,6)
    buyB = round(buyB,6)
    buyAAmount = round(buyAAmount,6)
    buyBAmount = round(buyBAmount,6) 
    #print('gate: bids:',buyA,buyAAmount,' asks:',sellA,sellAAmount)
    #print('kucoin: bids:',buyB,buyBAmount,' asks:',sellB,sellBAmount)
#leagalizeDepth()
def cancelAllOrders():
    info = gate.fetch_open_orders(symbol = 'GRIN/USDT',since=None,limit=None,params={})
    for i in info:
        print(gate.cancel_order(symbol = 'GRIN/USDT',id = i['id'],params={}))
    info = kucoin.fetch_open_orders(symbol = 'GRIN/USDT',since=None,limit=None,params={})
    for i in info:
        print(kucoin.cancel_order(symbol = 'GRIN/USDT',id = i['id'],params={}))

def checkBalance():
    cancelAllOrders()
    global balanceA,balanceB,buyA,sellA, buyB, sellB,buyAAmount , sellAAmount , buyBAmount , sellBAmount,initBalanceA,initBalanceB
    deltaStocks = initBalanceA['GRIN']['total'] + initBalanceB['GRIN']['total'] - balanceA['GRIN']['total'] - balanceB['GRIN']['total']
    print('gate:','GRIN:',balanceA['GRIN']['total'] ,', USDT:',balanceA['USDT']['total'],'total GRIN:',balanceA['GRIN']['total']+balanceB['GRIN']['total'])
    print('kucoin:','GRIN:',balanceB['GRIN']['total'] ,', USDT:',balanceB['USDT']['total'],'total USDT:',balanceA['USDT']['total']+balanceB['USDT']['total'])
    print('initgate:','GRIN:',initBalanceA['GRIN']['total'] ,', USDT:',initBalanceA['USDT']['total'],'inittotal GRIN',initBalanceA['GRIN']['total']+initBalanceB['GRIN']['total'])
    print('initkucoin:','GRIN:',initBalanceB['GRIN']['total'] ,', USDT:',initBalanceB['USDT']['total'],'inittotal USDT',initBalanceA['USDT']['total']+initBalanceB['USDT']['total'])
    print('deltaStocks:',deltaStocks)
    maxDeltaStocks = 1
    if(deltaStocks > maxDeltaStocks):#
        if(sellA > sellB):#
            print(gate.create_order(symbol='GRIN/USDT',type = 'limit',side = 'sell',amount = deltaStocks,price = sellA))
        else:
            print(kucoin.create_order(symbol='GRIN/USDT',type = 'limit',side = 'sell',amount = deltaStocks,price = sellA))
    if(deltaStocks < -maxDeltaStocks):#
        if(buyA < buyB):#
            print(gate.create_order(symbol='GRIN/USDT',type = 'limit',side = 'buy',amount = -deltaStocks,price = buyA))
        else:
            print(kucoin.create_order(symbol='GRIN/USDT',type = 'limit',side = 'buy',amount = -deltaStocks,price = buyB))

checkBalanceCount = 0
def work():
    global balanceA,balanceB,buyA,sellA, buyB, sellB,buyAAmount , sellAAmount , buyBAmount , sellBAmount,checkBalanceCount
    maxAmountA = maxAmountB = 0
    balanceA = gate.fetch_balance()
    balanceB = kucoin.fetch_balance()
    leagalizeDepth()
    if(checkBalanceCount <= 0):
        print('checking balance')
        checkBalance()
        checkBalanceCount = 300
        return 
    checkBalanceCount-=1
    #A->B   
    deltaPriceA = buyB - sellA
    if(deltaPriceA /((buyA+sellA+buyB+sellB)/4) > 0.01):
        maxAmountA = min(balanceB['GRIN']['free'],min(sellAAmount,min(buyBAmount,balanceA['USDT']['free']/sellA))) * 0.999
        if(maxAmountA > 1):
            print('gate -> kucoin',min(maxAmountA,1),deltaPriceA)
            print(gate.create_order(symbol='GRIN/USDT',type = 'limit',side = 'buy',amount = min(maxAmountA,1),price = sellA))
            print(kucoin.create_order(symbol='GRIN/USDT',type = 'limit',side = 'sell',amount = min(maxAmountA,1),price = buyB))
    
    #B->A   
    deltaPriceB = buyA - sellB
    if(deltaPriceB /((buyA+sellA+buyB+sellB)/4) > 0.01):
        maxAmountB = min(balanceA['GRIN']['free'],min(sellBAmount,min(buyAAmount,balanceB['USDT']['free']/sellB))) * 0.999
        if(maxAmountB > 1):
            print('kucoin -> gate',min(maxAmountB,1),deltaPriceB)
            print(kucoin.create_order(symbol='GRIN/USDT',type = 'limit',side = 'buy',amount = min(maxAmountB,1),price = sellB))
            print(gate.create_order(symbol='GRIN/USDT',type = 'limit',side = 'sell',amount = min(maxAmountB,1),price = buyA))
    deltaPriceA=round(deltaPriceA,6)
    deltaPriceB=round(deltaPriceB,6)
    v = PrettyTable(['EXCHANGE','GRIN','USDT','BUY','BUYAMOUNT','SELL','SELLAMOUNT'])
    v.align["EXCHANGE"] = "l"
    v.padding_width = 3
    v.add_row(['Gate',balanceA['GRIN']['total'],balanceA['USDT']['total'],buyA,buyAAmount,sellA,sellAAmount])
    v.add_row(['KuCoin',balanceB['GRIN']['total'],balanceB['USDT']['total'],buyB,buyBAmount,sellB,sellBAmount])
    v.add_row(['initGate',initBalanceA['GRIN']['total'],initBalanceA['USDT']['total'],'X','X','X','X'])
    v.add_row(['initKuCoin',initBalanceB['GRIN']['total'],initBalanceB['USDT']['total'],'X','X','X','X'])
    v.add_row(['total',balanceA['GRIN']['total']+balanceB['GRIN']['total'],balanceA['USDT']['total']+balanceB['USDT']['total'],'X','X','X','X'])
    v.add_row(['initTotal',initBalanceA['GRIN']['total']+initBalanceB['GRIN']['total'],initBalanceA['USDT']['total']+initBalanceB['USDT']['total'],'X','X','X','X'])
    v.add_row(['deltaPriceA',deltaPriceA,'deltaPriceB',deltaPriceB,'X','X','X'])
    v.add_row(['delta',round(balanceA['GRIN']['total']+balanceB['GRIN']['total']-initBalanceA['GRIN']['total']-initBalanceB['GRIN']['total'],6),round(balanceA['USDT']['total']+balanceB['USDT']['total']-initBalanceA['USDT']['total']-initBalanceB['USDT']['total'],6),'X','X','X','X'])
    
    print(v)
    #print(deltaPriceA,maxAmountA,deltaPriceB,maxAmountB)


error_times=0
while(True):
    try:
        work()
        time.sleep(1)
    except Exception as e:
        error_times+=1
        print(e,error_times)

'''
depthA = gate.fetch_order_book(symbol = 'GRIN/USDT',limit = None,params={})
print(depthA)
depthB = kucoin.fetch_order_book(symbol = 'GRIN/USDT',limit = None,params={})
print(depthB)
'''
