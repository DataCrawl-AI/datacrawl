from typing import Optional
import time

import requests
from bs4 import BeautifulSoup

from tiny_web_crawler.logging import get_logger

MAX_RETRIES = 5

logger = get_logger()

def is_transient_error(status_code: int) -> bool:
    transient_errors = [408, 502, 503, 504]

    return status_code in transient_errors

def fetch_url(url: str, retries: int = MAX_RETRIES) -> Optional[BeautifulSoup]:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.text
        return BeautifulSoup(data, 'lxml')
    except requests.exceptions.HTTPError as http_err:
        if response.status_code and is_transient_error(response.status_code) and retries > 1:
            logger.error("Transient HTTP error occurred: %s. Retrying...", http_err)
            time.sleep( 1*(MAX_RETRIES-retries+1) )
            return fetch_url( url, retries-1 )

        logger.error("HTTP error occurred: %s", http_err)
        return None
    except requests.exceptions.ConnectionError as conn_err:
        logger.error("Connection error occurred: %s", conn_err)
    except requests.exceptions.Timeout as timeout_err:
        logger.error("Timeout error occurred: %s", timeout_err)
    except requests.exceptions.RequestException as req_err:
        logger.error("Request error occurred: %s", req_err)
    return None
