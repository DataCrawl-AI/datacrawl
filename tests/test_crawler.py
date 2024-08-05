import urllib
import urllib.error
from io import BytesIO
from logging import DEBUG, ERROR, WARNING
from typing import Callable
from unittest.mock import MagicMock, mock_open, patch

import pytest
import responses
from datacrawl import CrawlSettings, Datacrawl
from pytest import LogCaptureFixture

from tests.conftest import root_url


@responses.activate
def test_crawl(
    mock_urlopen: MagicMock,
    mock_response: MagicMock,
    setup_responses: Callable[[str, str, int], None],
) -> None:
    setup_responses(root_url, f"<html><body><a href='{root_url}/test'>link</a></body></html>", 200)
    setup_responses(
        f"{root_url}/test", f"<html><body><a href='{root_url}'>link</a></body></html>", 200
    )

    mock_urlopen.side_effect = lambda url: mock_response

    spider = Datacrawl(CrawlSettings(root_url=root_url, max_links=10))
    spider.crawl(root_url)

    assert root_url in spider.crawl_result
    assert spider.crawl_result[root_url]["urls"] == [f"{root_url}/test"]

    spider.crawl(f"{root_url}/test")

    assert f"{root_url}/test" in spider.crawl_result
    assert spider.crawl_result[f"{root_url}/test"]["urls"] == [root_url]


@responses.activate
def test_crawl_invalid_url(mock_urlopen: MagicMock, caplog: LogCaptureFixture) -> None:
    spider = Datacrawl(CrawlSettings(root_url=root_url))

    with caplog.at_level(DEBUG):
        spider.crawl("invalid_url")

    assert "Invalid url to crawl:" in caplog.text
    assert spider.crawl_result == {}


@responses.activate
def test_crawl_already_crawled_url(
    mock_urlopen: MagicMock,
    mock_response: MagicMock,
    setup_responses: Callable[[str, str, int], None],
    caplog: LogCaptureFixture,
) -> None:
    setup_responses(root_url, f"<html><body><a href='{root_url}'>link</a></body></html>", 200)

    spider = Datacrawl(CrawlSettings(root_url=root_url))
    mock_urlopen.side_effect = lambda url: mock_response

    with caplog.at_level(DEBUG):
        spider.crawl(root_url)
        spider.crawl(root_url)

    assert "URL already crawled:" in caplog.text
    assert spider.crawl_result == {root_url: {"urls": [root_url]}}


@responses.activate
def test_crawl_unfetchable_url(
    mock_urlopen: MagicMock,
    mock_response: MagicMock,
    setup_responses: Callable[[str, str, int], None],
) -> None:
    setup_responses(root_url, f"<html><body><a href='{root_url}'>link</a></body></html>", 404)

    spider = Datacrawl(CrawlSettings(root_url=root_url))
    mock_response.status = 404
    mock_urlopen.side_effect = lambda url: mock_response

    spider.crawl(root_url)
    assert spider.crawl_result == {}


@responses.activate
def test_crawl_found_invalid_url(
    mock_urlopen: MagicMock,
    mock_response: MagicMock,
    setup_responses: Callable[[str, str, int], None],
    caplog: LogCaptureFixture,
) -> None:
    setup_responses(root_url, "<html><body><a href='^invalidurl^'>link</a></body></html>", 200)

    spider = Datacrawl(CrawlSettings(root_url=root_url))
    mock_urlopen.side_effect = lambda url: mock_response

    with caplog.at_level(DEBUG):
        spider.crawl(root_url)

    assert "Invalid url:" in caplog.text
    assert spider.crawl_result == {root_url: {"urls": []}}


@responses.activate
def test_crawl_found_duplicate_url(
    mock_urlopen: MagicMock,
    mock_response: MagicMock,
    setup_responses: Callable[[str, str, int], None],
) -> None:
    setup_responses(
        root_url,
        f"<html><body><a href='{root_url}'>link1</a>"
        f"<a href='{root_url}'>link2</a></body></html>",
        200,
    )

    spider = Datacrawl(CrawlSettings(root_url=root_url))
    mock_urlopen.side_effect = lambda url: mock_response

    spider.crawl(root_url)
    assert spider.crawl_result == {root_url: {"urls": [root_url]}}


