from typing import Optional

from dataclasses import dataclass

@dataclass
class GeneralSettings:
    root_url: str
    max_links: int = 5
    save_to_file: Optional[str] = None
    max_workers: int = 1
    delay: float = 0.5
    verbose: bool = True

@dataclass
class CrawlSettings:
    url_regex: Optional[str] = None
    include_body: bool = False
    internal_links_only: bool = False
    external_links_only: bool = False
    respect_robots_txt: bool = True

    def __post_init__(self) -> None:
        if self.internal_links_only and self.external_links_only:
            raise ValueError("Only one of internal_links_only and external_links_only can be set to True")
