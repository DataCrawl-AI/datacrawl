# conftest.py
from typing import Callable, Generator
from unittest.mock import MagicMock, patch

import pytest

from tests.utils import setup_mock_response

root_url = "http://example.com"


@pytest.fixture
def mock_urlopen() -> Generator[MagicMock, None, None]:
    with patch("urllib.request.urlopen") as mock:
        yield mock


@pytest.fixture
def mock_response() -> MagicMock:
    response = MagicMock()
    response.read.return_value = b""
    response.status = 200
    return response


@pytest.fixture
def setup_responses() -> Callable[[str, str, int], None]:
    def _setup_responses(url: str, body: str, status: int = 200) -> None:
        setup_mock_response(url=url, body=body, status=status)

    return _setup_responses