@responses.activate
def test_crawl_no_urls_in_page(
    mock_urlopen: MagicMock,
    mock_response: MagicMock,
    setup_responses: Callable[[str, str, int], None],
) -> None:
    setup_responses(root_url, "<html><body></body></html>", 200)

    spider = Datacrawl(CrawlSettings(root_url=root_url))
    mock_urlopen.side_effect = lambda url: mock_response

    spider.crawl(root_url)
    assert spider.crawl_result == {root_url: {"urls": []}}


@responses.activate
def test_save_results() -> None:
    spider = Datacrawl(CrawlSettings(root_url=root_url, max_links=10, save_to_file="out.json"))
    spider.crawl_result = {root_url: {"urls": [f"{root_url}/test"]}}

    with patch("builtins.open", mock_open()) as mocked_file:
        spider.save_results()
        mocked_file.assert_called_once_with("out.json", "w", encoding="utf-8")


@responses.activate
def test_url_regex(
    mock_urlopen: MagicMock,
    mock_response: MagicMock,
    setup_responses: Callable[[str, str, int], None],
) -> None:
    setup_responses(
        root_url,
        f"<html><body><a href='{root_url}/123'>link</a>"
        f"<a href='{root_url}/test'>link</a></body></html>",
        200,
    )

    regex = rf"{root_url}/[0-9]+"

    spider = Datacrawl(CrawlSettings(root_url=root_url, url_regex=regex))
    mock_urlopen.side_effect = lambda url: mock_response

    spider.start()
    assert spider.crawl_result[root_url]["urls"] == [f"{root_url}/123"]
    assert f"{root_url}/test" not in spider.crawl_result[root_url]["urls"]


@responses.activate
def test_include_body(
    mock_urlopen: MagicMock,
    mock_response: MagicMock,
    setup_responses: Callable[[str, str, int], None],
) -> None:
    setup_responses(root_url, f"<html><body><a href='{root_url}/test'>link</a></body></html>", 200)
    setup_responses(f"{root_url}/test", "<html><body><h>This is a header</h></body></html>", 200)

    spider = Datacrawl(CrawlSettings(root_url=root_url, include_body=True))
    mock_urlopen.side_effect = lambda url: mock_response

    spider.start()
    assert (
        spider.crawl_result[root_url]["body"]
        == f'<html><body><a href="{root_url}/test">link</a></body></html>'
    )
    assert (
        spider.crawl_result[f"{root_url}/test"]["body"]
        == "<html><body><h>This is a header</h></body></html>"
    )


@responses.activate
def test_internal_links_only(
    mock_urlopen: MagicMock,
    mock_response: MagicMock,
    setup_responses: Callable[[str, str, int], None],
    caplog: LogCaptureFixture,
) -> None:
    setup_responses(
        root_url,
        f"<html><body><a href='{root_url}/test'>link</a>"
        "<a href='http://external.com/test'>link</a></body></html>",
        200,
    )

    spider = Datacrawl(CrawlSettings(root_url=root_url, internal_links_only=True))
    mock_urlopen.side_effect = lambda url: mock_response

    with caplog.at_level(DEBUG):
        spider.crawl(root_url)

    assert "Skipping: External link:" in caplog.text
    assert spider.crawl_result == {root_url: {"urls": [f"{root_url}/test"]}}


@responses.activate
def test_external_links_only(
    mock_urlopen: MagicMock,
    mock_response: MagicMock,
    setup_responses: Callable[[str, str, int], None],
    caplog: LogCaptureFixture,
) -> None:
    setup_responses(
        root_url,
        f"<html><body><a href='{root_url}/test'>link</a>"
        "<a href='http://external.com/test'>link</a></body></html>",
        200,
    )

    spider = Datacrawl(CrawlSettings(root_url=root_url, external_links_only=True))
    mock_urlopen.side_effect = lambda url: mock_response

    with caplog.at_level(DEBUG):
        spider.crawl(root_url)

    assert "Skipping: Internal link:" in caplog.text
    assert spider.crawl_result == {root_url: {"urls": ["http://external.com/test"]}}


@responses.activate
def test_external_and_internal_links_only() -> None:
    with pytest.raises(ValueError):
        Datacrawl(
            CrawlSettings(root_url=root_url, internal_links_only=True, external_links_only=True)
        )


