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
        print(f'Scraping tickers for ETFs listed in {exchange}...')
        ETFs = ETFs.append(get_exchange_ETF_tickers(exchange))
    ETFs = ETFs.rename(columns={'Fund Description (Click link for more details)': 'fund_desp', 'Symbol': 'ticker'}) \
        .drop(columns=['IB Symbol', 'Currency'])
    return ETFs


def download_ETF_hist(ticker: str, sleep_sec=1) -> DataFrame:
    """
    sleep_sec: seconds to pause after downloading the ticker's data
    """
    print(f'Downloading {ticker} price and volume...')
    ETF = yf.Ticker(ticker)
    ETF_price = ETF.history(period='max', auto_adjust=True)
    ETF_price = ETF_price.assign(date=ETF_price.index,
                                 ticker=ticker,
                                 r=ETF_price.Close.pct_change(),
                                 volume=ETF_price.Volume * ETF_price.Close)
    time.sleep(sleep_sec)
    return ETF_price[['date', 'ticker', 'r', 'volume']].dropna(subset=['r', 'volume'])


def get_ETF_holdings(ticker: str, sleep_sec=1) -> str:
    """
    This function scraps ETF holdings  from Yahoo finance
    """
    print(f'Downloading {ticker} holdings...')
    html = requests.get(f'https://finance.yahoo.com/quote/{ticker}/holdings?p={ticker}').text
    soup = BeautifulSoup(html, 'lxml')
    try:
        table_rows = soup.find('div', attrs={'data-test': 'top-holdings'}).find('table').find('tbody').find_all('tr')
        ETF_holdings = '|'.join([row.find('td').text for row in table_rows])
    except:
        ETF_holdings = np.nan
    time.sleep(sleep_sec)
    return ETF_holdings


def get_ETF_sum_AUM(ticker: str, sleep_sec=1) -> list:
    """
    This function downloads  ETF summary and AUM using yfinance get_info method.
    """
    print(f'Downloading {ticker} summary and AUM...')
    ETF = yf.Ticker(ticker)
    try:
        ETF_info = ETF.get_info()
        ETF_summary = ETF_info['longBusinessSummary']
        ETF_mktcap = ETF_info['totalAssets']
    except:
        ETF_summary = np.nan
        ETF_mktcap = np.nan
    time.sleep(sleep_sec)
    return [ETF_summary, ETF_mktcap]


