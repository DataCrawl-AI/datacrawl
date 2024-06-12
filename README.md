# Tiny Web Crawler

A simple and efficient web crawler in Python.

## Features

- Crawl web pages and extract links
- Handle relative and absolute URLs
- Save crawl results to a JSON file
- Easy to use and extend

## Installation

Install using pip:

```sh
pip install tiny-web-crawler
```

## Usage

```python
from tiny_web_crawler.crawler import Spider

root_url = 'http://example.com'
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
            ...
        ],
    "https://github.com/solutions/ci-cd": {
        "urls": [
            "https://github.com/solutions/ci-cd/",
            "https://githubuniverse.com/",
            ...
        ]
      }
    }
}
```


## License

This project is licensed under the GNU GPLv3 License - see the LICENSE file for details.