@patch.object(Datacrawl, "crawl")
@patch.object(Datacrawl, "save_results")
def test_start(mock_save_results: MagicMock, mock_crawl: MagicMock) -> None:
    spider = Datacrawl(CrawlSettings(root_url=root_url, max_links=10))
    mock_crawl.side_effect = lambda url: spider.crawl_result.update(
        {url: {"urls": [f"{root_url}/test"]}}
    )

    spider.start()

    assert mock_crawl.call_count == 1
    assert root_url in spider.crawl_result
    assert spider.crawl_result[root_url]["urls"] == [f"{root_url}/test"]


@patch.object(Datacrawl, "crawl")
@patch.object(Datacrawl, "save_results")
def test_start_with_save_to_file(mock_save_results: MagicMock, mock_crawl: MagicMock) -> None:
    spider = Datacrawl(CrawlSettings(root_url=root_url, max_links=10, save_to_file="file.txt"))
    mock_crawl.side_effect = lambda url: spider.crawl_result.update(
        {url: {"urls": [f"{root_url}/test"]}}
    )

    spider.start()

    assert mock_crawl.call_count == 1
    assert root_url in spider.crawl_result
    assert spider.crawl_result[root_url]["urls"] == [f"{root_url}/test"]

    mock_save_results.assert_called_once()


@responses.activate
@patch("urllib.request.urlopen")
def test_respect_robots_txt(
    mock_urlopen: MagicMock,
    setup_responses: Callable[[str, str, int], None],
    caplog: LogCaptureFixture,
) -> None:
    setup_responses(
        root_url,
        "<html><body><a href='http://notcrawlable.com'>link</a></body></html>",
        200,
    )
    setup_responses(
        "http://notcrawlable.com",
        f"<html><body><a href='{root_url}'>link</a></body></html>",
        200,
    )

    mock_urlopen.side_effect = lambda url: (
        BytesIO(b"User-agent: *\nAllow: /")
        if url == f"{root_url}/robots.txt"
        else (
            BytesIO(b"User-agent: *\nDisallow: /")
            if url == "http://notcrawlable.com/robots.txt"
            else urllib.error.URLError(f"No mock for {url}")
        )
    )

    spider = Datacrawl(CrawlSettings(root_url=root_url, respect_robots_txt=True))

    with caplog.at_level(DEBUG):
        spider.start()

    assert spider.crawl_result == {root_url: {"urls": ["http://notcrawlable.com"]}}
    assert "Skipped: Url doesn't allow crawling:" in caplog.text
    assert "http://notcrawlable.com/robots.txt" in spider.robots


@responses.activate
@patch("urllib.request.urlopen")
def test_respect_robots_txt_allowed(
    mock_urlopen: MagicMock,
    setup_responses: Callable[[str, str, int], None],
    caplog: LogCaptureFixture,
) -> None:
    setup_responses(root_url, f"<html><body><a href='{root_url}'>link</a></body></html>", 200)

    mock_urlopen.side_effect = lambda url: (
        BytesIO(b"User-agent: *\nAllow: /")
        if url == f"{root_url}/robots.txt"
        else urllib.error.URLError(f"No mock for {url}")
    )

    spider = Datacrawl(CrawlSettings(root_url=root_url, respect_robots_txt=True))

    with caplog.at_level(DEBUG):
        spider.crawl(root_url)

    assert spider.crawl_result == {root_url: {"urls": [root_url]}}


@responses.activate
@patch("urllib.request.urlopen")
def test_respect_robots_txt_not_allowed(
    mock_urlopen: MagicMock,
    setup_responses: Callable[[str, str, int], None],
    caplog: LogCaptureFixture,
) -> None:
    setup_responses(
        root_url,
        "<html><body><a href='http://crawlable.com'>link</a></body></html>",
        200,
    )

    mock_urlopen.side_effect = lambda url: (
        BytesIO(b"User-agent: *\nDisallow: /")
        if url == f"{root_url}/robots.txt"
        else urllib.error.URLError(f"No mock for {url}")
    )

    spider = Datacrawl(CrawlSettings(root_url=root_url, respect_robots_txt=True))

    with caplog.at_level(DEBUG):
        spider.crawl(root_url)

    assert spider.crawl_result == {}
    assert "Skipped: Url doesn't allow crawling:" in caplog.text
    assert f"{root_url}/robots.txt" in spider.robots


