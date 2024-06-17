from tiny_web_crawler.networking.validator import is_valid_url

def test_is_valid_url() -> None:
    assert is_valid_url("http://example.com") is True
    assert is_valid_url('invalid') is False
