import ib_insync

from ib_insync import IB, Contract, util, Option, Stock, Order, MarketOrder
import asyncio
import os
import pandas as pd
import numpy as np


def trade():
    ib = IB()

    ib.connect("127.0.0.1", 7497, clientId=0)  # Connect to TWS or Gateway

    print('fills : {}'.format(len(ib.fills())))
    for fill in ib.fills():
        print(fill)
    print()
    print('open Trades : {}'.format(len(ib.openTrades())))
    for open_tr in ib.openTrades():
        print(open_tr)
    print()
    # print('executions : \n{}\n'.format(ib.executions()))

    ib.disconnect()


if __name__ == "__main__":
    trade()
