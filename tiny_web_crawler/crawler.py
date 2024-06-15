from __future__ import annotations
import json
import urllib.parse
from typing import Dict, List, Optional, Set
from concurrent.futures import ThreadPoolExecutor, as_completed

import time
import requests
import validators
from bs4 import BeautifulSoup
from colorama import Fore, Style, init

init(autoreset=True)

DEFAULT_SCHEME: str = 'http://'


class Spider():
    """
    A simple web crawler class.

    Attributes:
        root_url (str): The root URL to start crawling from.
        max_links (int): The maximum number of links to crawl.
        crawl_result (Dict[str, Dict[str, List[str]]]): The dictionary storing the crawl results.
        crawl_set (Set[str]): A set of URLs to be crawled.
        link_count (int): The current count of crawled links.
        save_to_file (Optional[str]): The file path to save the crawl results.
    """

    def __init__(self,
                 root_url: str,
                 max_links: int = 5,
                 save_to_file: Optional[str] = None,
                 max_workers: int = 1,
                 delay: float = 0.5,
                 verbose: bool = True,
                 stay_within_domain: bool = False) -> None:
        """
        Initializes the Spider class.

        Args:
            root_url (str): The root URL to start crawling from.
            max_links (int): The maximum number of links to crawl.
            save_to_file (Optional[str]): The file to save the crawl results to.
            stay_within_domain (bool): Whether to stay within the root domain.
        """
        self.root_url: str = root_url
        self.max_links: int = max_links
        self.crawl_result: Dict[str, Dict[str, List[str]]] = {}
        self.crawl_set: Set[str] = set()
        self.link_count: int = 0
        self.save_to_file: Optional[str] = save_to_file
        self.scheme: str = DEFAULT_SCHEME
        self.max_workers: int = max_workers
        self.delay: float = delay
        self.verbose: bool = verbose
        self.stay_within_domain: bool = stay_within_domain
        self.root_domain: str = urllib.parse.urlparse(root_url).netloc

    def fetch_url(self, url: str) -> Optional[BeautifulSoup]:
        """
        Reads the content of a URL and parses it using BeautifulSoup with lxml parser.

        Args:
            url (str): The URL to fetch and parse.

        Returns:
            Optional[BeautifulSoup]: A BeautifulSoup object if the URL is fetched successfully, None otherwise.
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
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

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        Checks if the provided URL is valid.

        Args:
            url (str): The URL to validate.

        Returns:
            bool: True if the URL is valid, False otherwise.
        """
        return bool(validators.url(url))

    def verbose_print(self, content: str) -> None:
        if self.verbose:
            print(content)

    def save_results(self) -> None:
        """
        Saves the crawl results into a JSON file.
        """
        if self.save_to_file:
            with open(self.save_to_file, 'w', encoding='utf-8') as file:
                json.dump(self.crawl_result, file, indent=4)

    def format_url(self, url: str, base_url: str) -> str:
        """
        Formats a URL to ensure it is absolute and removes any query parameters or fragments.

        Args:
            url (str): The URL to format.
            base_url (str): The base URL to resolve relative URLs.

        Returns:
            str: The formatted URL.
        """
        parsed_url = urllib.parse.urlparse(url)
        base_url = base_url.rstrip('/')

        if parsed_url.scheme:
            self.scheme = parsed_url.scheme

        if not parsed_url.scheme and not parsed_url.netloc:
            if self.is_valid_url(DEFAULT_SCHEME + parsed_url.path):
                return DEFAULT_SCHEME + parsed_url.path

            if parsed_url.path.startswith('/'):
                return base_url + parsed_url.path

            return f"{base_url}/{parsed_url.path}"

        return f"{self.scheme}://{parsed_url.netloc}{parsed_url.path}"

    def crawl(self, url: str) -> None:
        """
        Crawls a given URL, extracts links, and adds them to the crawl results.

        Args:
            url (str): The URL to crawl.
        """
        if not self.is_valid_url(url):
            self.verbose_print(Fore.RED + f"Invalid url to crawl: {url}")
            return

        if url in self.crawl_result:
            self.verbose_print(Fore.YELLOW + f"URL already crawled: {url}")
            return

        self.verbose_print(Fore.GREEN + f"Crawling: {url}")
        soup = self.fetch_url(url)
        if not soup:
            return

        links = soup.body.find_all('a', href=True) if soup.body else []
        self.crawl_result[url] = {'urls': []}

        for link in links:
            pretty_url = self.format_url(link['href'].lstrip(), url)
            if not self.is_valid_url(pretty_url):
                self.verbose_print(Fore.RED + f"Invalid url: {pretty_url}")
                continue

            # Check if we need to stay within the root domain
            if self.stay_within_domain and urllib.parse.urlparse(pretty_url).netloc != self.root_domain:
                self.verbose_print(Fore.RED + f"External link ignored: {pretty_url}")
                continue

            if pretty_url in self.crawl_result[url]['urls']:
                continue

            self.crawl_result[url]['urls'].append(pretty_url)
            self.crawl_set.add(pretty_url)
            self.verbose_print(Fore.BLUE + f"Link found: {pretty_url}")

        if self.link_count < self.max_links:
            self.link_count += 1
            self.verbose_print(
                Fore.GREEN + f"Links crawled: {self.link_count}")

    def start(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Starts the crawling process from the root URL. Crawls up to max_links URLs.

        Returns:
            Dict[str, Dict[str, List[str]]]: The crawl results.
        """
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.crawl, self.root_url)}

            while self.link_count < self.max_links and futures:
                for future in as_completed(futures):
                    futures.remove(future)
                    if future.exception() is None:
                        while self.link_count < self.max_links and self.crawl_set:
                            url = self.crawl_set.pop()
                            if url not in self.crawl_result:
                                futures.add(executor.submit(self.crawl, url))
                                time.sleep(self.delay)
                                break  # Break to check the next future

        if self.save_to_file:
            self.save_results()
        self.verbose_print(Style.BRIGHT + Fore.MAGENTA + "Exiting....")
        return self.crawl_result


def main() -> None:
    """
    The main function to initialize and start the crawler.
    """
    root_url = 'https://pypi.org/'
    max_links = 5

    crawler = Spider(root_url, max_links, save_to_file='out.json', stay_within_domain=True)
    print(Fore.GREEN + f"Crawling: {root_url}")
    crawler.start()


if __name__ == '__main__':
    main()