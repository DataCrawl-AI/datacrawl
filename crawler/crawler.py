from __future__ import annotations

import json
import urllib.parse
from typing import Dict, List, Optional, Set

import requests
import validators
from bs4 import BeautifulSoup
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)


class SpiderConfig:
    def __init__(self, root_url: str, max_links: int, save_to_file: Optional[str] = None) -> None:
        self.root_url: str = root_url
        self.max_links: int = max_links
        self.default_scheme: str = 'http://'
        self.save_to_file: Optional[str] = save_to_file
        self.scheme: str = self.default_scheme


class Spider:
    """
    A simple web crawler class.

    Attributes:
        root_url (str): The root URL to start crawling from.
        max_links (int): The maximum number of links to crawl.
        crawl_result (Dict[str, Dict[str, List[str]]]): The dictionary storing the crawl results.
        crawl_set (Set[str]): A set of URLs to be crawled.
        link_count (int): The current count of crawled links.
        default_scheme (str): The default URL scheme (e.g., 'http://').
        save_to_file (Optional[str]): The file path to save the crawl results.
        scheme (str): The current URL scheme being used.
    """

    def __init__(self, root_url: str, max_links: int, save_to_file: Optional[str] = None) -> None:
        """
        Initializes the Spider class.

        Args:
            root_url (str): The root URL to start crawling from.
            max_links (int): The maximum number of links to crawl.
            save_to_file (Optional[str]): The file to save the crawl results to.
        """
        self.root_url: str = root_url
        self.max_links: int = max_links
        self.crawl_result: Dict[str, Dict[str, List[str]]] = {}
        self.crawl_set: Set[str] = set()
        self.link_count: int = 0
        self.default_scheme: str = 'http://'
        self.save_to_file: Optional[str] = save_to_file
        self.scheme: str = self.default_scheme

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        Returns True for a valid url, False for an invalid url.
        """
        return bool(validators.url(url))

    def fetch_url(self, url: str) -> Optional[BeautifulSoup]:
        """
        Reads the content of a URL and parses it using BeautifulSoup with lxml parser.

        Args:
            url (str): The URL to fetch and parse.

        Returns:
            Optional[BeautifulSoup]: A BeautifulSoup object if the URL is fetched successfully,
            None otherwise.
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
        except Exception as e:  # pylint: disable=broad-exception-caught
            # Catch all other exceptions
            print(Fore.RED + f"An unexpected error occurred: {e}")
        return None

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
            if self.is_valid_url(self.default_scheme + parsed_url.path):
                return self.default_scheme + parsed_url.path

            if parsed_url.path.startswith('/'):
                return base_url + parsed_url.path
            else:
                return f"{base_url}/{parsed_url.path}"

        return f"{self.scheme}://{parsed_url.netloc}{parsed_url.path}"

    def crawl(self, url: str) -> None:
        """
        Crawls a given URL, extracts links, and adds them to the crawl results.

        Args:
            url (str): The URL to crawl.
        """
        if not self.is_valid_url(url):
            print(Fore.RED + f"Invalid url to crawl: {url}")
            return

        if url in self.crawl_result:
            print(Fore.YELLOW + f"URL already crawled: {url}")
            return

        print(Fore.GREEN + f"Crawling: {url}")
        soup = self.fetch_url(url)
        if not soup:
            return

        links = soup.body.find_all('a', href=True)
        self.crawl_result[url] = {'urls': []}

        for link in links:
            pretty_url = self.format_url(link['href'].lstrip(), url)
            if not self.is_valid_url(pretty_url):
                print(Fore.RED + f"Invalid url: {pretty_url}")
                continue

            if pretty_url in self.crawl_result[url]['urls']:
                continue

            self.crawl_result[url]['urls'].append(pretty_url)
            self.crawl_set.add(pretty_url)
            print(Fore.BLUE + f"Link found: {pretty_url}")

        if self.link_count < self.max_links:
            self.link_count += 1
            print(Fore.GREEN + f"Links crawled: {self.link_count}")

    def start(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Starts the crawling process from the root URL. Crawls up to max_links URLs.

        Returns:
            Dict[str, Dict[str, List[str]]]: The crawl results.
        """
        self.crawl(self.root_url)

        while self.crawl_set and self.link_count < self.max_links:
            self.crawl(self.crawl_set.pop())

        if self.save_to_file:
            self.save_results()
        print(Style.BRIGHT + Fore.MAGENTA + "Exiting....")
        return self.crawl_result


def main() -> None:
    """
    The main function to initialize and start the crawler.
    """
    root_url = 'http://github.com'
    max_links = 2

    crawler = Spider(root_url, max_links, save_to_file='out.json')
    crawler.start()


if __name__ == '__main__':
    main()
