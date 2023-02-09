import json
from pprint import pprint
from edgar.client import EdgarClient
from edgar.enums import FilingTypeCodes
from edgar.form_retriever.form_4_retriever import Form4Retriever
from yahoo.stock_price_retriever import StockPriceRetriever

# Initialize the Edgar Client
# edgar_client = EdgarClient()

# # Initialize the `Filings` Services.
# filings_service = edgar_client.filings()

# filings = filings_service.get_filings_by_type(
#     cik='1326801',
#     filing_type=FilingTypeCodes.FILING_4
# )
# print("-----------")
# print(filings)

def read_file(file_path):
    f = open(file_path, 'r')
    lines = f.readlines()
    f.close()
    return lines

def get_company_tik_to_cik_map():  
    with open('data/company_tickers.json') as f:
        data = json.load(f)
        tik_to_cik = {}
        for attribute, value in data.items():
            tik_to_cik[value['ticker']] = value['cik_str']
        return tik_to_cik
tik_to_cik_map = get_company_tik_to_cik_map()

stock_price_retriever = StockPriceRetriever()
form_4_retriever = Form4Retriever()
stocks = read_file('data/qqq.txt')[1:]
count = 0
for stock in stocks:
    stock_info = stock.split('\t')
    stock_tik = stock_info[1]
    # stock_price_retriever.get_historical_prices(stock_tik)
    company_cik = tik_to_cik_map[stock_tik]
    print("{}\t{}\t{}".format(count, stock_tik, company_cik))
    count += 1
    form_4_retriever.get_form_4_fillings(company_cik=company_cik)
    if count > 5:
        break

# Grab some filings for Facebook.
# filings = filings_service.get_filings_by_cik(cik='1326801')
# print(filings)

# # Grab the 10-Ks for Facebook,
# pprint(
#     filings_service.get_filings_by_type(
#         cik='1326801',
#         filing_type=FilingTypeCodes.FILING_10K
#     )
# )

# # Grab some filings for Facebook using the advance query.
# pprint(
#     filings_service.query(
#         cik='1326801',
#         filing_type='10-k'
#     )
# )