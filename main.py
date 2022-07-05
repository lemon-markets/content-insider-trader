from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
from pytz import utc
import os

from insider_trades.handlers.figi import FigiAPI
from insider_trades.handlers.finviz import FinVizAPI

from insider_trades.transactions import Transactions
from insider_trades.helpers import Helpers

load_dotenv()
helpers: Helpers = Helpers()


def inside_trades():
    figi_api: FigiAPI = FigiAPI()
    finviz_api: FinVizAPI = FinVizAPI()
    venue = helpers.client.market_data.venues.get(os.getenv('MIC')).results[0]
    if not venue.is_open:
        print(f"Venue is not open. Next opening day is {venue.opening_days[0].day}-{venue.opening_days[0].month}"
              f"-{venue.opening_days[0].year}")
        return
    # COMMENT FROM HERE...
    transactions: Transactions = finviz_api.get_transactions()

    gm_tickers = figi_api.find_gm_tickers(transactions.get_tickers())
    transactions.set_gm_tickers(gm_tickers)
    transactions.drop_nontradables()  # drop all gm_tickers labeled 'NA'
    transactions.raw_dataframe.to_csv("transactions.csv")
    # ...UP TO THIS POINT TO USE SAVED DATA

    # uncomment lines below and comment all tagged lines above to use saved data
    # import pandas as pd
    # transactions = Transactions(pd.read_csv("transactions.csv"))

    helpers.get_isins(transactions)

    buy, sell = transactions.get_trade_decisions()
    orders = helpers.place_trades(buy, sell)
    helpers.activate_orders(orders)


if __name__ == '__main__':
    scheduler = BlockingScheduler(timezone=utc)
    
    # reschedule your trades for the future years ad infinitum
    scheduler.add_job(inside_trades(),
                      trigger=CronTrigger(day="mon-fri",
                                          hour=10,
                                          minute=30,
                                          timezone=utc))

    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
