import requests
import logging
from requests import Timeout
from retry import retry


class BaseRequestExecutor:
    TIMEOUT = 5

    @staticmethod
    @retry((ConnectionError, Timeout), delay=5, tries=5)
    def sendRequest(method, api_tuple):
        # Burp Proxy
        http_proxy = "http://127.0.0.1:8083"
        https_proxy = "http://127.0.0.1:8083"
        proxyDict = {
            "http": http_proxy,
            "https": https_proxy,
        }
        url, headers, body, asset = api_tuple
        session = requests.session()
        try:
            if method == "POST":
                if headers is not None:
                    response = session.post(url, data=body, headers=headers, timeout=BaseRequestExecutor.TIMEOUT,
                                            verify=True)
                else:
                    response = session.post(url, data=body, timeout=BaseRequestExecutor.TIMEOUT, verify=True)

                logging.debug(f"Response code for {url} : {response.status_code}, {response.request}")

                if response.status_code not in range(200, 299):
                    logging.warning(
                        requests.exceptions.HTTPError(f"Request failed with status code {response.status_code}"))

                return (asset, response)

            elif method == "GET":
                if headers is not None:
                    response = session.get(url, headers=headers, verify=False, proxies=proxyDict,
                                           timeout=BaseRequestExecutor.TIMEOUT)
                else:
                    response = session.get(url, verify=False, proxies=proxyDict, timeout=BaseRequestExecutor.TIMEOUT)

                logging.debug(f"Response code for {url} : {response.status_code}, {response.request}")

                if response.status_code not in range(200, 299):
                    logging.warning(
                        requests.exceptions.HTTPError(f"Request failed with status code {response.status_code}"))

                return (asset, response)
        except requests.exceptions.Timeout as e:
            logging.error(f"Error: HTTP Request Exception in {url} - {e}")
            raise
        except requests.exceptions.RequestException as e:
            logging.error(f"Error: HTTP Request Exception in {url} - {e}")
            raise
