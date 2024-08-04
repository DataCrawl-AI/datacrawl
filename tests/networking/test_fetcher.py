import asyncio
from logging import ERROR
from unittest.mock import patch

import pytest
import requests
import responses
from aiohttp import ClientConnectionError, ClientError
from aioresponses import aioresponses
from bs4 import BeautifulSoup
from tiny_web_crawler.networking.fetcher import fetch_url, fetch_url_async

from tests.utils import setup_mock_response


@pytest.mark.asyncio
async def test_fetch_url_async_success() -> None:
    url = "http://example.com"
    html_content = "<html><body><a href='http://example.com'>link</a></body></html>"

    with aioresponses() as m:
        m.get(url, status=200, body=html_content)

        result = await fetch_url_async(url, retries=1)

        assert result is not None
        assert isinstance(result, BeautifulSoup)
        assert result.find("a").text == "link"


@pytest.mark.asyncio
async def test_fetch_url_async_http_error() -> None:
    url = "http://example.com"

    with aioresponses() as m:
        m.get(url, status=404)

        result = await fetch_url_async(url, retries=1)

        assert result is None


@pytest.mark.asyncio
async def test_fetch_url_async_transient_error_retry() -> None:
    url = "http://example.com"
    html_content = "<html><body><a href='http://example.com'>link</a></body></html>"

    with aioresponses() as m:
        m.get(url, status=503)
        m.get(url, status=200, body=html_content)

        result = await fetch_url_async(url, retries=2)

        assert result is not None
        assert isinstance(result, BeautifulSoup)
        assert result.find("a").text == "link"


@pytest.mark.asyncio
async def test_fetch_url_async_connection_error() -> None:
    url = "http://example.com"

    with aioresponses() as m:
        m.get(url, exception=ClientConnectionError())

        result = await fetch_url_async(url, retries=1)

        assert result is None


@pytest.mark.asyncio
async def test_fetch_url_async_timeout_error() -> None:
    url = "http://example.com"

    with aioresponses() as m:
        m.get(url, exception=asyncio.TimeoutError())

        result = await fetch_url_async(url, retries=1)

        assert result is None


@pytest.mark.asyncio
async def test_fetch_url_async_request_exception() -> None:
    url = "http://example.com"

    with aioresponses() as m:
        m.get(url, exception=ClientError())

        result = await fetch_url_async(url, retries=1)

        assert result is None


@responses.activate
def test_fetch_url() -> None:
    setup_mock_response(
        url="http://example.com",
        body="<html><body><a href='http://example.com'>link</a></body></html>",
        status=200,
    )

    resp = fetch_url("http://example.com", 1)

    assert resp is not None
    assert resp.text == "link"


@responses.activate
def test_fetch_url_connection_error(caplog) -> None:  # type: ignore
    with caplog.at_level(ERROR):
        # Fetch url whose response isn't mocked to raise ConnectionError
        resp = fetch_url("http://connection.error", 1)

    assert "Connection error occurred:" in caplog.text
    assert resp is None


@responses.activate
def test_fetch_url_http_error(caplog) -> None:  # type: ignore
    error_codes = [403, 404, 412]

    for error_code in error_codes:
        setup_mock_response(
            url=f"http://http.error/{error_code}",
            body="<html><body><a href='http://http.error'>link</a></body></html>",
            status=error_code,
        )

        with caplog.at_level(ERROR):
            resp = fetch_url(f"http://http.error/{error_code}", 1)

        assert "HTTP error occurred:" in caplog.text
        assert resp is None


@responses.activate
def test_fetch_url_timeout_error(caplog) -> None:  # type: ignore
    setup_mock_response(url="http://timeout.error", body=requests.exceptions.Timeout(), status=408)

    with caplog.at_level(ERROR):
        # Fetch url whose response isn't mocked to raise ConnectionError
        resp = fetch_url("http://timeout.error", 1)

    assert "Timeout error occurred:" in caplog.text
    assert resp is None


@responses.activate
def test_fetch_url_requests_exception(caplog) -> None:  # type: ignore
    setup_mock_response(
        url="http://requests.exception",
        body=requests.exceptions.RequestException(),
        status=404,
    )

    with caplog.at_level(ERROR):
        # Fetch url whose response isn't mocked to raise ConnectionError
        resp = fetch_url("http://requests.exception", 1)

    assert "Request error occurred:" in caplog.text
    assert resp is None


@patch("time.sleep")
@responses.activate
def test_fetch_url_transient_error_retry_5(mock_sleep, caplog) -> None:  # type: ignore
    setup_mock_response(
        url="http://transient.error",
        body="<html><body><a href='http://transient.error'>link</a></body></html>",
        status=503,
    )

    max_retry_attempts = 5

    with caplog.at_level(ERROR):
        resp = fetch_url("http://transient.error", max_retry_attempts)

    assert resp is None

    # Assert url was fetched once then retried x ammount of times
    assert len(responses.calls) == max_retry_attempts + 1

    # Assert sleep time grew with every request
    expected_delays = [1, 2, 3, 4, 5]
    actual_delays = [call.args[0] for call in mock_sleep.call_args_list]
    assert actual_delays == expected_delays

    assert "Transient HTTP error occurred:" in caplog.text


@patch("time.sleep")
@responses.activate
def test_fetch_url_transient_error_retry_10(mock_sleep, caplog) -> None:  # type: ignore
    setup_mock_response(
        url="http://transient.error",
        body="<html><body><a href='http://transient.error'>link</a></body></html>",
        status=503,
    )

    max_retry_attempts = 10

    with caplog.at_level(ERROR):
        resp = fetch_url("http://transient.error", max_retry_attempts)

    assert resp is None

    # Assert url was fetched once then retried x ammount of times
    assert len(responses.calls) == max_retry_attempts + 1

    # Assert sleep time grew with every request
    expected_delays = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    actual_delays = [call.args[0] for call in mock_sleep.call_args_list]
    assert actual_delays == expected_delays

    assert "Transient HTTP error occurred:" in caplog.text


@patch("time.sleep")
@responses.activate
def test_fetch_url_transient_error_retry_success(mock_sleep, caplog) -> None:  # type: ignore
    setup_mock_response(
        url="http://transient.error",
        body="<html><body><a href='http://transient.error'>link</a></body></html>",
        status=503,
    )
    setup_mock_response(
        url="http://transient.error",
        body="<html><body><a href='http://transient.error'>link</a></body></html>",
        status=200,
    )

    max_retry_attempts = 1

    with caplog.at_level(ERROR):
        resp = fetch_url("http://transient.error", max_retry_attempts)

    assert resp is not None
    assert resp.text == "link"

    # Assert url was fetched 2 times
    assert len(responses.calls) == 2

    # Assert time.sleep was called
    mock_sleep.assert_called_once_with(1)

    assert "Transient HTTP error occurred:" in caplog.text
