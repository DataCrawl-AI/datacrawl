from dataclasses import dataclass
from typing import Optional


@dataclass
class GeneralSettings:
    """
    A simple dataclass to store general settings for the Spider class

    Attributes:
        root_url (str): The root URL to start crawling from.
        max_links (int): The maximum number of links to crawl. (Default: 5)
        save_to_file (Optional[str]): The file path to save the crawl results.
        max_workers (int): Max count of concurrent workers. (Default: 1)
        delay (float): Delay between requests. (Default: 0.5)
        verbose (bool): Whether or not to print debug messages (Default: True)
    """

    root_url: str = ""
    max_links: int = 5
    save_to_file: Optional[str] = None
    max_workers: int = 1
    delay: float = 0.5
    verbose: bool = True


@dataclass
class CrawlSettings:
    """
    A simple dataclass to store crawl settings for the Spider class

    Attributes:
        url_regex (Optional[str]):
            A regular expression against which urls will be matched before crawling

        include_body (bool):
            Whether or not to include the crawled page's body in crawl_result
            (Default: False)

        internal_links_only (bool):
            Whether or not to crawl only internal links (Default: False)

        external_links_only (bool):
            Whether or not to crawl only external links (Default: False)

        respect_robots_txt (bool):
            Whether or not to respect website's robots.txt files (default: True)
    """

    url_regex: Optional[str] = None
    include_body: bool = False
    internal_links_only: bool = False
    external_links_only: bool = False
    respect_robots_txt: bool = True
    max_retry_attempts: int = 5


@dataclass
class SpiderSettings(GeneralSettings, CrawlSettings):
    """
    A simple dataclass that stores all the settings for the Spider class
    """

    def __post_init__(self) -> None:
        if self.root_url == "":
            raise ValueError('"root_url" argument is required')

        if self.internal_links_only and self.external_links_only:

            raise ValueError(
                "Only one of internal_links_only and external_links_only can be set to True"
            )
