from setuptools import setup, find_packages

setup(
    name="tiny-web-crawler",  # PyPI package name
    version="0.1.2",
    author="Indrajith Indraprastham",
    author_email="indr4jith@gmail.com",
    description="A simple and efficient web crawler in Python.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/indrajithi/tiny-web-crawler",
    packages=find_packages(
        include=["tiny_web_crawler",
                 "tiny_web_crawler.*", "crawler", "crawler.*"]
    ),
    install_requires=["validators", "beautifulsoup4",
                      "lxml", "colorama", "requests"],
    extras_require={
        "dev": ["mypy", "pytest", "responses", "pylint"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
    ],
    keywords="web crawler, scraping, web scraping, python crawler, SEO, data extraction",
    project_urls={
        "Documentation": "https://github.com/indrajithi/tiny-web-crawler#readme",
        "Source": "https://github.com/indrajithi/tiny-web-crawler",
        "Tracker": "https://github.com/indrajithi/tiny-web-crawler/issues",
    },
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "tiny-web-crawler=tiny_web_crawler.crawler:main",
        ],
    },
)
