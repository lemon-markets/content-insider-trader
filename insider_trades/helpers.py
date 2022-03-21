import datetime
import os
from typing import List

from insider_trades.handlers.lemon import LemonMarketsAPI
from insider_trades.transactions import Transactions


class Helpers:
    def __init__(self, lemon_api: LemonMarketsAPI):
        self._lemon_api = lemon_api

    def get_isins(self, transactions: Transactions):
        isins = []

        for ticker in transactions.get_gm_tickers():
            try:
                instrument = self._lemon_api.get_instrument(ticker)
            except Exception as e:
                print(e)
                raise
            else:
                if instrument.get("total") > 0:
                    isins.append(instrument.get("results")[0].get("isin"))
                else:
                    isins.append("NA")
        transactions.set_isins(isins)

    def place_trades(self, buy: List[str], sell: List[str]):
        orders = []

        expires_at = "p0d"

        # place buy orders
        for isin in buy:
            side = "buy"
            quantity = 1
            order = self._lemon_api.place_order(
                isin, expires_at, quantity, side
            )
            orders.append(order)
            print(f"You are {side}ing {quantity} share(s) of instrument {isin}.")

        positions = self._lemon_api.get_positions()
        positions_isins = []

        for item in positions:
            positions_isins.append(item.get("isin"))

        # place sell orders
        for isin in sell:
            if isin in positions_isins:
                side = "sell"
                quantity = 1
                order = self._lemon_api.place_order(
                    isin, expires_at, quantity, side
                )
                orders.append(order)
                print(f"You are {side}ing {quantity} share(s) of instrument {isin}.")
            else:
                print(
                    f"You do not have sufficient holdings of instrument {isin} to place a sell order."
                )

        return orders

    def activate_order(self, orders):
        for order in orders:
            self._lemon_api.activate_order(order["results"].get("id"))
            print(f'Activated {order["results"].get("isin")}')
        return orders



