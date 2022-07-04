import os
from typing import List

from lemon import api

from insider_trades.transactions import Transactions


class Helpers:
    def __init__(self):
        self.client = api.create(
            market_data_api_token=os.getenv('DATA_API_KEY'),
            trading_api_token=os.getenv('TRADING_API_KEY'),
            env='paper'
        )

    def get_isins(self, transactions: Transactions):
        isins = []

        for ticker in transactions.get_gm_tickers():
            try:
                instruments = self.client.market_data.instruments.get(search=ticker, type='stock')
            except Exception as e:
                print(e)
                raise
            else:
                if instruments.total > 0:
                    isins.append(instruments.results[0].isin)
                else:
                    isins.append("NA")
        transactions.set_isins(isins)

    def place_trades(self, buy: List[str], sell: List[str]):
        order_ids = []

        expires_at = 0
        quantity = 1

        # place buy orders
        for isin in buy:
            side = "buy"
            price = self.client.market_data.quotes.get_latest(isin=isin).results[0].b * quantity
            if price < 50:
                print(f"Order cannot be placed as total price, €{price}, is less than minimum order amount of €50.")
                continue
            order = self.client.trading.orders.create(
                isin=isin, expires_at=expires_at, quantity=quantity, side=side
            )
            order_ids.append(order.results.id)
            print(f"You are {side}ing {quantity} share(s) of instrument {isin}.")

        positions = self.client.trading.positions.get().results
        positions_isins = []

        for item in positions:
            positions_isins.append(item.isin)

        # place sell orders
        for isin in sell:
            if isin in positions_isins:
                side = "sell"
                price = self.client.market_data.quotes.get_latest(isin=isin).results[0].b / 10000. * quantity
                if price < 50:
                    print(f"Order cannot be placed as total price, €{price}, is less than minimum order amount of €50.")
                    continue
                order = self.client.trading.orders.create(
                    isin=isin, expires_at=expires_at, quantity=quantity, side=side
                )
                order_ids.append(order.results.id)
                print(f"You are {side}ing {quantity} share(s) of instrument {isin}.")
            else:
                print(
                    f"You do not have sufficient holdings of instrument {isin} to place a sell order."
                )

        return order_ids

    def activate_orders(self, order_ids):
        for order_id in order_ids:
            self.client.trading.orders.activate(order_id=order_id)

    def get_opening_days(self):
        return self.client.market_data.venues.get(os.getenv("MIC")).results[0].opening_days
