import json
import time
import requests
import logging
import pathlib

from typing import Dict


class EdgarSession():

    """
    Overview:
    ----
    Serves as the main Session for the 
    `EDGARClient`. The `EdgarSession` object
    handles all the requests made to EDGAR.
    """

    def __init__(self, client: object) -> None:
        """Initializes the `EdgarSession` client.

        ### Parameters:
        ----
        client (str): The `edgar.EdgarClient` Python Client.

        ### Usage:
        ----
            >>> edgar_client = EdgarClient()
            >>> edgar_session = EdgarSession()
        """

        from edgar.client import EdgarClient

        # We can also add custom formatting to our log messages.
        log_format = '%(asctime)-15s|%(filename)s|%(message)s'

        self.client: EdgarClient = client
        self.resource = 'https://www.sec.gov'
        self.api_resource = 'https://data.sec.gov'
        self.total_requests = 0

        if not pathlib.Path('logs').exists():
            pathlib.Path('logs').mkdir()
            pathlib.Path('logs/sec_api_log.log').touch()

        logging.basicConfig(
            filename="logs/sec_api_log.log",
            level=logging.INFO,
            encoding="utf-8",
            format=log_format
        )

    def __repr__(self) -> str:
        """String representation of the `EdgarClient.EdgarSession` object."""

        # define the string representation
        str_representation = '<EdgarClient.EdgarSession (active=True, connected=True)>'

        return str_representation

    def build_url(self, endpoint: str, use_api: bool = False) -> str:
        """Builds the full url for the endpoint.

        ### Parameters
        ----
        endpoint : str
            The endpoint being requested.

        use_api : bool (optional, Default=False)
            If `True` use the API resource URL, `False`
            use the filings resource URL.

        ### Returns
        ----
        str:
            The full URL with the endpoint needed.
        """

        if use_api:
            url = self.api_resource + endpoint
        else:
            url = self.resource + endpoint

        return url

    def make_request(
        self,
        method: str,
        endpoint: str,
        params: dict = None,
        data: dict = None,
        json_payload: dict = None,
        use_api: bool = False
    ) -> Dict:
        """Handles all the requests in the library.

        ### Overview:
        ---
        A central function used to handle all the requests made in the library,
        this function handles building the URL, defining Content-Type, passing
        through payloads, and handling any errors that may arise during the request.

        ### Parameters:
        ----
        method : str
            The Request method, can be one of the
            following: ['get','post','put','delete','patch']

        endpoint : str
            The API URL endpoint.

        params : dict (optional, Default=None) 
            The URL params for the request.

        data : dict (optional, Default=None)
            A data payload for a request.

        json : dict (optional, Default=None)
            A json data payload for a request

        use_api : bool (optional, Default=False)
            If `True` use the API resource URL, `False`
            use the filings resource URL.

        ### Returns:
        ----
            A Dictionary object containing the JSON values.
        """

        # Build the URL.
        url = self.build_url(endpoint=endpoint, use_api=use_api)

        logging.info(
            "URL: {url}".format(url=url)
        )

        if params:
            logging.info(
                "PARAMS: {params}".format(params=params)
            )

        # Define a new session.
        request_session = requests.Session()
        request_session.verify = True

        # Define a new request.
        request_request = requests.Request(
            method=method.upper(),
            url=url,
            params=params,
            data=data,
            json=json_payload
        ).prepare()

        print(request_request.url)

        self.total_requests += 1

        # Send the request.
        response: requests.Response = request_session.send(
            request=request_request
        )

        if self.total_requests == 9:
            print("sleeping for 5 seconds.")
            time.sleep(5)
            self.total_requests = 0

        # Keep going.
        while response.status_code != 200:

            try:
                response: requests.Response = request_session.send(
                    request=request_request
                )
            except:
                print("Sleeping for five seconds")
                time.sleep(5)

        # Close the session.
        request_session.close()

        # Grab the headers.
        response_headers = response.headers
        content_type = response_headers['Content-Type']

        # If it's okay and no details.
        if response.ok and len(response.content) > 0:

            if content_type in ['application/atom+xml', 'text/xml', 'text/html']:
                return response.text
            else:
                try:
                    return response.json()
                except:
                    content = response.content.replace(
                        b'Content-type: application/json\r\n\r\n',
                        b''
                    )
                    return json.loads(content)

        elif len(response.content) > 0 and response.ok:
            return {
                'message': 'response successful',
                'status_code': response.status_code
            }

        elif not response.ok:

            # Define the error dict.
            error_dict = {
                'error_code': response.status_code,
                'response_url': response.url,
                'response_body': json.loads(response.content.decode('ascii')),
                'response_request': dict(response.request.headers),
                'response_method': response.request.method,
            }

            # Log the error.
            logging.error(
                msg=json.dumps(obj=error_dict, indent=4)
            )

            raise requests.HTTPError()
