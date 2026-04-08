import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class APIClient:

    def __init__(self, base_url: str, token: str = None):
        self.base_url = base_url.rstrip("/")
        self.session  = requests.Session()

        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://",  adapter)
        self.session.mount("https://", adapter)

        if token:
            self.set_auth_token(token)

    def set_auth_token(self, token: str):
        self.session.headers.update(
            {"Authorization": f"Bearer {token}"}
        )

    def get(self, endpoint: str, params: dict = None):
        url      = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.get(url, params=params)
        print(f"GET {url} -> {response.status_code}")
        return response

    def post(self, endpoint: str, payload: dict = None):
        url      = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.post(url, json=payload)
        print(f"POST {url} -> {response.status_code}")
        return response

    def put(self, endpoint: str, payload: dict = None):
        url      = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.put(url, json=payload)
        print(f"PUT {url} -> {response.status_code}")
        return response

    def delete(self, endpoint: str):
        url      = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.delete(url)
        print(f"DELETE {url} -> {response.status_code}")
        return response

    def assert_status(self, response, expected: int):
        assert response.status_code == expected, (
            f"Expected {expected}, got {response.status_code}. "
            f"Body: {response.text}"
        )