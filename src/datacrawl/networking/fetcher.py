import asyncio
import time
from typing import Optional

import aiohttp
import requests
from bs4 import BeautifulSoup

from datacrawl.logger import get_logger

TRANSIENT_ERRORS = [408, 502, 503, 504]

logger = get_logger()


def is_transient_error(status_code: int) -> bool:
    return status_code in TRANSIENT_ERRORS


def fetch_url(url: str, retries: int, attempts: int = 0) -> Optional[BeautifulSoup]:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.text
        return BeautifulSoup(data, "lxml")
    except requests.exceptions.HTTPError as http_err:
        if response.status_code and is_transient_error(response.status_code) and retries > 0:
            logger.error("Transient HTTP error occurred: %s. Retrying...", http_err)
            time.sleep(attempts + 1)
            return fetch_url(url, retries - 1, attempts + 1)

        logger.error("HTTP error occurred: %s", http_err)
        return None
    except requests.exceptions.ConnectionError as conn_err:
        logger.error("Connection error occurred: %s", conn_err)
    except requests.exceptions.Timeout as timeout_err:
        logger.error("Timeout error occurred: %s", timeout_err)
    except requests.exceptions.RequestException as req_err:
        logger.error("Request error occurred: %s", req_err)
    return None


async def fetch_url_async(url: str, retries: int, attempts: int = 0) -> Optional[BeautifulSoup]:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:
                if response.status in TRANSIENT_ERRORS and retries > 0:
                    logger.error(
                        "Transient HTTP error occurred: %s. Retrying...",
                        response.status,
                    )
                    await asyncio.sleep(attempts + 1)
                    return await fetch_url_async(url, retries - 1, attempts + 1)

                response.raise_for_status()
                data = await response.text()
                return BeautifulSoup(data, "lxml")
        except aiohttp.ClientResponseError as http_err:
            if response.status in TRANSIENT_ERRORS and retries > 0:
                logger.error("Transient HTTP error occurred: %s. Retrying...", http_err)
                await asyncio.sleep(attempts + 1)
                return await fetch_url_async(url, retries - 1, attempts + 1)
            logger.error("HTTP error occurred: %s", http_err)
            return None
        except aiohttp.ClientConnectionError as conn_err:
            logger.error("Connection error occurred: %s", conn_err)
        except asyncio.TimeoutError as timeout_err:
            logger.error("Timeout error occurred: %s", timeout_err)
        except aiohttp.ClientError as req_err:
            logger.error("Request error occurred: %s", req_err)
        return None
