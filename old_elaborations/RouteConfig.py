import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class RequestsConfig:
    @staticmethod
    def route_session():
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    @staticmethod
    def call_api_route(session, endpoint, params):
        r = session.get(endpoint, params=params)
        return r

    @staticmethod
    def check_invalid_status_code(response):
        if response.status_code != 200:
            print("ERROR: HTTP Response code {0} for request {1}".format(response.status_code, response.request.path_url))
            return False
        return True
