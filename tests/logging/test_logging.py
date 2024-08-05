import logging
from logging import DEBUG, ERROR, INFO

import pytest
import responses
from datacrawl import CrawlSettings, Datacrawl
from datacrawl.logger import (
    LOGGER_NAME,
    get_logger,
    set_logging_level,
)

from tests.utils import setup_mock_response


def test_get_logger() -> None:
    logger = get_logger()

    assert isinstance(logger, logging.Logger)
    assert logger.name == LOGGER_NAME


def test_set_logging_level(caplog: pytest.LogCaptureFixture) -> None:
    logger = get_logger()

    set_logging_level(ERROR)

    logger.info("123")
    logger.error("456")

    assert logger.getEffectiveLevel() == ERROR
    assert "123" not in caplog.text
    assert "456" in caplog.text


def test_verbose_logging_level() -> None:
    logger = get_logger()

    Datacrawl(CrawlSettings(root_url="http://example.com", verbose=True))

    assert logger.getEffectiveLevel() == DEBUG

    Datacrawl(CrawlSettings(root_url="http://example.com", verbose=False))

    assert logger.getEffectiveLevel() == INFO


@responses.activate
def test_verbose_true(caplog: pytest.LogCaptureFixture) -> None:
    setup_mock_response(url="http://example.com", body="<html><body></body></html>", status=200)

    spider = Datacrawl(CrawlSettings(root_url="http://example.com", verbose=True))
    spider.start()

    assert len(caplog.text) > 0
    assert "DEBUG" in caplog.text


@responses.activate
def test_verbose_false_no_errors(caplog: pytest.LogCaptureFixture) -> None:
    setup_mock_response(url="http://example.com", body="<html><body></body></html>", status=200)

    spider = Datacrawl(CrawlSettings(root_url="http://example.com", verbose=False))
    spider.start()

    assert len(caplog.text) == 0
