# -*- coding: utf-8 -*-
# filename: crawler.py
# Author: Indrajith Indraprastham
# License: GPL v3: http://www.gnu.org/licenses/

# --------------------------------------------------------------------------------
# README
# --------------------------------------------------------------------------------
# Install Requirements
# pip install validators beautifulsoup4 lxml colorama

# Python version: Python 3.6.3 :: Anaconda, Inc.

from bs4 import BeautifulSoup
import requests
import json
import urllib.parse
import validators
from colorama import init, Fore, Style
from typing import Optional, Dict, Set

# Initialize colorama
init(autoreset=True)


class Spider:
    def __init__(self, root_url: str, max_links: int, save_to_file: Optional[str] = None) -> None:
        self.root_url: str = root_url
        self.max_links: int = max_links
        self.crawl_result: Dict[str, Dict[str, list]] = {}
        self.crawl_set: set = set()
        self.link_count: int = 0
        self.default_scheme: str = 'http://'
        self.save_to_file: Optional[str] = save_to_file
        self.scheme: str = self.default_scheme

    def fetch_url(self, url: str) -> Optional(BeautifulSoup):
        """
        Reads the content of a url, parses it using BeautifulSoup with lxml parser.
        """
        try:
            with requests.get(url) as response:
                data = response.text
            return BeautifulSoup(data, 'lxml')
        except Exception as e:
            print(Fore.RED + f"Unable to fetch url: {url}, Error: {e}")
            return None

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        Returns True for a valid url, False for an invalid url.
        """
        return bool(validators.url(url))

    def save_results(self) -> None:
        """
        Saves results into a json file.
        """
        with open(self.save_to_file, 'w') as file:
            json.dump(self.crawl_result, file, indent=4)

    def format_url(self, url: str, base_url: str) -> str:
        """
        Removes any query, params, tag-id reference in the urls.
        Adds base_url to url if it is a relative link (link to the same domain).
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

    def start(self) -> Dict[str, Dict[str, list]]:
        """
        Start crawling from the root_url. Crawls up to max_links urls.
        After each crawl, urls found are added to the crawl_set,
        next url to crawl is taken from this set.
        """
        self.crawl(self.root_url)

        while self.crawl_set and self.link_count < self.max_links:
            self.crawl(self.crawl_set.pop())

        if self.save_to_file:
            self.save_results()
        print(Style.BRIGHT + Fore.MAGENTA + "Exiting....")
        return self.crawl_result


def main() -> None:
    root_url = 'http://github.com'
    max_links = 2

    crawler = Spider(root_url, max_links, save_to_file='out.json')
    crawler.start()


if __name__ == '__main__':
    main()
