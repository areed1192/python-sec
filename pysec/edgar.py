import requests
import xml.etree.ElementTree as ET

# https://www.sec.gov/cgi-bin/srch-edgar?text=form-type%3D%2810-q*+OR+10-k*%29&first=2020&last=2020


class EDGARQuery():

    def __init__(self):

        # base URL for the SEC EDGAR browser
        self.endpoint = r"https://www.sec.gov/cgi-bin/browse-edgar"
        self.browse_service = 'browse-edgar'
        self.search_service = 'srch-edgar'
        self.cik_lookup = 'cik_lookup'
        self.mutal_fund_search = 'series'


        # define our parameters dictionary
        self.query_dict = {'action':'getcompany',
                           'CIK':'1265107',
                           'type':'10-k',
                           'dateb':'20190101',
                           'owner':'exclude',
                           'start':'',
                           'output':'',
                           'count':'100'}

    def query_filing_type(self, filing_type = None):

        params = {'action':'getcompany','type':'10-k'}




# # request the url, and then parse the response.
# response = requests.get(url = endpoint, params = param_dict)
# soup = BeautifulSoup(response.content, 'html.parser')
