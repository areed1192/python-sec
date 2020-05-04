import requests
import pprint
import csv

from typing import List
from typing import Dict


# Grab the data for a specific Day.
URL = "https://api.exchangeratesapi.io/2010-01-12"

# Grab the data for a list of Symbols.
URL_SYMBOLS = "https://api.exchangeratesapi.io/latest?symbols=USD,GBP"

# Grab the data for a Date Range and List of Symbols.
URL_DATE_RANGE = "https://api.exchangeratesapi.io/history?start_at=2018-01-01&end_at=2018-09-01&symbols=ILS,JPY"


"""
    https://exchangeratesapi.io/
"""

def simple_fx_request(symbols: List[str], base: str, start_at: str = None, end_at = None) -> Dict:
    """Makes a request to the Exchange Rates API.

    Arguments:
    ----
    symbols {List[str]} -- A list of FX symbols. For example, `['EUR', 'USD']`.

    Keyword Arguments:
    ----
    start_at {str} -- If specified, will filter the data after this date. (default: {None})
        
    end_at {[type]} -- If specified, will filter the data before this date. (default: {None})

    Returns:
    ----
    Dict -- A dictionary containing the speicfied data.
    """

    url_base = "https://api.exchangeratesapi.io/history"

    params = {
        'base':base,
        'symbols':','.join(symbols),
        'start_at':start_at,
        'end_at':end_at
    }

    response = requests.get(url=url_base, params=params)

    if response.status_code == 200:
       return response.json()


if __name__ == "__main__":

    symbols_dict = {
        'EUR': ['USD', 'JPY', 'CAD', 'GBP'],
        'USD': ['EUR', 'JPY', 'CAD', 'GBP']
    }

    bases = ['EUR','USD']
    start_at = '2010-04-01'
    end_at = '2020-04-26'

    for base in bases:
        
        symbols = symbols_dict[base]
        data = simple_fx_request(symbols=symbols, base = base, start_at=start_at, end_at=end_at)
        rates = data['rates']

        with open('rates_{}.csv'.format(base), mode='w+', newline='') as rate_file:

            csv_writer = csv.writer(rate_file)
            csv_writer.writerow(['DATE'] + symbols_dict[base])

            for rate in rates:
                date = rate
                rate_data = rates[date]

                try:
                    csv_writer.writerow([date, rate_data['USD'], rate_data['JPY'], rate_data['CAD'], rate_data['GBP']])
                except:
                    csv_writer.writerow([date, rate_data['EUR'], rate_data['JPY'], rate_data['CAD'], rate_data['GBP']])


