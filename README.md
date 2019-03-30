# Info
A Scrapy web crawler downloading content from a list of websites.
- Dynamic Content Friendly – With the help of Splash, this crawler can scrape websites running JavaScript.
- High Performance – The application uses an in-memory key-value database called Redis as a cache of content downloaded. It provides a faster downloading process than counterparts using traditional databases.

# Dependencies
- Scrapy
- Splash
- Redis

# Instructions
- Input urls into list.txt with one url in one line.
- Type::
sudo scrapy crawl standalone
