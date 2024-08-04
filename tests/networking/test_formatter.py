import pytest
from datacrawl.networking.formatter import DEFAULT_SCHEME, format_url


@pytest.mark.parametrize(
    "url, base_url, expected",
    [
        ("/test", "http://example.com", "http://example.com/test"),
        ("http://example.com/test", "http://example.com", "http://example.com/test"),
        ("path1/path2", "http://example.com", "http://example.com/path1/path2"),
        ("/path1/path2", "http://example.com", "http://example.com/path1/path2"),
        ("path.com", "http://example.com", f"{DEFAULT_SCHEME}path.com"),
    ],
)
def test_format_url(url: str, base_url: str, expected: str) -> None:
    assert format_url(url, base_url) == expected
