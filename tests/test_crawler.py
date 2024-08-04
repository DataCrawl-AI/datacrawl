import urllib.error
from io import BytesIO
from logging import DEBUG, ERROR, WARNING
from unittest.mock import MagicMock, mock_open, patch

import pytest
import responses
from tiny_web_crawler import Spider, SpiderSettings

from tests.utils import setup_mock_response


@responses.activate
def test_crawl() -> None:
    setup_mock_response(
        url="http://example.com",
        body="<html><body><a href='http://example.com/test'>link</a></body></html>",
        status=200,
    )
    setup_mock_response(
        url="http://example.com/test",
        body="<html><body><a href='http://example.com'>link</a></body></html>",
        status=200,
    )

    spider = Spider(SpiderSettings(root_url="http://example.com", max_links=10))
    spider.crawl("http://example.com")

    assert "http://example.com" in spider.crawl_result
    assert spider.crawl_result["http://example.com"]["urls"] == ["http://example.com/test"]

    spider.crawl("http://example.com/test")

    assert "http://example.com/test" in spider.crawl_result
    assert spider.crawl_result["http://example.com/test"]["urls"] == ["http://example.com"]


@responses.activate
def test_crawl_invalid_url(caplog) -> None:  # type: ignore
    spider = Spider(SpiderSettings(root_url="http://example.com"))

    with caplog.at_level(DEBUG):
        spider.crawl("invalid_url")

    assert "Invalid url to crawl:" in caplog.text
    assert spider.crawl_result == {}


@responses.activate
def test_crawl_already_crawled_url(caplog) -> None:  # type: ignore
    setup_mock_response(
        url="http://example.com",
        body="<html><body><a href='http://example.com'>link</a></body></html>",
        status=200,
    )

    spider = Spider(SpiderSettings(root_url="http://example.com"))

    with caplog.at_level(DEBUG):
        spider.crawl("http://example.com")
        spider.crawl("http://example.com")

    assert "URL already crawled:" in caplog.text
    assert spider.crawl_result == {"http://example.com": {"urls": ["http://example.com"]}}


@responses.activate
def test_crawl_unfetchable_url() -> None:
    setup_mock_response(
        url="http://example.com",
        body="<html><body><a href='http://example.com'>link</a></body></html>",
        status=404,
    )

    spider = Spider(SpiderSettings(root_url="http://example.com"))

    spider.crawl("http://example.com")
    assert spider.crawl_result == {}


@responses.activate
def test_crawl_found_invalid_url(caplog) -> None:  # type: ignore
    setup_mock_response(
        url="http://example.com",
        body="<html><body><a href='^invalidurl^'>link</a></body></html>",
        status=200,
    )

    spider = Spider(SpiderSettings(root_url="http://example.com"))

    with caplog.at_level(DEBUG):
        spider.crawl("http://example.com")

    assert "Invalid url:" in caplog.text
    assert spider.crawl_result == {"http://example.com": {"urls": []}}


@responses.activate
def test_crawl_found_duplicate_url() -> None:
    setup_mock_response(
        url="http://example.com",
        body="<html><body><a href='http://duplicate.com'>link1</a>"
        + "<a href='http://duplicate.com'>link2</a></body></html>",
        status=200,
    )

    spider = Spider(SpiderSettings(root_url="http://example.com"))
    spider.crawl("http://example.com")

    assert spider.crawl_result == {"http://example.com": {"urls": ["http://duplicate.com"]}}


@responses.activate
def test_crawl_no_urls_in_page() -> None:
    setup_mock_response(url="http://example.com", body="<html><body></body></html>", status=200)

    spider = Spider(SpiderSettings(root_url="http://example.com"))
    spider.crawl("http://example.com")

    assert spider.crawl_result == {"http://example.com": {"urls": []}}


