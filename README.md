# Tiny Web Crawler

[![CI](https://github.com/indrajithi/tiny-web-crawler/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/indrajithi/tiny-web-crawler/actions/workflows/ci.yml)
[![Stable Version](https://img.shields.io/pypi/v/tiny-web-crawler?label=stable)](https://pypi.org/project/tiny-web-crawler/#history)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/tiny-web-crawler)](https://pypi.org/project/tiny-web-crawler/)
[![Download Stats](https://img.shields.io/pypi/dm/tiny-web-crawler)](https://pypistats.org/packages/tiny-web-crawler)

A simple and efficient web crawler for Python.


## Features

- Crawl web pages and extract links starting from a root URL recursively
- Concurrent workers and custom delay
- Handle relative and absolute URLs
- Designed with simplicity in mind, making it easy to use and extend for various web crawling tasks

## Installation

Install using pip:

```sh
pip install tiny-web-crawler
```

## Usage

```python
from tiny_web_crawler.crawler import Spider

root_url = 'http://github.com'
max_links = 2

crawl = Spider(root_url, max_links)
crawl.start()


# Set workers and delay (default: delay is 0.5 sec and verbose is True)
# If you do not want delay, set delay=0

crawl = Spider(root_url='https://github.com', max_links=5, max_workers=5, delay=1, verbose=False)
crawl.start()

```


## Output Format

Crawled output sample for `https://github.com`

```json
{
    "http://github.com": {
        "urls": [
            "http://github.com/",
            "https://githubuniverse.com/",
            "..."
        ],
    "https://github.com/solutions/ci-cd": {
        "urls": [
            "https://github.com/solutions/ci-cd/",
            "https://githubuniverse.com/",
            "..."
        ]
      }
    }
}
```


