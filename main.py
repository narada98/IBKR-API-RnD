import ib_insync
import sys
from ib_insync import IB, Contract, util, Option, Stock, Order, MarketOrder, StopOrder, LimitOrder
import pandas as pd
import numpy as np


# prints all order (open orders, filled orders) of CURRENT session
def print_orders(ib):
    print('fills : {}'.format(len(ib.fills())))
    for fill in ib.fills():
        print(fill)
    print()
    print('open Trades : {}'.format(len(ib.openTrades())))
    for open_tr in ib.openTrades():
        print(open_tr)
    print()


# prints positions - not dependant on session
def print_positions(ib):
    positions = ib.positions()
    for pos in positions:
        print(pos)
    print()


# prints portfolio items - not dependant on session
def print_portfolio(ib):
    portfolio = ib.portfolio()
    for item in portfolio:
        print(item)


def explore():
    # defining and connecting to IB
    ib = IB()
    ib.connect("127.0.0.1", 7497, clientId=0)  # Connect to TWS or Gateway

    # options definitions - exchange and currency are constant
    symbol = "SPY"
    exchange = "SMART"
    currency = "USD"
    exp_date = "20231124"

    # defining the underlying symbol's stock
    under_stock = Stock(symbol, exchange, currency)

    # getting the latest market data and full contract details of the stock
    stock_pr = ib.reqMktData(under_stock)
    latest_stock_pr = stock_pr.last
    print("last price for {} : \n{}\n".format(symbol, latest_stock_pr))

    stock_data = ib.reqContractDetails(under_stock)
    IB.sleep(2)

    # get the contract ID from the full contract details of the stock
    stock_conId = stock_data[0].contract.conId

    # Defining strike values for calls and puts
    call_strike = round(latest_stock_pr * 1.05, 0)
    put_strike = round(latest_stock_pr * 0.95, 0)

    # getting options chain from IB
    opt_chain = ib.reqSecDefOptParams(underlyingSymbol=symbol, underlyingSecType='STK', futFopExchange='',
                                      underlyingConId=stock_conId)

    print("options chain : \n{}\n".format(opt_chain))

    # converting opt chain into a pandas Dataframe for easier processing
    opt_df = util.df(opt_chain)
    # filtering with exchange since we only need SMART exchange
    chain = opt_df.loc[opt_df['exchange'] == exchange]

    # Filtering out the closest strike prices from the available strike prices from the options chain
    differences = [abs(strike_val - latest_stock_pr) for strike_val in chain['strikes'].iloc[0]]
    smallest_idx = pd.Series(differences).nsmallest(40).index
    closest_strikes = (pd.Series(chain['strikes'].iloc[0]).iloc[smallest_idx]).to_list()

    # defining the all the possible option contracts
    possible_contracts = [Option(symbol=symbol,
                                 lastTradeDateOrContractMonth=exp_date,
                                 strike=opt_strike,
                                 right=right,
                                 exchange=exchange,
                                 tradingClass='SPY')
                          for right in ['P', 'C']
                          for opt_strike in closest_strikes]

    # checking and filtering out possible contacts and get only the qualified (existing) contracts
    print('\nQualifying Contracts\n')
    complete_cons = []
    for idx, con in enumerate(possible_contracts):

        con_data_dict = con.dict()
        qualified_cons = ib.qualifyContracts(con)

        if len(qualified_cons) != 0:
            conId = qualified_cons[0].conId
            con_data_dict['conId'] = conId
            complete_cons.append(Contract(**con_data_dict))

    # creating a dataframe with all qualified contracts for easier processing
    good_opts_df = pd.DataFrame()
    for complete_con in complete_cons:
        contract_dict = complete_con.dict()
        contract_dict['contract_obj'] = complete_con
        good_opts_df = pd.concat([good_opts_df, pd.DataFrame([contract_dict])], ignore_index=True)

    print(good_opts_df)

    # selecting the call option that has the closest possible strike to desired strike
    call_df = good_opts_df.loc[good_opts_df.right == 'C']
    call_df['abs_difference'] = (call_df['strike'] - call_strike).abs()
    call_df_sorted = call_df.sort_values(by=['abs_difference']).reset_index(drop=True)
    print(call_df_sorted[['abs_difference', 'strike']])

    selected_call = call_df_sorted['contract_obj'].iloc[1]
    print('selected call strike : {} | desired strike : {}'.format(selected_call.strike, call_strike))

    # selecting the put option that has the closest possible strike to desired strike
    put_df = good_opts_df.loc[good_opts_df.right == 'P']
    put_df['abs_difference'] = (put_df['strike'] - put_strike).abs()
    put_df_sorted = put_df.sort_values(by=['abs_difference']).reset_index(drop=True)
    print(put_df_sorted[['abs_difference', 'strike']])
    print()

    selected_put = put_df_sorted['contract_obj'].iloc[1]
    print('selected put strike : {} | desired strike : {}'.format(selected_put.strike, put_strike))

    # Defining market order objects. need to define separate objects for each order
    call_order = MarketOrder(action='buy', totalQuantity=1, tif='GTC')
    put_order = MarketOrder(action='buy', totalQuantity=1, tif='GTC')

    # Placing orders
    call_trade = ib.placeOrder(selected_call, call_order)
    print('\ncall trade : \n{}'.format(call_trade))

    put_trade = ib.placeOrder(selected_put, put_order)
    print('\nput trade : \n{}'.format(put_trade))

    # waiting for call order to fill - to do : Need to either wait for both or do this waiting in parallel
    try:
        while not call_trade.isDone():
            print('waiting until call order fill')
            ib.sleep(0.5)
        print('order filled')
    except:
        print('order filled')
        print()

    # Gets all the filled orders and places limit orders to sell
    # to do : This needs to be improved to search based of Order ID, not Contract ID

    filled_trades = ib.fills()
    ib.sleep(5)
    for filled_trade in filled_trades:
        if filled_trade.contract.conId == selected_call.conId:
            avg_price = filled_trade.execution.avgPrice
            print('selected filled call trade : \n{}'.format(filled_trade))
            print()
            sell_limit_price = round(avg_price * 1.20, 2)
            call_limit_order = LimitOrder(action='sell', totalQuantity=1, lmtPrice=sell_limit_price, tif='GTC')
            print('\nstop price : {}\n'.format(sell_limit_price))
            limit_sell = ib.placeOrder(selected_call, call_limit_order)
            print('sell order : \n{}\n'.format(limit_sell))
            break

    for filled_trade in filled_trades:
        if filled_trade.contract.conId == selected_put.conId:
            avg_price = filled_trade.execution.avgPrice
            print('selected filled put trade : \n{}'.format(filled_trade))
            print()
            sell_limit_price = round(avg_price * 1.20, 2)
            put_limit_order = LimitOrder(action='sell', totalQuantity=1, lmtPrice=sell_limit_price, tif='GTC')
            print('\nstop price : {}\n'.format(sell_limit_price))
            limit_sell = ib.placeOrder(selected_put, put_limit_order)
            print('stop sell order : \n{}\n'.format(limit_sell))
            break

    print_orders(ib)

    ib.disconnect()


if __name__ == "__main__":
    explore()

    # # Use below section to display portfolio items
    # ib = IB()
    # ib.connect("127.0.0.1", 7497, clientId=0)

    # print_portfolio(ib)

    # ib.disconnect()

