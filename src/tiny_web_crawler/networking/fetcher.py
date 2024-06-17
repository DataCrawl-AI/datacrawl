from typing import Optional

import requests
from bs4 import BeautifulSoup
from colorama import Fore


def fetch_url(url: str) -> Optional[BeautifulSoup]:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.text
        return BeautifulSoup(data, 'lxml')
    except requests.exceptions.HTTPError as http_err:
        print(Fore.RED + f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(Fore.RED + f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(Fore.RED + f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(Fore.RED + f"Request error occurred: {req_err}")
    return None
