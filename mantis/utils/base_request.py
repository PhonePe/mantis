import requests
import logging
from requests import Timeout
from retry import retry


class BaseRequestExecutor:

    TIMEOUT = 5

    @staticmethod 
    @retry((ConnectionError, Timeout), delay=5, tries=5)
    def sendRequest(method, api_tuple):
        self, url, body, asset = api_tuple
        session = requests.session()
        try:
            if method == "POST":
                response = session.post(url, data=body, headers=self.headers, timeout=BaseRequestExecutor.TIMEOUT,verify=True)
                logging.debug(response.request.url)
                logging.debug(response.request.body)
                logging.debug(response.text)

                if response.status_code not in range(200, 299):
                    logging.warning(requests.exceptions.HTTPError(f"Request failed with status code {response.status_code}"))
                
                return (asset,response)
            
            elif method == "GET":
                response = session.get(url, headers=self.headers, verify=True)
                logging.debug(f"Response code for {url} : {response.status_code}, {response.request}")
                if response.status_code not in range(200, 299):
                    logging.warning(requests.exceptions.HTTPError(f"Request failed with status code {response.status_code}"))
                
                return (asset,response)
        except requests.exceptions.Timeout as e:
            logging.error(f"Error: HTTP Request Exception in {url} - {e}")
            raise
        except requests.exceptions.RequestException as e:
            logging.error(f"Error: HTTP Request Exception in {url} - {e}")
            raise
