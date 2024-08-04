import urllib.parse
import urllib.robotparser
from typing import Optional

import requests


def get_robots_txt_url(url: str) -> str:
    """
    Returns a url to a robots.txt file from the provided url.

    Args:
        url (str): The URL to get the robots.txt of.

    Returns:
        str: The robots.txt url.
    """

    parsed_url = urllib.parse.urlparse(url)

    return parsed_url.scheme + "://" + parsed_url.netloc + "/robots.txt"


def is_robots_txt_allowed(
    url: str, robot_parser: Optional[urllib.robotparser.RobotFileParser] = None
) -> bool:
    """
    Checks if the provided URL can be crawled, according to its corresponding robots.txt file

    Args:
        url (str): The URL to check.

    Returns:
        bool: True if the URL can be crawled, False otherwise.
    """

    user_agent = requests.utils.default_user_agent()

    if robot_parser is None:
        robot_parser = setup_robots_txt_parser(url)

    return robot_parser.can_fetch(user_agent, url)


def setup_robots_txt_parser(robots_txt_url: str) -> urllib.robotparser.RobotFileParser:
    """
    Creates a RobotFileParser object from the given url to a robots.txt file

    Args:
        robot_txt_url (str): The URL to the robots.txt file.

    Returns:
        urllib.robotparser.RobotFileParser:
        The RobotFileParser object with the url already read.
    """

    robot_parser = urllib.robotparser.RobotFileParser()
    robot_parser.set_url(robots_txt_url)
    robot_parser.read()

    return robot_parser