@responses.activate
def test_save_results() -> None:
    spider = Spider(
        SpiderSettings(root_url="http://example.com", max_links=10, save_to_file="out.json")
    )
    spider.crawl_result = {"http://example.com": {"urls": ["http://example.com/test"]}}

    with patch("builtins.open", mock_open()) as mocked_file:
        spider.save_results()
        mocked_file.assert_called_once_with("out.json", "w", encoding="utf-8")


@responses.activate
def test_url_regex() -> None:
    setup_mock_response(
        url="http://example.com",
        body="<html><body><a href='http://example.com/123'>link</a>"
        + "<a href='http://example.com/test'>link</a></body></html>",
        status=200,
    )

    # This regex matches strings starting with "http://example.com/"
    # And only have numeric characters after it
    regex = r"http://example\.com/[0-9]+"

    spider = Spider(SpiderSettings(root_url="http://example.com", url_regex=regex))
    spider.start()

    assert spider.crawl_result["http://example.com"]["urls"] == ["http://example.com/123"]

    assert "http://example.com/test" not in spider.crawl_result["http://example.com"]["urls"]


@responses.activate
def test_include_body() -> None:
    setup_mock_response(
        url="http://example.com",
        body="<html><body><a href='http://example.com/test'>link</a></body></html>",
        status=200,
    )
    setup_mock_response(
        url="http://example.com/test",
        body="<html><body><h>This is a header</h></body></html>",
        status=200,
    )

    spider = Spider(SpiderSettings(root_url="http://example.com", include_body=True))
    spider.start()

    assert (
        spider.crawl_result["http://example.com"]["body"]
        == '<html><body><a href="http://example.com/test">link</a></body></html>'
    )
    assert (
        spider.crawl_result["http://example.com/test"]["body"]
        == "<html><body><h>This is a header</h></body></html>"
    )


@responses.activate
def test_internal_links_only(caplog) -> None:  # type: ignore
    setup_mock_response(
        url="http://internal.com",
        body="<html><body><a href='http://internal.com/test'>link</a>"
        + "<a href='http://external.com/test'>link</a></body></html>",
        status=200,
    )

    spider = Spider(SpiderSettings(root_url="http://internal.com", internal_links_only=True))

    with caplog.at_level(DEBUG):
        spider.crawl("http://internal.com")

    assert "Skipping: External link:" in caplog.text
    assert spider.crawl_result == {"http://internal.com": {"urls": ["http://internal.com/test"]}}


@responses.activate
def test_external_links_only(caplog) -> None:  # type: ignore
    setup_mock_response(
        url="http://internal.com",
        body="<html><body><a href='http://internal.com/test'>link</a>"
        + "<a href='http://external.com/test'>link</a></body></html>",
        status=200,
    )

    spider = Spider(SpiderSettings(root_url="http://internal.com", external_links_only=True))

    with caplog.at_level(DEBUG):
        spider.crawl("http://internal.com")

    assert "Skipping: Internal link:" in caplog.text
    assert spider.crawl_result == {"http://internal.com": {"urls": ["http://external.com/test"]}}


@responses.activate
def test_external_and_internal_links_only() -> None:
    with pytest.raises(ValueError):
        Spider(
            SpiderSettings(
                root_url="http://example.com",
                internal_links_only=True,
                external_links_only=True,
            )
        )


@patch.object(Spider, "crawl")
@patch.object(Spider, "save_results")
def test_start(mock_save_results: MagicMock, mock_crawl: MagicMock) -> None:
    spider = Spider(SpiderSettings(root_url="http://example.com", max_links=10))
    mock_crawl.side_effect = lambda url: spider.crawl_result.update(
        {url: {"urls": ["http://example.com/test"]}}
    )
    print(mock_save_results)

    spider.start()

    assert mock_crawl.call_count == 1
    assert "http://example.com" in spider.crawl_result
    assert spider.crawl_result["http://example.com"]["urls"] == ["http://example.com/test"]


