# ETF Dowloader
Functions to mass download ETF tickers, price, and volume data from an exchange or an country.

## Example Usage

Scrape all ETF tickers listed NYSE from Interactive Brokers (IB). Valid exchange strings can be found at Interactive Brokers's website: https://www.interactivebrokers.com/en/index.php?f=1562&p=north_america
    
    get_exchange_ETF_tickers('nyse')
Scrape all ETF tickers list the US and Canada

    get_country_ETF_tickers(['chx', 'bex', 'amex', 'arca'])
    get_country_ETF_tickers(['pure', 'chix_ca', 'omega', 'tse'])

Download SPY's price and volume history from yahoo finance   

    download_ETF_hist('SPY')
      
Download SPY's top 10 holdings from yahoo finance   

    get_ETF_holdings('SPY')
Download SPY's summary and AUM from yahoo finance

    get_ETF_sum_AUM('SPY') 

