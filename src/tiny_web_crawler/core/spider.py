from __future__ import annotations

from dataclasses import dataclass, field
import json
import time
import re

from typing import Dict, List, Optional, Set, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.parse
import urllib.robotparser
import requests

from tiny_web_crawler.networking.fetcher import fetch_url
from tiny_web_crawler.networking.validator import is_valid_url
from tiny_web_crawler.networking.formatter import format_url
from tiny_web_crawler.networking.robots_txt import is_robots_txt_allowed, setup_robots_txt_parser, get_robots_txt_url
from tiny_web_crawler.logging import get_logger, set_logging_level, INFO, DEBUG

DEFAULT_SCHEME: str = 'http://'
logger = get_logger()

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
        respect_robots_txt (bool): Whether or not to respect website's robots.txt files (defualt: True)
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
    url_regex: Optional[str] = None
    include_body: bool = False
    internal_links_only: bool = False
    external_links_only: bool = False
    respect_robots_txt: bool = True

    def __post_init__(self) -> None:
        self.scheme: str = DEFAULT_SCHEME

        self.robots: Dict[str, urllib.robotparser.RobotFileParser] = {}

        self.root_netloc: str = urllib.parse.urlparse(self.root_url).netloc

        if self.internal_links_only and self.external_links_only:
            raise ValueError("Only one of internal_links_only and external_links_only can be set to True")

        if self.verbose:
            set_logging_level(DEBUG)
        else:
            set_logging_level(INFO)

        if not self.respect_robots_txt:
            logger.warning(
                "Ignoring robots.txt files! You might be at risk of:\n"+
                "Agent/IP bans;\n"+
                "Disrupted operation;\n"+
                "Increased suspicion from anti-bot services;\n"+
                "Potential legal action;"
            )

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
            logger.debug("Invalid url to crawl: %s", url)
            return

        if url in self.crawl_result:
            logger.debug("URL already crawled: %s", url)
            return

        if self.respect_robots_txt and not self._handle_robots_txt(url):
            logger.debug("Skipped: Url doesn't allow crawling: %s", url)
            return

        logger.debug("Crawling: %s", url)
        soup = fetch_url(url)
        if not soup:
            return

        links = soup.body.find_all('a', href=True) if soup.body else []
        self.crawl_result[url] = {'urls': []}

        if self.include_body:
            self.crawl_result[url]['body'] = str(soup)

        for link in links:
            pretty_url = format_url(link['href'].lstrip(), url, self.scheme)

            if self._should_skip_link(pretty_url, url):
                continue

            self.crawl_result[url]['urls'].append(pretty_url)
            self.crawl_set.add(pretty_url)
            logger.debug("Link found: %s", pretty_url)

        if self.link_count < self.max_links:
            self.link_count += 1
            logger.debug("Links crawled: %s", self.link_count)

    def _should_skip_link(self, pretty_url: str, url: str) -> bool:
        if not is_valid_url(pretty_url):
            logger.debug("Invalid url: %s", pretty_url)
            return True

        if pretty_url in self.crawl_result[url]['urls']:
            return True

        if self.url_regex and not re.compile(self.url_regex).match(pretty_url):
            logger.debug("Skipping: URL didn't match regex: %s", pretty_url)
            return True

        if self.internal_links_only and self.root_netloc != urllib.parse.urlparse(pretty_url).netloc:
            logger.debug("Skipping: External link: %s", pretty_url)
            return True

        if self.external_links_only and self.root_netloc == urllib.parse.urlparse(pretty_url).netloc:
            logger.debug("Skipping: Internal link: %s", pretty_url)
            return True

        return False

    def _handle_robots_txt(self, url: str) -> bool:
        user_agent = requests.utils.default_user_agent()
        robots_url = get_robots_txt_url(url)

        if robots_url in self.robots:
            robot_parser = self.robots[robots_url]
        else:
            robot_parser = setup_robots_txt_parser(robots_url)

            self.robots[robots_url] = robot_parser

        if not is_robots_txt_allowed(url, robot_parser):
            return False

        crawl_delay = robot_parser.crawl_delay(user_agent)
        if crawl_delay is not None:
            time.sleep(float(crawl_delay))

        return True

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
        logger.debug("Exiting....")
        return self.crawl_result
