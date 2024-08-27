import aiohttp
import pytest
from aioresponses import aioresponses
from datacrawl.core.crawl_settings import CrawlSettings
from datacrawl.core.crawler import Datacrawl

from tests.conftest import root_url


@pytest.fixture
def crawl_settings() -> CrawlSettings:
    return CrawlSettings(
        root_url=root_url,
        max_links=2,
        max_workers=5,
        delay=1,
        verbose=True,
        include_body=True,
        respect_robots_txt=True,
        save_to_file=None,  # Avoid file I/O during tests
    )


@pytest.fixture
def crawler(crawl_settings: CrawlSettings) -> Datacrawl:
    return Datacrawl(crawl_settings)


@pytest.mark.asyncio
async def test_crawl(crawler: Datacrawl) -> None:
    with aioresponses() as m:
        m.get(
            root_url,
            status=200,
            body=f"<html><body><a href='{root_url}/page1'>link</a></body></html>",
        )
        m.get(
            f"{root_url}/page1",
            status=200,
            body=f"<html><body><a href='{root_url}'>link</a></body></html>",
        )

        results = await crawler.start()
        assert root_url in results
        assert f"{root_url}/page1" in results[root_url]["urls"]
        assert root_url in results[f"{root_url}/page1"]["urls"]


@pytest.mark.asyncio
async def test_crawl_invalid_url(crawler: Datacrawl) -> None:
    with aioresponses() as m:
        m.get("http://invalid-url", status=404)

        await crawler.crawl(aiohttp.ClientSession(), "http://invalid-url")
        assert "http://invalid-url" not in crawler.crawl_result