@responses.activate
@patch("urllib.request.urlopen")
def test_respect_robots_txt_disabled(
    mock_urlopen: MagicMock,
    setup_responses: Callable[[str, str, int], None],
    caplog: LogCaptureFixture,
) -> None:
    setup_responses(
        root_url,
        "<html><body><a href='http://notcrawlable.com'>link</a></body></html>",
        200,
    )
    setup_responses(
        "http://notcrawlable.com",
        f"<html><body><a href='{root_url}'>link</a></body></html>",
        200,
    )

    mock_urlopen.side_effect = lambda url: (
        BytesIO(b"User-agent: *\nAllow: /")
        if url == f"{root_url}/robots.txt"
        else (
            BytesIO(b"User-agent: *\nDisallow: /")
            if url == "http://notcrawlable.com/robots.txt"
            else urllib.error.URLError(f"No mock for {url}")
        )
    )

    with caplog.at_level(WARNING):
        spider = Datacrawl(CrawlSettings(root_url=root_url, respect_robots_txt=False))

    assert "Ignoring robots.txt files! You might be at risk of:" in caplog.text

    with caplog.at_level(DEBUG):
        spider.start()

    assert spider.crawl_result == {
        root_url: {"urls": ["http://notcrawlable.com"]},
        "http://notcrawlable.com": {"urls": [root_url]},
    }

    assert "Skipped: Url doesn't allow crawling:" not in caplog.text
    assert "http://notcrawlable.com/robots.txt" not in spider.robots


@responses.activate
@patch("urllib.request.urlopen")
@patch("time.sleep", return_value=None)
def test_respect_robots_txt_crawl_delay(
    mock_sleep: MagicMock,
    mock_urlopen: MagicMock,
    setup_responses: Callable[[str, str, int], None],
    caplog: LogCaptureFixture,
) -> None:
    setup_responses(
        root_url,
        "<html><body><a href='http://notcrawlable.com'>link</a></body></html>",
        200,
    )

    mock_urlopen.side_effect = lambda url: (
        BytesIO(b"User-agent: *\nAllow: /\ncrawl-delay: 1")
        if url == f"{root_url}/robots.txt"
        else urllib.error.URLError(f"No mock for {url}")
    )

    spider = Datacrawl(CrawlSettings(root_url=root_url, respect_robots_txt=True))

    with caplog.at_level(DEBUG):
        spider.crawl(root_url)

    assert mock_sleep.call_count == 1
    mock_sleep.assert_called_with(1.0)
    assert spider.crawl_result == {root_url: {"urls": ["http://notcrawlable.com"]}}


def test_crawl_no_root_url() -> None:
    with pytest.raises(ValueError):
        Datacrawl(CrawlSettings(verbose=False))


@patch("time.sleep")
@responses.activate
def test_crawl_url_transient_retry(
    mock_sleep: MagicMock,
    setup_responses: Callable[[str, str, int], None],
    caplog: LogCaptureFixture,
) -> None:
    setup_responses(
        root_url,
        f"<html><body><a href='{root_url}'>link</a></body></html>",
        503,
    )

    spider = Datacrawl(CrawlSettings(root_url=root_url, respect_robots_txt=False))

    with caplog.at_level(ERROR):
        spider.crawl(root_url)

    assert spider.crawl_result == {}
    assert len(responses.calls) == 6

    expected_delays = [1, 2, 3, 4, 5]
    actual_delays = [call.args[0] for call in mock_sleep.call_args_list]
    assert actual_delays == expected_delays

    assert "Transient HTTP error occurred:" in caplog.text


@patch("time.sleep")
@responses.activate
def test_crawl_url_transient_retry_custom_retry_amount(
    mock_sleep: MagicMock,
    setup_responses: Callable[[str, str, int], None],
    caplog: LogCaptureFixture,
) -> None:
    setup_responses(
        root_url,
        f"<html><body><a href='{root_url}'>link</a></body></html>",
        503,
    )

    spider = Datacrawl(
        CrawlSettings(root_url=root_url, max_retry_attempts=10, respect_robots_txt=False)
    )

    with caplog.at_level(ERROR):
        spider.crawl(root_url)

    assert spider.crawl_result == {}
    assert len(responses.calls) == 11

    expected_delays = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    actual_delays = [call.args[0] for call in mock_sleep.call_args_list]
    assert actual_delays == expected_delays

    assert "Transient HTTP error occurred:" in caplog.text