@patch.object(Spider, "crawl")
@patch.object(Spider, "save_results")
def test_start_with_save_to_file(mock_save_results: MagicMock, mock_crawl: MagicMock) -> None:
    spider = Spider(
        SpiderSettings(root_url="http://example.com", max_links=10, save_to_file="file.txt")
    )
    mock_crawl.side_effect = lambda url: spider.crawl_result.update(
        {url: {"urls": ["http://example.com/test"]}}
    )

    spider.start()

    assert mock_crawl.call_count == 1
    assert "http://example.com" in spider.crawl_result
    assert spider.crawl_result["http://example.com"]["urls"] == ["http://example.com/test"]

    mock_save_results.assert_called_once()


@responses.activate
@patch("urllib.request.urlopen")
def test_respect_robots_txt(mock_urlopen, caplog) -> None:  # type: ignore
    setup_mock_response(
        url="http://crawlable.com",
        body="<html><body><a href='http://notcrawlable.com'>link</a></body></html>",
        status=200,
    )
    setup_mock_response(
        url="http://notcrawlable.com",
        body="<html><body><a href='http://crawlable.com'>link</a></body></html>",
        status=200,
    )

    mock_urlopen.side_effect = lambda url: (
        BytesIO(b"User-agent: *\nAllow: /")
        if url == "http://crawlable.com/robots.txt"
        else (
            BytesIO(b"User-agent: *\nDisallow: /")
            if url == "http://notcrawlable.com/robots.txt"
            else urllib.error.URLError(f"No mock for {url}")
        )
    )

    spider = Spider(SpiderSettings(root_url="http://crawlable.com", respect_robots_txt=True))

    with caplog.at_level(DEBUG):
        spider.start()

    assert spider.crawl_result == {"http://crawlable.com": {"urls": ["http://notcrawlable.com"]}}

    assert "Skipped: Url doesn't allow crawling:" in caplog.text

    assert "http://notcrawlable.com/robots.txt" in spider.robots


@responses.activate
@patch("urllib.request.urlopen")
def test_respect_robots_txt_allowed(mock_urlopen, caplog) -> None:  # type: ignore
    setup_mock_response(
        url="http://crawlable.com",
        body="<html><body><a href='http://crawlable.com'>link</a></body></html>",
        status=200,
    )

    mock_urlopen.side_effect = lambda url: (
        BytesIO(b"User-agent: *\nAllow: /")
        if url == "http://crawlable.com/robots.txt"
        else urllib.error.URLError(f"No mock for {url}")
    )

    spider = Spider(SpiderSettings(root_url="http://crawlable.com", respect_robots_txt=True))

    with caplog.at_level(DEBUG):
        spider.crawl("http://crawlable.com")

    assert spider.crawl_result == {"http://crawlable.com": {"urls": ["http://crawlable.com"]}}


@responses.activate
@patch("urllib.request.urlopen")
def test_respect_robots_txt_not_allowed(mock_urlopen, caplog) -> None:  # type: ignore
    setup_mock_response(
        url="http://notcrawlable.com",
        body="<html><body><a href='http://crawlable.com'>link</a></body></html>",
        status=200,
    )

    mock_urlopen.side_effect = lambda url: (
        BytesIO(b"User-agent: *\nDisallow: /")
        if url == "http://notcrawlable.com/robots.txt"
        else urllib.error.URLError(f"No mock for {url}")
    )

    spider = Spider(SpiderSettings(root_url="http://notcrawlable.com", respect_robots_txt=True))

    with caplog.at_level(DEBUG):
        spider.crawl("http://notcrawlable.com")

    assert spider.crawl_result == {}

    assert "Skipped: Url doesn't allow crawling:" in caplog.text

    assert "http://notcrawlable.com/robots.txt" in spider.robots


