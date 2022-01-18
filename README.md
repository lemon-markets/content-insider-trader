<h1 align='center'>
  🍋 Following Insider Trades 🍋 
</h1>

## 👋 Introduction 

This is a public [lemon.markets](https://lemon.markets) repository that outlines an **insider trade strategy** using our API. To get a general understanding of the API, please refer to our [documentation](https://docs.lemon.markets). The `insider_trading_bot` scrapes insider trades reported on [finviz](https://finviz.com/insidertrading.ashx?tc=7) and places trades depending on the direction and magnitude of the insider trade. Note that this is only a showcase of the product and should not be used as investment advice. 

A walk-through of this script can be found in [this blog-post]().

## 🏃‍♂️ Quick Start
Not interested in reading a novella before you get started? We get it! To get this project up and running quickly, here's what you need to do:
1. Clone this repository;
2. Sign up to [lemon.markets](https://www.lemon.markets/);
3. Configure your environment variables as outlined in the 'Configuration' section;
4. Modify the trade logic in the `transactions.py` file;
5. Update the parameters (e.g. `quantity`) in the `helpers.py` file;
6. Run the script & see how it performs! 

## 🔌 API Usage

This project uses the [lemon.markets API](https://www.lemon.markets/en-de/for-developers).

lemon.markets is a brokerage API by developers for developers that allows you to build your own experience at the stock market. We will use the Market Data API and Trading API to retrieve the ISIN (unique identifier) that belongs to a particular financial instrument and to place trades. If you do not have a lemon.markets account yet, you can sign up [here](https://dashboard.lemon.markets/signup). 🚀

## ⚙️ Configuration

The script uses several environment variables, configure your .env file as follows:

```python
MIC=XMUN
TRADING_URL=https://paper-trading.lemon.markets/rest/v1/
MARKET_URL=https://data.lemon.markets/v1/
API_KEY=<your-api-key>
OPENFIGI_URL=https://api.openfigi.com/v3/search/
OPENFIGI_KEY=<your-open-figi-key>
SPACE_ID=<your-space-id>
```
Please provide your unique `API_KEY`, `OPENFIGI_KEY` and `SPACE_ID`.

## ❓ What's happening under the hood?
### 📊 Collecting Data
For this project, we collect data from finviz because the data is presented in an easily digestible format. For each insider trade, we can access who placed the trade and how big the trade was (relative to the rest of their position).

To parse the data, we use [BeautifulSoup](https://medium.com/r?url=https%3A%2F%2Fwww.crummy.com%2Fsoftware%2FBeautifulSoup%2Fbs4%2Fdoc%2F), which is a Python package that can extract data from HTML documents.

### 📈 Placing Trades 
Our base project works with a very simple trade rule: replicate all trades by CEOs, CFOs, CTOs, and COOs if the trade constitutes at least 1% of their total holdings (see if you can come up with something a bit more complex 😉):
``` python
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
```
We can then feed this list of ISINs to the lemon.markets API to place and activate our trades. 

## 🤝 Interested in contributing?

This (and all lemon.markets open source projects) is(are) a work in progress. If you are interested in contributing to this repository, simply create a PR and/or contact us at [support@lemon.markets](mailto:support@lemon.markets).

Looking forward to building lemon.markets with you 🍋
