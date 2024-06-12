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
import urllib.request
import json
import urllib.parse
import validators
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)


class Spider:
    def __init__(self, root_url, max_links, save_to_file=None):
        self.root_url = root_url
        self.max_links = max_links
        self.crawl_result = {}
        self.crawl_set = set()
        self.link_count = 0
        self.default_scheme = 'http://'
        self.save_to_file = save_to_file
        self.scheme = self.default_scheme

    def fetch_url(self, url):
        """
        Reads the content of a url, parses it using BeautifulSoup with lxml parser.
        """
        try:
            with urllib.request.urlopen(url) as response:
                data = response.read()
            return BeautifulSoup(data, 'lxml')
        except Exception as e:
            print(Fore.RED + f"Unable to fetch url: {url}, Error: {e}")
            return None

    @staticmethod
    def is_valid_url(url):
        """
        Returns True for a valid url, False for an invalid url.
        """
        return validators.url(url)

    def save_results(self):
        """
        Saves results into a json file.
        """
        with open(self.save_to_file, 'w') as file:
            json.dump(self.crawl_result, file, indent=4)

    def format_url(self, url, base_url):
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

    def crawl(self, url):
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

    def start(self):
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


def main():
    root_url = 'http://github.com'
    max_links = 2

    crawler = Spider(root_url, max_links, save_to_file='out.json')
    crawler.start()


if __name__ == '__main__':
    main()
