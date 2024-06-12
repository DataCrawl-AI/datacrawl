import requests
import pytest
import urllib.request
from unittest.mock import patch, MagicMock, mock_open
from crawler.crawler import Spider
import responses


def test_is_valid_url():
    assert Spider.is_valid_url("http://example.com") is True
    # assert Spider.is_valid_url('invalid') is False


def test_format_url():
    spider = Spider("http://example.com", 10)
    assert spider.format_url(
        "/test", "http://example.com") == "http://example.com/test"
    assert spider.format_url("http://example.com/test",
                             "http://example.com") == "http://example.com/test"


@responses.activate
def test_fetch_url():
    responses.add(responses.GET, 'http://example.com',
                  body="<html><body><a href='http://example.com'>link</a></body></html>", status=200)
    spider = Spider(root_url='http://example.com', max_links=2)
    resp = spider.fetch_url('http://example.com')

    assert resp.text == 'link'


@responses.activate
def test_crawl():
    # Mock HTTP response
    responses.add(responses.GET, 'http://example.com',
                  body="<html><body><a href='http://example.com/test'>link</a></body></html>",
                  status=200,
                  content_type='text/html')

    spider = Spider("http://example.com", 10)
    spider.crawl("http://example.com")

    assert "http://example.com" in spider.crawl_result
    assert spider.crawl_result["http://example.com"]["urls"] == [
        "http://example.com/test"]


@responses.activate
def test_save_results():
    spider = Spider("http://example.com", 10, save_to_file="out.json")
    spider.crawl_result = {
        "http://example.com": {"urls": ["http://example.com/test"]}}

    with patch("builtins.open", mock_open()) as mocked_file:
        spider.save_results()
        mocked_file.assert_called_once_with("out.json", "w")


@patch.object(Spider, 'crawl')
@patch.object(Spider, 'save_results')
def test_start(mock_save_results, mock_crawl):
    spider = Spider("http://example.com", 10)
    mock_crawl.side_effect = lambda url: spider.crawl_result.update(
        {url: {'urls': ['http://example.com/test']}})

    spider.start()

    assert mock_crawl.call_count == 1
    assert "http://example.com" in spider.crawl_result
    assert spider.crawl_result["http://example.com"]["urls"] == [
        'http://example.com/test']
