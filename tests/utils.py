from typing import Union

import responses


def setup_mock_response(url: str, status: int, body: Union[str, Exception]) -> None:
    responses.add(responses.GET, url, body=body, status=status, content_type="text/html")
