from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.robotparser
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from logging import DEBUG, INFO
from typing import Any, Dict, List, Set

import requests

from datacrawl.core.spider_settings import SpiderSettings
from datacrawl.logger import get_logger, set_logging_level
from datacrawl.networking.fetcher import fetch_url
from datacrawl.networking.formatter import format_url
from datacrawl.networking.robots_txt import (
    get_robots_txt_url,
    is_robots_txt_allowed,
    setup_robots_txt_parser,
)
from datacrawl.networking.validator import is_valid_url

DEFAULT_SCHEME: str = "http://"
logger = get_logger()


@dataclass
class Spider:
    """
    A simple web crawler class.

    Attributes:
        settings (SpiderSettings):
        The SpiderSettings object with the settings for the Spider object
    """

    settings: SpiderSettings

    crawl_result: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    crawl_set: Set[str] = field(default_factory=set)
    link_count: int = 0

    def __post_init__(self) -> None:
        self.scheme: str = DEFAULT_SCHEME

        self.robots: Dict[str, urllib.robotparser.RobotFileParser] = {}

        self.root_netloc: str = urllib.parse.urlparse(self.settings.root_url).netloc

        if self.settings.verbose:
            set_logging_level(DEBUG)
        else:
            set_logging_level(INFO)

        if not self.settings.respect_robots_txt:
            logger.warning(
                "Ignoring robots.txt files! You might be at risk of:\n"
                + "Agent/IP bans;\n"
                + "Disrupted operation;\n"
                + "Increased suspicion from anti-bot services;\n"
                + "Potential legal action;"
            )

    def save_results(self) -> None:
        """
        Saves the crawl results into a JSON file.
        """
        if self.settings.save_to_file:
            with open(self.settings.save_to_file, "w", encoding="utf-8") as file:
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

        if self.settings.respect_robots_txt and not self._handle_robots_txt(url):
            logger.debug("Skipped: Url doesn't allow crawling: %s", url)
            return

        logger.debug("Crawling: %s", url)
        soup = fetch_url(url, retries=self.settings.max_retry_attempts)
        if not soup:
            return

        links = soup.body.find_all("a", href=True) if soup.body else []
        self.crawl_result[url] = {"urls": []}

        if self.settings.include_body:
            self.crawl_result[url]["body"] = str(soup)

        for link in links:
            pretty_url = format_url(link["href"].lstrip(), url, self.scheme)

            if self._should_skip_link(pretty_url, url):
                continue

            self.crawl_result[url]["urls"].append(pretty_url)
            self.crawl_set.add(pretty_url)
            logger.debug("Link found: %s", pretty_url)

        if self.link_count < self.settings.max_links:
            self.link_count += 1
            logger.debug("Links crawled: %s", self.link_count)

    def _should_skip_link(self, pretty_url: str, url: str) -> bool:
        if not is_valid_url(pretty_url):
            logger.debug("Invalid url: %s", pretty_url)
            return True

        if pretty_url in self.crawl_result[url]["urls"]:
            return True

        if self.settings.url_regex and not re.compile(self.settings.url_regex).match(pretty_url):
            logger.debug("Skipping: URL didn't match regex: %s", pretty_url)
            return True

        if (
            self.settings.internal_links_only
            and self.root_netloc != urllib.parse.urlparse(pretty_url).netloc
        ):
            logger.debug("Skipping: External link: %s", pretty_url)
            return True

        if (
            self.settings.external_links_only
            and self.root_netloc == urllib.parse.urlparse(pretty_url).netloc
        ):
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
        with ThreadPoolExecutor(max_workers=self.settings.max_workers) as executor:
            futures = {executor.submit(self.crawl, self.settings.root_url)}

            while self.link_count < self.settings.max_links and futures:
                for future in as_completed(futures):
                    futures.remove(future)
                    if future.exception() is None:
                        while self.link_count < self.settings.max_links and self.crawl_set:
                            url = self.crawl_set.pop()
                            if url not in self.crawl_result:
                                futures.add(executor.submit(self.crawl, url))
                                time.sleep(self.settings.delay)
                                break  # Break to check the next future

        if self.settings.save_to_file:
            self.save_results()
        logger.debug("Exiting....")
        return self.crawl_result