@responses.activate
@patch("urllib.request.urlopen")
def test_respect_robots_txt_disabled(mock_urlopen, caplog) -> None:  # type: ignore
    setup_mock_response(
        url="http://crawlable.com",
        body="<html><body><a href='http://notcrawlable.com'>link</a></body></html>",
        status=200,
    )
    setup_mock_response(
        url="http://notcrawlable.com",
        body="<html><body><a href='http://crawlable.com'>link</a></body></html>",
        status=200,
    )

    mock_urlopen.side_effect = lambda url: (
        BytesIO(b"User-agent: *\nAllow: /")
        if url == "http://crawlable.com/robots.txt"
        else (
            BytesIO(b"User-agent: *\nDisallow: /")
            if url == "http://notcrawlable.com/robots.txt"
            else urllib.error.URLError(f"No mock for {url}")
        )
    )

    with caplog.at_level(WARNING):
        spider = Spider(SpiderSettings(root_url="http://crawlable.com", respect_robots_txt=False))

    assert "Ignoring robots.txt files! You might be at risk of:" in caplog.text

    with caplog.at_level(DEBUG):
        spider.start()

    assert spider.crawl_result == {
        "http://crawlable.com": {"urls": ["http://notcrawlable.com"]},
        "http://notcrawlable.com": {"urls": ["http://crawlable.com"]},
    }

    assert "Skipped: Url doesn't allow crawling:" not in caplog.text

    assert "http://notcrawlable.com/robots.txt" not in spider.robots


@responses.activate
@patch("urllib.request.urlopen")
@patch("time.sleep", return_value=None)
def test_respect_robots_txt_crawl_delay(mock_sleep, mock_urlopen, caplog) -> None:  # type: ignore
    setup_mock_response(
        url="http://crawlable.com",
        body="<html><body><a href='http://notcrawlable.com'>link</a></body></html>",
        status=200,
    )

    mock_urlopen.side_effect = lambda url: (
        BytesIO(b"User-agent: *\nAllow: /\ncrawl-delay: 1")
        if url == "http://crawlable.com/robots.txt"
        else urllib.error.URLError(f"No mock for {url}")
    )

    spider = Spider(SpiderSettings(root_url="http://crawlable.com", respect_robots_txt=True))

    with caplog.at_level(DEBUG):
        spider.crawl("http://crawlable.com")

    assert mock_sleep.call_count == 1
    mock_sleep.assert_called_with(1.0)

    assert spider.crawl_result == {"http://crawlable.com": {"urls": ["http://notcrawlable.com"]}}


def test_crawl_no_root_url() -> None:
    with pytest.raises(ValueError):
        Spider(SpiderSettings(verbose=False))


@patch("time.sleep")
@responses.activate
def test_crawl_url_transient_retry(mock_sleep, caplog) -> None:  # type: ignore
    setup_mock_response(
        url="http://transient.error",
        body="<html><body><a href='http://transient.error'>link</a></body></html>",
        status=503,
    )

    spider = Spider(SpiderSettings(root_url="http://transient.error", respect_robots_txt=False))

    with caplog.at_level(ERROR):
        spider.crawl("http://transient.error")

    assert spider.crawl_result == {}

    assert len(responses.calls) == 6

    expected_delays = [1, 2, 3, 4, 5]
    actual_delays = [call.args[0] for call in mock_sleep.call_args_list]
    assert actual_delays == expected_delays

    assert "Transient HTTP error occurred:" in caplog.text


@patch("time.sleep")
@responses.activate
def test_crawl_url_transient_retry_custom_retry_amount(mock_sleep, caplog) -> None:  # type: ignore
    setup_mock_response(
        url="http://transient.error",
        body="<html><body><a href='http://transient.error'>link</a></body></html>",
        status=503,
    )

    spider = Spider(
        SpiderSettings(
            root_url="http://transient.error",
            max_retry_attempts=10,
            respect_robots_txt=False,
        )
    )

    with caplog.at_level(ERROR):
        spider.crawl("http://transient.error")

    assert spider.crawl_result == {}

    assert len(responses.calls) == 11

    expected_delays = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    actual_delays = [call.args[0] for call in mock_sleep.call_args_list]
    assert actual_delays == expected_delays

    assert "Transient HTTP error occurred:" in caplog.text
