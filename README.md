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
```
MIT License

Copyright (c) 2024 Indrajith Indraprastham

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

