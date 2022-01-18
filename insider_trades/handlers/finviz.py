import requests
import re
from bs4 import BeautifulSoup
import pandas as pd

from insider_trades.transactions import Transactions


class FinVizAPI:
    def get_transactions(self) -> Transactions:
        insider_trades = []

        url = "https://finviz.com/insidertrading.ashx"
        # this header can be anything, we need to feed the request a dummy header to successfully scrape this data
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/70.0.3538.77 Safari/537.36'}
        page = requests.get(url, headers=headers)

        soup = BeautifulSoup(page.content, "html.parser")

        # find all tr tags with class starting with "insider"
        page_trades = soup.find_all("tr", class_=re.compile("^insider"))

        for page_trade in page_trades:
            trade = page_trade.find_all("td")

            us_ticker = trade[0].string
            owner = trade[1].string

            relationship = trade[2].string
            date = trade[3].string
            transaction = trade[4].string
            # finviz uses thousand separator, remove to ensure float conversion works
            cost = float(trade[5].string.replace(",", ""))
            num_shares = float(trade[6].string.replace(",", ""))
            value = float(trade[7].string.replace(",", ""))
            tot_shares = float(trade[8].string.replace(",", ""))
            publish_date = trade[9].string

            trade_info = [us_ticker, owner, relationship, date, transaction, cost, num_shares, value, tot_shares,
                          publish_date]
            insider_trades.append(trade_info)

        column_names = ["Ticker", "Owner", "Relationship", "Date", "Transaction", "Cost", "Number of Shares",
                        "Value ($)", "Total Shares", "Publish Date"]

        transactions = pd.DataFrame(insider_trades, columns=column_names)
        print(transactions.head())

        return Transactions(transactions)
