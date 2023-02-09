import logging
import time
import requests
from edgar.client import EdgarClient
from edgar.enums import FilingTypeCodes
from edgar.parser import EdgarParser


class Form4Retriever():

    """
    ## Overview:
    ----
    Retrieve and Parse form 4 for a company.
    """

    def __init__(self) -> None:
        self.edgar_client = EdgarClient()
        self.edgar_parser = EdgarParser()

    def get_form_4_fillings(self, company_cik):
        logging.info("Trying to get form 4 for company {}".format(company_cik))
        # Initialize the `Filings` Services.
        filings_service = self.edgar_client.filings()

        filings = filings_service.get_filings_by_type(
            cik=company_cik,
            filing_type = FilingTypeCodes.FILING_4)
        count = 0
        for filing in filings:
            if filing['filing_type'] != '4':
                print("Filing type is {}. Skipping ... {}".format(filing['filing_type'], filing['filing_href']))
                continue
            filing_href = filing['filing_href']
            logging.info("retrieving filing_href: {}".format(filing_href))
            detail_page_response = self.get_page(filing_href=filing_href)
            form_4_xml_path = self.edgar_parser.get_form_4_xml_path(
                response_text=detail_page_response.content
            )
            sec_url = 'https://www.sec.gov'
            req_url = sec_url + form_4_xml_path
            form_4_xml_page_response = self.get_page(filing_href=req_url)
            try:
                form_4_content = self.edgar_parser.parse_form_4_xml(form_4_xml_page_response.content)
                print("{}\t{}".format(count, form_4_content))
            except Exception as ex:
                print("{}\t Failed to parse {}. EX: {}".format(count, req_url, ex))
            count += 1
            time.sleep(0.1)

    
    def get_page(self, filing_href):
        response = requests.get(filing_href, headers={'User-Agent': 'G'}, stream=True)
        # print("4 page response: {}".format(response.content))
        return response

