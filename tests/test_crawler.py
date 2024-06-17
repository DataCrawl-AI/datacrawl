from unittest.mock import MagicMock, mock_open, patch

import responses

import requests

from tiny_web_crawler.crawler import Spider, DEFAULT_SCHEME

def test_is_valid_url() -> None:
    assert Spider.is_valid_url("http://example.com") is True
    assert Spider.is_valid_url('invalid') is False


def test_format_url() -> None:
    spider = Spider("http://example.com", 10)

    assert (
        spider.format_url("/test", "http://example.com")
        == "http://example.com/test"
    )

    assert (
        spider.format_url("http://example.com/test", "http://example.com")
        == "http://example.com/test"
    )

    assert (
        spider.format_url('path1/path2', 'http://example.com')
        == 'http://example.com/path1/path2'
    )

    assert (
        spider.format_url('/path1/path2', 'http://example.com')
        == 'http://example.com/path1/path2'
    )

    assert (
        spider.format_url('path.com', 'http://example.com')
        == DEFAULT_SCHEME + 'path.com'
    )


@responses.activate
def test_fetch_url() -> None:
    responses.add(
        responses.GET,
        "http://example.com",
        body="<html><body><a href='http://example.com'>link</a></body></html>",
        status=200,
    )
    spider = Spider(root_url="http://example.com", max_links=2)
    resp = spider.fetch_url("http://example.com")

    assert resp is not None
    assert resp.text == "link"


@responses.activate
def test_fetch_url_connection_error(capsys) -> None: # type: ignore
    spider = Spider("http://connection.error")

    # Fetch url whose response isn't mocked to raise ConnectionError
    resp = spider.fetch_url("http://connection.error")

    captured = capsys.readouterr()
    assert "Connection error occurred:" in captured.out
    assert resp is None


@responses.activate
def test_fetch_url_http_error(capsys) -> None: # type: ignore
    responses.add(
        responses.GET,
        "http://http.error/404",
        body="<html><body><a href='http://http.error'>link</a></body></html>",
        status=404
    )
    responses.add(
        responses.GET,
        "http://http.error/408",
        body="<html><body><a href='http://http.error'>link</a></body></html>",
        status=408
    )
    responses.add(
        responses.GET,
        "http://http.error/403",
        body="<html><body><a href='http://http.error'>link</a></body></html>",
        status=403
    )

    spider = Spider("http://http.error")

    resp404 = spider.fetch_url("http://http.error/404")

    captured = capsys.readouterr()
    assert "HTTP error occurred:" in captured.out
    assert resp404 is None

    resp408 = spider.fetch_url("http://http.error/408")

    captured = capsys.readouterr()
    assert "HTTP error occurred:" in captured.out
    assert resp408 is None

    resp403 = spider.fetch_url("http://http.error/403")

    captured = capsys.readouterr()
    assert "HTTP error occurred:" in captured.out
    assert resp403 is None


@responses.activate
def test_fetch_url_timeout_error(capsys) -> None: # type: ignore
    responses.add(
        responses.GET,
        "http://timeout.error",
        body=requests.exceptions.Timeout(),
        status=408
    )

    spider = Spider("http://timeout.error")

    # Fetch url whose response isn't mocked to raise ConnectionError
    resp = spider.fetch_url("http://timeout.error")

    captured = capsys.readouterr()
    assert "Timeout error occurred:" in captured.out
    assert resp is None


@responses.activate
def test_fetch_url_requests_exception(capsys) -> None: # type: ignore
    responses.add(
        responses.GET,
        "http://requests.exception",
        body=requests.exceptions.RequestException(),
        status=404
    )

    spider = Spider("http://requests.exception")

    # Fetch url whose response isn't mocked to raise ConnectionError
    resp = spider.fetch_url("http://requests.exception")

    captured = capsys.readouterr()
    assert "Request error occurred:" in captured.out
    assert resp is None


@responses.activate
def test_crawl() -> None:
    # Mock HTTP response
    responses.add(
        responses.GET,
        "http://example.com",
        body="<html><body><a href='http://example.com/test'>link</a></body></html>",
        status=200,
        content_type="text/html",
    )

    spider = Spider("http://example.com", 10)
    spider.crawl("http://example.com")

    assert "http://example.com" in spider.crawl_result
    assert spider.crawl_result["http://example.com"]["urls"] == [
        "http://example.com/test"
    ]


@responses.activate
def test_save_results() -> None:
    spider = Spider("http://example.com", 10, save_to_file="out.json")
    spider.crawl_result = {
        "http://example.com": {"urls": ["http://example.com/test"]}}

    with patch("builtins.open", mock_open()) as mocked_file:
        spider.save_results()
        mocked_file.assert_called_once_with("out.json", "w", encoding='utf-8')


@responses.activate
def test_url_regex() -> None:
    # Mock HTTP response
    responses.add(
        responses.GET,
        "http://example.com",
        body="<html><body><a href='http://example.com/123'>link</a>"
        +"<a href='http://example.com/test'>link</a></body></html>",
        status=200,
        content_type="text/html",
    )

    # This regex matches strings starting with "http://example.com/"
    # And only have numeric characters after it
    regex = r"http://example\.com/[0-9]+"

    spider = Spider("http://example.com", 0, url_regex=regex)
    spider.start()

    assert spider.crawl_result["http://example.com"]["urls"] == ["http://example.com/123"]

    assert "http://example.com/test" not in spider.crawl_result["http://example.com"]["urls"]


@responses.activate
def test_include_body() -> None:
    # Mock HTTP response
    responses.add(
        responses.GET,
        "http://example.com",
        body="<html><body><a href='http://example.com/test'>link</a></body></html>",
        status=200,
        content_type="text/html",
    )
    responses.add(
        responses.GET,
        "http://example.com/test",
        body="<html><body><h>This is a header</h></body></html>",
        status=200,
        content_type="text/html",
    )

    spider = Spider("http://example.com", include_body=True)
    spider.start()

    assert (
        spider.crawl_result["http://example.com"]["body"]
        == '<html><body><a href="http://example.com/test">link</a></body></html>'
    )
    assert (
        spider.crawl_result["http://example.com/test"]["body"]
        == "<html><body><h>This is a header</h></body></html>"
    )


@patch.object(Spider, "crawl")
@patch.object(Spider, "save_results")
def test_start(mock_save_results: MagicMock, mock_crawl: MagicMock) -> None:
    spider = Spider("http://example.com", 10)
    mock_crawl.side_effect = lambda url: spider.crawl_result.update(
        {url: {"urls": ["http://example.com/test"]}}
    )
    print(mock_save_results)

    spider.start()

    assert mock_crawl.call_count == 1
    assert "http://example.com" in spider.crawl_result
    assert spider.crawl_result["http://example.com"]["urls"] == [
        "http://example.com/test"
    ]
