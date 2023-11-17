import ib_insync

from ib_insync import IB, Contract, util, Option, Stock, Order, MarketOrder, StopOrder, LimitOrder
import asyncio
import os
import pandas as pd
import numpy as np


def print_orders(ib):
    print('fills : {}'.format(len(ib.fills())))
    for fill in ib.fills():
        print(fill)
    print()
    print('open Trades : {}'.format(len(ib.openTrades())))
    for open_tr in ib.openTrades():
        print(open_tr)
    print()


def print_positions(ib):
    positions = ib.positions()
    for pos in positions:
        print(pos)
    print()


def print_portfolio(ib):
    portfolio = ib.portfolio()
    for item in portfolio:
        print(item)


def trade():
    ib = IB()

    ib.connect("127.0.0.1", 7497, clientId=0)  # Connect to TWS or Gateway
    order = MarketOrder(action='buy', totalQuantity=1, tif='GTC')
    limit_order = LimitOrder(action='sell', totalQuantity=1, lmtPrice=0, tif='GTC')

    opt_contract = Contract(secType='OPT', conId=616713012, symbol='TSLA', lastTradeDateOrContractMonth='20231118',
                            strike=222.5, right='c', multiplier='100', exchange='SMART', currency='USD',
                            localSymbol='TSLA  231117C00220000', tradingClass='TSLA')
    opt_contract = Contract(secType='OPT', symbol='TSLA', lastTradeDateOrContractMonth="20231117", strike=230,
                            right='C', exchange="SMART")
    inx_opt = Contract(secType='OPT', conId=654559982, symbol='SPY', lastTradeDateOrContractMonth='20231117',
                       strike=443.0, right='C', multiplier='100', exchange='SMART', currency='USD',
                       localSymbol='SPY   231117C00443000', tradingClass='SPY')
    inx_opt_2 = Contract(secType='OPT', symbol='SPY', lastTradeDateOrContractMonth='20231117', strike=449.0, right='C',
                         exchange='SMART')

    con_data_dict = inx_opt_2.dict()
    # possible_cons = ib.reqContractDetails(con)
    qualified_cons = ib.qualifyContracts(inx_opt_2)
    ib.sleep(3)

    if len(qualified_cons) != 0:
        # possible_contracts[idx].conId = qualified_cons[0].conId
        conId = qualified_cons[0].conId
        con_data_dict['conId'] = conId
    complete_con = Contract(**con_data_dict)

    # trade1 = ib.placeOrder(complete_con, order)
    # print('order : \n{}\n'.format(trade1))

    open_trades = ib.openTrades()

    # print_positions(ib)
    # print_portfolio(ib)
    print_orders(ib)

    filled_trades = ib.fills()
    ib.sleep(5)
    for filled_trade in filled_trades:
        # print(filled_trade.contract.conId, complete_con.conId)
        if filled_trade.contract.conId == complete_con.conId:
            avg_price = filled_trade.execution.avgPrice
            print('selected filled trade : \n{}'.format(filled_trade))
            print()
            sell_limit_price = avg_price * 0.50
            limit_order.lmtPrice = sell_limit_price
            limit_sell = ib.placeOrder(complete_con, limit_order)
            print('limit sell order : \n{}\n'.format(limit_sell))
            ib.sleep(5)

            try:
                open_trades = ib.openTrades()
                open_trade_1 = open_trades[-1]
                print(open_trade_1)
                while not open_trade_1.isDone():
                    print('waiting until fill')
                    ib.sleep(1)
                print('order filled')
            except:
                print('order filled')
                print()
            break

    print_orders(ib)

    # limit_order.lmtPrice =

    # st_contract = Stock('TSLA', 'SMART', 'USD')
    # trade2 = ib.placeOrder(st_contract, order)
    # print(trade2)

    # print_positions(ib)
    # print_portfolio(ib)
    # print_orders(ib)

    # conId = 76792991
    # print(ib.fills()[0].contract)
    # print()
    #
    # stop_order = StopOrder('sell', totalQuantity=1, stopPrice=227.60)
    # stop1 = ib.placeOrder(ib.fills()[0].contract, stop_order)
    # print('fills : {}\n{}\n'.format(len(ib.fills()), ib.fills()))
    # print('openTrades : {}\n{}\n'.format(len(ib.openTrades()), ib.openOrders()))

    ib.disconnect()


def demo_limit_order():

    ib = IB()
    ib.connect("127.0.0.1", 7497, clientId=0)
    # print_positions(ib)
    # print_portfolio(ib)
    print_orders(ib)
    ib.disconnect()


if __name__ == "__main__":

    demo_limit_order()
    # trade()
