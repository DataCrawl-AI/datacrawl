import pytest

from tiny_web_crawler.networking.formatter import format_url, DEFAULT_SCHEME

@pytest.mark.parametrize(
    "url, base_url, expected",
    [
        ("/test", "http://example.com", "http://example.com/test"),
        ("http://example.com/test", "http://example.com", "http://example.com/test"),
        ("path1/path2", "http://example.com", "http://example.com/path1/path2"),
        ("/path1/path2", "http://example.com", "http://example.com/path1/path2"),
        ("path.com", "http://example.com", f"{DEFAULT_SCHEME}path.com"),
    ]
)
def test_format_url(url: str, base_url: str, expected: str) -> None:
    assert format_url(url, base_url) == expected
