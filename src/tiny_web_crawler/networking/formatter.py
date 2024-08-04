import urllib.parse

import validators

DEFAULT_SCHEME: str = "http://"


def format_url(url: str, base_url: str, scheme: str = DEFAULT_SCHEME) -> str:
    """
    Formats a URL to ensure it is absolute and removes any query parameters or fragments.

    Args:
        url (str): The URL to format.
        base_url (str): The base URL to resolve relative URLs.
        scheme (str): The URL scheme to use (default: 'http://').

    Returns:
        str: The formatted URL.
    """
    parsed_url = urllib.parse.urlparse(url)
    base_url = base_url.rstrip("/")

    if parsed_url.scheme:
        scheme = parsed_url.scheme

    if not parsed_url.scheme and not parsed_url.netloc:
        if validators.url(DEFAULT_SCHEME + parsed_url.path):
            return DEFAULT_SCHEME + parsed_url.path

        if parsed_url.path.startswith("/"):
            return base_url + parsed_url.path

        return f"{base_url}/{parsed_url.path}"

    return f"{scheme}://{parsed_url.netloc}{parsed_url.path}"
