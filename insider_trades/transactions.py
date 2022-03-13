import pandas as pd
from typing import List


class Transactions:
    def __init__(self, dataframe: pd.DataFrame):
        self._df = dataframe

    def get_tickers(self):
        return self._df.loc[:, "Ticker"]

    def set_gm_tickers(self, gm_tickers: list):
        self._df.loc[:, "gm_ticker"] = gm_tickers

    def get_gm_tickers(self):
        return self._df.loc[:, "gm_ticker"]

    def drop_nontradables(self):
        self._df = self._df[self._df.gm_ticker != "NA"]

    def set_isins(self, isins: List[str]):
        self._df.loc[:, "isin"] = isins
        print(self._df)

    def get_trade_decisions(self):
        buy = set()
        sell = set()

        trusted_relationships = ["CEO", "CFO", "COO", "CTO"]

        for index, row in self._df.iterrows():
            transaction_type = row["Transaction"]
            relationship = row["Relationship"]

            # if insider buys large amount, we also want to buy
            if transaction_type == "Buy" and (relationship in trusted_relationships or "Officer" in relationship):
                if row["Number of Shares"] / row["Total Shares"] > 0.01:  # trade >1% of total shares
                    buy.add(row["isin"])
                    print(f'Buy {row["gm_ticker"]}.')

            # if insider sells large amount, we also want to sell
            elif transaction_type == "Sale" and (relationship in trusted_relationships or "Officer" in relationship):
                if row["Number of Shares"] / row["Total Shares"] > 0.01:  # trade >1% of total shares
                    sell.add(row["isin"])
                    print(f'Sell {row["gm_ticker"]}.')

        return buy, sell

    @property
    def raw_dataframe(self) -> pd.DataFrame:
        return self._df
