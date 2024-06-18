import logging
import responses

from tiny_web_crawler.core.spider import Spider
from tiny_web_crawler.logging import get_logger, set_logging_level, DEBUG, INFO, ERROR, LOGGER_NAME
from tests.utils import setup_mock_response


def test_get_logger() -> None:
    logger = get_logger()

    assert isinstance(logger, logging.Logger)
    assert logger.name == LOGGER_NAME


def test_set_logging_level(caplog) -> None: # type: ignore
    logger = get_logger()

    set_logging_level(ERROR)

    logger.info("123")
    logger.error("456")

    assert logger.getEffectiveLevel() == ERROR
    assert "123" not in caplog.text
    assert "456" in caplog.text


def test_verbose_logging_level() -> None:
    logger = get_logger()

    spider = Spider("http://example.com", verbose=True) # pylint: disable=unused-variable

    assert logger.getEffectiveLevel() == DEBUG

    spider = Spider("http://example.com", verbose=False) # pylint: disable=unused-variable

    assert logger.getEffectiveLevel() == INFO


@responses.activate
def test_verbose_true(caplog) -> None: # type: ignore
    setup_mock_response(
        url="http://example.com",
        body="<html><body></body></html>",
        status=200
    )

    spider = Spider("http://example.com", verbose=True)
    spider.start()

    assert len(caplog.text) > 0
    assert "DEBUG" in caplog.text


@responses.activate
def test_verbose_false_no_errors(caplog) -> None: # type: ignore
    setup_mock_response(
        url="http://example.com",
        body="<html><body></body></html>",
        status=200
    )

    spider = Spider("http://example.com", verbose=False)
    spider.start()

    assert len(caplog.text) == 0


@responses.activate
def test_verbose_false_errors(caplog) -> None: # type: ignore
    setup_mock_response(
        url="http://example.com",
        body="<html><body><a href='invalidurl'>link</a>",
        status=200
    )

    spider = Spider("http://example.com", verbose=False)
    spider.start()

    assert "DEBUG" not in caplog.text
    assert "ERROR" in caplog.text
    assert len(caplog.text) > 0
