from typing import Optional

import requests
from bs4 import BeautifulSoup

from tiny_web_crawler.logging import get_logger

logger = get_logger()

def fetch_url(url: str) -> Optional[BeautifulSoup]:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.text
        return BeautifulSoup(data, 'lxml')
    except requests.exceptions.HTTPError as http_err:
        logger.error("HTTP error occurred: %s", http_err)
    except requests.exceptions.ConnectionError as conn_err:
        logger.error("Connection error occurred: %s", conn_err)
    except requests.exceptions.Timeout as timeout_err:
        logger.error("Timeout error occurred: %s", timeout_err)
    except requests.exceptions.RequestException as req_err:
        logger.error("Request error occurred: %s", req_err)
    return None
