import datetime
import logging
import re
import uuid
import textwrap

from typing import Iterable, NoReturn

from robocorp import browser
from RPA.HTTP import HTTP

from utils.date_utils import is_datetime_in_interval, parse_string_date
from utils.string_utils import get_extension_from_url_file, clean_text, is_image_extension
from utils.url_utils import extract_hostname_from_url, currency_in_text, download_image

http = HTTP()
logger = logging.getLogger(__name__)
DOWNLOADED_IMAGES_PATH = "output/"


class Item:
    """
    Parse information related to a single news.
    """

    def __init__(self, title, link, description, image, publish_date):
        self.title = title
        self.link = link
        self.description = description
        self.image_url = image
        self.publish_date = publish_date
        self.currency_in_title_or_desc = self.is_currency_in_title_or_desc()
        self.uuid = str(uuid.uuid4())
        self.image_name = ''

    def __repr__(self):
        return f'{textwrap.shorten(self.title, width=50, placeholder="...")} {self.publish_date:%D}'

    def is_currency_in_title_or_desc(self) -> bool:
        return currency_in_text(self.title) or currency_in_text(self.description)

    def download_image(self):
        """ Download image of the new in output/"""
        logger.info(f'Downloading image from News # {self.uuid}...')
        ext = get_extension_from_url_file(self.image_url)

        if not is_image_extension(ext):
            download_image(self.image_url, f"{DOWNLOADED_IMAGES_PATH}/{self.uuid})")

        image_name = f"{DOWNLOADED_IMAGES_PATH}/{self.uuid}.{ext}"
        try:
            http.download(
                url=self.image_url,
                target_file=image_name,
                overwrite=True,
            )
            logger.info(f'Image saved as {image_name}')
            self.image_name = image_name
        except OSError as e:
            logger.info(f'It was not possible download image for News # {self.uuid}: {str(e)}')


class News:
    """
    Parse information about different news platforms.
    """

    def __init__(self, url):
        self.base_url: str = url
        self.news: list = []
        self.last_scrapped: 'datetime' = None
        self.page = None

    def __str__(self):
        return f"{self.domain} - {len(self.news)} News captured."

    @property
    def domain(self):
        return extract_hostname_from_url(self.base_url)

    def close_modal(self):
        try:
            self.page.click('a[title="Close"].fancybox-item.fancybox-close')
        except Exception as e:
            ...

    def next_page(self, current_url):
        """ Given the current url, create a new one increasing the value equivalent to the page """
        pattern = r'(p=)(\d+)'
        new_url = re.sub(pattern, lambda m: f'{m.group(1)}{int(m.group(2)) + 1}', current_url)
        try:
            logger.info(f'From {current_url=} to {new_url=}')
            self.page.goto(new_url, timeout=30000)
            self.page.wait_for_load_state()
        except Exception as e:
            logger.info(e)

    def is_page_available(self):
        """ If page has results, so it means is able to be scrapped."""
        try:
            logger.info('Checking if there are results in current page')
            main = self.page.locator('main.SearchResultsModule-main')
            results = main.locator('div.SearchResultsModule-results')
            results.locator('div.PageList-items-item')
        except Exception:
            logger.info('There is no results in in current page')
            return False
        else:
            logger.info('There are results in current page')
            return True

    def _build_url_search(self, category, query) -> str:
        """ Define query params based on newspaper platform """
        url_search = ''
        match self.domain:
            case 'apnews.com':
                category_query = {
                    'newest': '&s=3',
                    'relevance': '&s=0',
                    'oldest': '&s=2',
                }
                url_search = f"{self.base_url}/search?q={query}{category_query.get(category, 'relevance')}&p=1"
            case _:
                ...

        return url_search

    def initial_search(self, category, query):
        """ Fetch url to extract data. """
        attempts = 3
        url = self._build_url_search(category, query)
        for _ in range(attempts):
            try:
                self.page = browser.page()
                logger.info(f'Fetching url {url}')
                self.page.goto(url)
                self.page.wait_for_load_state()
            except Exception as e:
                logger.info(f'Error fetching url {url!r}: {str(e)}')
            else:
                return url

    def scrap(self, category, query, limit_pages, interval_limit):
        """ Main function that initiate the process of scraping news"""
        self.initial_search(category, query)
        self.extract_news(interval_limit, limit_pages)

    def extract_news(self, interval_limit, limit_pages=100_000_000):
        """ Load in self.news attribute all the extracted news where
        every item of the list is an Item object. """
        pages = 0
        while self.is_page_available() and pages <= limit_pages:
            main = self.page.locator('main.SearchResultsModule-main')
            results = main.locator('div.SearchResultsModule-results')
            news = results.locator('div.PageList-items-item')
            qty_news = news.count()
            self.extract_news_from_page(news, qty_news, interval_limit)
            self.next_page(self.page.url)
            pages += 1

    def extract_news_from_page(self, news, qty_news, interval_limit):
        """ Extract the news of a single page """
        browser.context().set_default_timeout(100)
        for i in range(qty_news):
            try:
                # If any mandatory element is not located, then I ignore that news.
                item = news.nth(i)
                title_div = item.locator('div.PagePromo-title')
                link = self.get_link_news(title_div, True)
                title = self.get_text(title_div, 'span.PagePromoContentIcons-text', False)
                description = self.get_text(item, 'div.PagePromo-description', True)
                date_of_news = self.get_text(item, 'div.PagePromo-date', True)
                link_images = self.get_image_url(item, False)
                item = Item(
                    clean_text(title),
                    link,
                    clean_text(description),
                    link_images[0] if link_images else '',
                    parse_string_date(date_of_news)
                )
                logger.info(f"News scrapped: {item}")
            except Exception as e:
                logger.info(f'Error locating element: {str(e)}')
            else:
                if is_datetime_in_interval(item.publish_date, *interval_limit):
                    self.news.append(item)
                    item.download_image()

    def get_text(self, item, instructions, mandatory=False):
        try:
            return item.locator(instructions).inner_text()
        except Exception as e:
            if mandatory:
                raise ... from e

    def get_link_news(self, item, mandatory=False):
        try:
            return item.locator('a.Link').get_attribute('href')
        except Exception as e:
            if mandatory:
                raise ... from e

    def get_image_url(self, item, mandatory=False):
        try:
            return item.locator('div.PagePromo-media picture').locator(
                'source').first.get_attribute('srcset').split(' ')
        except Exception as e:
            if mandatory:
                raise ... from e
