# Tiny Web Crawler

A simple and efficient web crawler in Python.

[![CI](https://github.com/indrajithi/tiny-web-crawler/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/indrajithi/tiny-web-crawler/actions/workflows/ci.yml)

## Features

- Crawl web pages and extract links starting from a root URL and extract all the links found on each page
- Handle relative and absolute URLs
- Save the results of your crawl in a structured JSON format for easy analysis and processing
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

spider = Spider(root_url, max_links)
spider.start()
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


## License

This project is licensed under the GNU GPLv3 License - see the LICENSE file for details.

