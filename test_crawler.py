import asyncio
import json

from datacrawl.core.crawl_settings import CrawlSettings
from datacrawl.core.crawler import Datacrawl


async def main() -> None:
    settings = CrawlSettings(
        root_url="http://indrajith.me",
        max_links=4,
        max_workers=5,
        delay=1,
        verbose=True,
        include_body=True,
        respect_robots_txt=True,
        save_to_file="crawl_results.json",
    )

    crawler = Datacrawl(settings)
    results = await crawler.start()
    print(json.dumps(results, indent=4))


if __name__ == "__main__":
    asyncio.run(main())
