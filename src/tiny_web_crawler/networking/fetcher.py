from typing import Optional

import requests
from bs4 import BeautifulSoup
from colorama import Fore

from tiny_web_crawler.logging import get_logger

logger = get_logger()

def fetch_url(url: str) -> Optional[BeautifulSoup]:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.text
        return BeautifulSoup(data, 'lxml')
    except requests.exceptions.HTTPError as http_err:
        logger.error(Fore.RED + f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        logger.error(Fore.RED + f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        logger.error(Fore.RED + f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        logger.error(Fore.RED + f"Request error occurred: {req_err}")
    return None
