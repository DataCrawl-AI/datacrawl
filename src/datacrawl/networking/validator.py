import validators


def is_valid_url(url: str) -> bool:
    """
    Checks if the provided URL is valid.

    Args:
        url (str): The URL to validate.

    Returns:
        bool: True if the URL is valid, False otherwise.
    """
    return bool(validators.url(url))
