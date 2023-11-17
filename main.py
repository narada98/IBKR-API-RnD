import ib_insync

from ib_insync import IB, Contract, util, Option, Stock
import asyncio
import os
import pandas as pd
import numpy as np


async def explore():
    ib = IB()

    await ib.connectAsync("127.0.0.1", 7497, clientId=0)  # Connect to TWS or Gateway

    symbol = "SPY"
    exchange = "SMART"
    currency = "USD"
    exp_date = "20231124"
    put_call = "c"

    under_stock = Stock(symbol, exchange, currency)

    stock_pr = ib.reqMktData(under_stock)
    stock_data = await ib.reqContractDetailsAsync(under_stock)
    # IB.sleep(2)

    stock_conId = stock_data[0].contract.conId

    print(stock_conId)
    # print("market data for {}: \n{}\n".format(symbol, stock_data))

    print("last price for {} : \n{}\n".format(symbol, stock_pr.last))

    if put_call == "c":
        strike = round(stock_pr.last * 1.05, 0)
    else:
        strike = round(stock_pr.last * 0.95, 0)

    contract = Option(symbol, exp_date, strike, put_call, exchange)

    opt_ticker = ib.reqMktData(contract)

    opt_chain = await ib.reqSecDefOptParamsAsync(underlyingSymbol=symbol, underlyingSecType='STK', futFopExchange='',
                                                 underlyingConId=stock_conId)

    # ib.sleep(2)

    print("options chain : \n{}\n".format(opt_chain))

    # print(util.df(opt_chain))
    opt_df = util.df(opt_chain)
    print(opt_df.columns)
    chain = opt_df.loc[opt_df['exchange'] == exchange]
    # chain = [c for c in opt_chain if c[0].tradingClass == 'SPX' and c.exchange == 'SMART']

    # chain = [c for c in opt_chain if c.tradingClass == 'SPX' and c.exchange == 'SMART']
    # for c in opt_chain:
    # print(c.exchange)

    print(chain['exchange'].iloc[0])
    closest_strike = min(chain['strikes'].iloc[0], key=lambda x: abs(x - strike))

    print(strike)
    print(closest_strike)
    possible_contracts = [Option(symbol=symbol,
                                 lastTradeDateOrContractMonth=exp_date,
                                 strike=opt_strike,
                                 right=right,
                                 exchange=exchange,
                                 tradingClass='SPY')
                          for right in ['p', 'c']
                          # for expiration in chain['expirations'].iloc[0]
                          for opt_strike in chain['strikes'].iloc[0]]

    # print(chain['strikes'].iloc[0])
    actual_contracts = await ib.qualifyContractsAsync(*possible_contracts)
    # ib.sleep(10)
    len(actual_contracts)
    print(actual_contracts)

    ib.disconnect()


async def main():
    await explore()


if __name__ == "__main__":
    # explore()
    asyncio.run(main())
