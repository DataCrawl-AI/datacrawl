from __future__ import annotations

from dataclasses import dataclass, field
import json
import time
import re

from typing import Dict, List, Optional, Set, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.parse
from colorama import Fore, Style

from tiny_web_crawler.networking.fetcher import fetch_url
from tiny_web_crawler.networking.validator import is_valid_url
from tiny_web_crawler.networking.formatter import format_url

DEFAULT_SCHEME: str = 'http://'

@dataclass
class Spider:
    """
    A simple web crawler class.

    Attributes:
        root_url (str): The root URL to start crawling from.
        max_links (int): The maximum number of links to crawl.
        crawl_result (Dict[str, Dict[str, Any]): The dictionary storing the crawl results.
        crawl_set (Set[str]): A set of URLs to be crawled.
        link_count (int): The current count of crawled links.
        save_to_file (Optional[str]): The file path to save the crawl results.
        max_workers (int): Max count of concurrent workers
        delay (float): request delay
        url_regex (Optional[str]): A regular expression against which urls will be matched before crawling
        include_body (bool): Whether or not to include the crawled page's body in crawl_result (default: False)
        internal_links_only (bool): Whether or not to crawl only internal links
        external_links_only (bool): Whether or not to crawl only external links
    """

    root_url: str
    root_netloc: str = field(init=False)
    max_links: int = 5
    save_to_file: Optional[str] = None
    max_workers: int = 1
    delay: float = 0.5
    verbose: bool = True
    crawl_result: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    crawl_set: Set[str] = field(default_factory=set)
    link_count: int = 0
    scheme: str = field(default=DEFAULT_SCHEME, init=False)
    url_regex: Optional[str] = None
    include_body: bool = False
    internal_links_only: bool = False
    external_links_only: bool = False

    def __post_init__(self) -> None:
        self.root_netloc = urllib.parse.urlparse(self.root_url).netloc

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

    def crawl(self, url: str) -> None:
        """
        Crawls a given URL, extracts links, and adds them to the crawl results.

        Args:
            url (str): The URL to crawl.
        """
        if not is_valid_url(url):
            self.verbose_print(Fore.RED + f"Invalid url to crawl: {url}")
            return

        if url in self.crawl_result:
            self.verbose_print(Fore.YELLOW + f"URL already crawled: {url}")
            return

        self.verbose_print(Fore.GREEN + f"Crawling: {url}")
        soup = fetch_url(url)
        if not soup:
            return

        links = soup.body.find_all('a', href=True) if soup.body else []
        self.crawl_result[url] = {'urls': []}

        if self.include_body:
            self.crawl_result[url]['body'] = str(soup)

        for link in links:
            pretty_url = format_url(link['href'].lstrip(), url, self.scheme)
            if not is_valid_url(pretty_url):
                self.verbose_print(Fore.RED + f"Invalid url: {pretty_url}")
                continue

            if pretty_url in self.crawl_result[url]['urls']:
                continue

            if self.url_regex:
                if not re.compile(self.url_regex).match(pretty_url):
                    self.verbose_print(Fore.YELLOW + f"Skipping: URL didn't match regex: {pretty_url}")
                    continue

            if self.internal_links_only and self.root_netloc != urllib.parse.urlparse(pretty_url).netloc:
                self.verbose_print(Fore.RED + f"Skipping: External link: {pretty_url}")
                continue

            if self.external_links_only and self.root_netloc == urllib.parse.urlparse(pretty_url).netloc:
                self.verbose_print(Fore.RED + f"Skipping: Internal link: {pretty_url}")
                continue

            self.crawl_result[url]['urls'].append(pretty_url)
            self.crawl_set.add(pretty_url)
            self.verbose_print(Fore.BLUE + f"Link found: {pretty_url}")

        if self.link_count < self.max_links:
            self.link_count += 1
            self.verbose_print(Fore.GREEN + f"Links crawled: {self.link_count}")

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
