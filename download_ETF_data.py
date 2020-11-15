import requests
from bs4 import BeautifulSoup
import pandas as pd
from pandas import DataFrame
import yfinance as yf
import time
import numpy as np
from typing import List


def get_exchange_ETF_tickers(exchange: str) -> DataFrame:
    """
    Scrapes ETF tickers for an exhange from IB product listing webpage
    exchange: string, needs to match the string used in IB link. Valid exchange codes are given in
    https://www.interactivebrokers.com/en/index.php?f=1562&p=north_america
    """
    html = requests.get('https://www.interactivebrokers.com/en/index.php?f=567&exch=' + exchange).text
    soup = BeautifulSoup(html, 'lxml')
    table = soup.find('h3', string='Exchange Traded Funds').find_next('table')
    heads = table.find('thead').find('tr').find_all('th')
    table_head = [head.text for head in heads]
    rows = table.find('tbody').find_all('tr')
    table_cotent = [[cell.text for cell in row.find_all('td')] for row in rows]
    df = pd.DataFrame(table_cotent, columns=table_head)
    return df


def get_country_ETF_tickers(exchanges: List[str]) -> DataFrame:
    """
    Get ETF info for a country by combinding info from several exchanges
    exchanges: list of exchanges in a country. Valid exchange codes are given in
    https://www.interactivebrokers.com/en/index.php?f=1562&p=north_america
    """
    ETFs = pd.DataFrame()
    for exchange in exchanges:
        ETFs = ETFs.append(get_exchange_ETF_tickers(exchange))
    ETFs = ETFs.rename(columns={'Fund Description (Click link for more details)': 'fund_desp', 'Symbol': 'ticker'}) \
        .drop(columns=['IB Symbol', 'Currency'])
    return ETFs


def download_ETF_hist(ticker: str, sleep_sec: float) -> DataFrame:
    """
    sleep_sec: seconds to pause after downloading the ticker's data
    """
    print(ticker)
    ETF = yf.Ticker(ticker)
    ETF_price = ETF.history(period='max', auto_adjust=True)
    ETF_price = ETF_price.assign(date=ETF_price.index,
                                 ticker=ticker,
                                 r=ETF_price.Close.pct_change(),
                                 volume=ETF_price.Volume * ETF_price.Close)
    time.sleep(sleep_sec)
    return ETF_price[['date', 'ticker', 'r', 'volume']].dropna(subset=['r', 'volume'])


def get_ETF_holdings(ticker: str) -> str:
    """
    This function scraps ETF holdings  from Yahoo finance
    """
    html = requests.get(f'https://finance.yahoo.com/quote/{ticker}/holdings?p={ticker}').text
    soup = BeautifulSoup(html, 'lxml')
    try:
        table_rows = soup.find('div', attrs={'data-test': 'top-holdings'}).find('table').find('tbody').find_all('tr')
        ETF_holdings = '|'.join([row.find('td').text for row in table_rows])
    except:
        ETF_holdings = np.nan
    time.sleep(1)
    return ETF_holdings


def get_ETF_info(ticker: str) -> list:
    """
    This function downloads other ETF info using yfinance get_info method.
    """
    ETF = yf.Ticker(ticker)
    try:
        ETF_info = ETF.get_info()
        ETF_summary = ETF_info['longBusinessSummary']
        ETF_mktcap = ETF_info['totalAssets']
    except:
        ETF_summary = np.nan
        ETF_mktcap = np.nan
    time.sleep(1)
    return [ETF_summary, ETF_mktcap]


# download ETF  summary, and holdings in Canada
def get_CA_ETF_tickers() -> DataFrame:
    ETF_info_CA = get_country_ETF_tickers(['pure', 'chix_ca', 'omega', 'tse'])
    ETF_info_CA = ETF_info_CA \
        .assign(ticker=ETF_info_CA.ticker.str.replace('.', '-'))
    ETF_info_CA = ETF_info_CA.assign(ticker=ETF_info_CA.ticker + '.TO') \
        .drop_duplicates()
    return ETF_info_CA.assign(fund_summary=[get_ETF_info(ticker)[0] for ticker in ETF_info_CA.ticker]) \
        .assign(fund_holdings=[get_ETF_holdings(ticker) for ticker in ETF_info_CA.ticker])

# download ETF  summary, and holdings in US
def get_US_ETF_tickers() -> DataFrame:
    ETF_info_US = get_country_ETF_tickers(['chx', 'bex', 'amex', 'arca']) \
        .drop_duplicates()
    return ETF_info_US.assign(fund_summary=[get_ETF_info(ticker)[0] for ticker in ETF_info_US.ticker]) \
        .assign(fund_holdings=[get_ETF_holdings(ticker) for ticker in ETF_info_US.ticker])

# download Canada ETF price and volume from yahoo finance
def get_CA_ETF() -> DataFrame:
    return pd.concat([download_ETF_hist(ETF, 1) for ETF in get_CA_ETF_tickers().ticker])

# download US ETF price and volume from yahoo finance
def get_US_ETF() -> DataFrame:
    return pd.concat([download_ETF_hist(ETF, 1) for ETF in get_US_ETF_tickers().ticker])
