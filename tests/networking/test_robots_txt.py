import urllib.robotparser
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from tiny_web_crawler.networking.robots_txt import (
    get_robots_txt_url,
    is_robots_txt_allowed,
    setup_robots_txt_parser,
)


@pytest.mark.parametrize(
    "url, expected",
    [
        ("http://example", "http://example/robots.txt"),
        ("http://example/path", "http://example/robots.txt"),
        ("https://example/", "https://example/robots.txt"),
        ("http://example/path1/path2/path3/path4", "http://example/robots.txt"),
        ("http://example/path#fragment", "http://example/robots.txt"),
        ("http://example/path?query=test", "http://example/robots.txt"),
    ],
)
def test_get_robots_txt_url(url: str, expected: str) -> None:
    assert get_robots_txt_url(url) == expected


@patch("urllib.request.urlopen")
def test_is_robots_txt_allowed_true(mock_urlopen: MagicMock) -> None:
    # Mock the response content of robots.txt
    mock_response = b"User-agent: *\nAllow: /"
    mock_urlopen.return_value = BytesIO(mock_response)

    assert is_robots_txt_allowed("http://example.com")


@patch("urllib.request.urlopen")
def test_is_robots_txt_allowed_false(mock_urlopen: MagicMock) -> None:
    # Mock the response content of robots.txt
    mock_response = b"User-agent: *\nDisallow: /"
    mock_urlopen.return_value = BytesIO(mock_response)

    assert not is_robots_txt_allowed("http://example.com")


@patch("urllib.request.urlopen")
def test_is_robots_txt_allowed_mixed(mock_urlopen: MagicMock) -> None:
    # Mock the response content of robots.txt
    mock_response = b"User-agent: *\nDisallow: /private"

    mock_urlopen.return_value = BytesIO(mock_response)
    assert is_robots_txt_allowed("http://example.com")

    mock_urlopen.return_value = BytesIO(mock_response)
    assert not is_robots_txt_allowed("http://example.com/private")


def test_is_robots_txt_allowed_no_robots_txt() -> None:
    # Check that websites with no robots.txt are set as crawlable
    assert is_robots_txt_allowed("http://example.com")


def test_setup_robots_txt_parser() -> None:
    robot_parser = setup_robots_txt_parser("http://example.com")

    assert isinstance(robot_parser, urllib.robotparser.RobotFileParser)
