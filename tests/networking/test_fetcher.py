
import responses
import requests

from tiny_web_crawler.networking.fetcher import fetch_url
from tiny_web_crawler.logging import ERROR
from tests.utils import setup_mock_response


@responses.activate
def test_fetch_url() -> None:
    setup_mock_response(
        url="http://example.com",
        body="<html><body><a href='http://example.com'>link</a></body></html>",
        status=200
    )

    resp = fetch_url("http://example.com")

    assert resp is not None
    assert resp.text == "link"


@responses.activate
def test_fetch_url_connection_error(caplog) -> None: # type: ignore

    with caplog.at_level(ERROR):
        # Fetch url whose response isn't mocked to raise ConnectionError
        resp = fetch_url("http://connection.error")

    assert "Connection error occurred:" in caplog.text
    assert resp is None


@responses.activate
def test_fetch_url_http_error(caplog) -> None: # type: ignore
    error_codes = [403, 404, 412]

    for error_code in error_codes:
        setup_mock_response(
            url=f"http://http.error/{error_code}",
            body="<html><body><a href='http://http.error'>link</a></body></html>",
            status=error_code
            )

        with caplog.at_level(ERROR):
            resp = fetch_url(f"http://http.error/{error_code}")

        assert "HTTP error occurred:" in caplog.text
        assert resp is None


@responses.activate
def test_fetch_url_timeout_error(caplog) -> None: # type: ignore
    setup_mock_response(
        url="http://timeout.error",
        body=requests.exceptions.Timeout(),
        status=408
    )

    with caplog.at_level(ERROR):
        # Fetch url whose response isn't mocked to raise ConnectionError
        resp = fetch_url("http://timeout.error")

    assert "Timeout error occurred:" in caplog.text
    assert resp is None


@responses.activate
def test_fetch_url_requests_exception(caplog) -> None: # type: ignore
    setup_mock_response(
        url="http://requests.exception",
        body=requests.exceptions.RequestException(),
        status=404
    )

    with caplog.at_level(ERROR):
        # Fetch url whose response isn't mocked to raise ConnectionError
        resp = fetch_url("http://requests.exception")

    assert "Request error occurred:" in caplog.text
    assert resp is None
