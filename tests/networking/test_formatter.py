from tiny_web_crawler.networking.formatter import format_url, DEFAULT_SCHEME

def test_format_url() -> None:
    assert (
        format_url("/test", "http://example.com")
        == "http://example.com/test"
    )

    assert (
        format_url("http://example.com/test", "http://example.com")
        == "http://example.com/test"
    )

    assert (
        format_url('path1/path2', 'http://example.com')
        == 'http://example.com/path1/path2'
    )

    assert (
        format_url('/path1/path2', 'http://example.com')
        == 'http://example.com/path1/path2'
    )

    assert (
        format_url('path.com', 'http://example.com')
        == DEFAULT_SCHEME + 'path.com'
    )
