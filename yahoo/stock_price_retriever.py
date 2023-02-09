import csv
import time
import requests

class StockPriceRetriever:
    def __init__(self) -> None:
        pass

    # used extreme small and large number for start and end time, so we always get the max time period for each company.
    def get_historical_prices(self, company_tik):
        download_url = 'https://query1.finance.yahoo.com/v7/finance/download/{}?period1=0&period2=16720128000&interval=1d&events=history&includeAdjustedClose=true'.format(company_tik)
        prices = self.download(download_url)
        self.write_to_file(company_tik, prices)
        return prices

    def download(self, filing_href):
        response = requests.get(filing_href, headers={'User-Agent': 'G'}, stream=True)
        return response.text
    
    def write_to_file(self, company_name, stock_prices):
        f = open('data/stock_prices/' + company_name + '.csv', 'w')
        f.write(stock_prices)
        f.close()
