import logging
import re
from urllib import parse

import requests

logger = logging.getLogger(__name__)


def extract_hostname_from_url(rawurl):
    if not rawurl:
        return
    protocols = ("http://", "https://")
    if not rawurl.startswith(protocols):
        rawurl = f"http://{rawurl}"

    return parse.urlparse(rawurl).hostname.replace("www.", "")


def currency_in_text(text: str) -> bool:
    """
    >>> currency_in_text('$11.1')
    True
    >>> currency_in_text('$111,111.11')
    True
    >>> currency_in_text('11 dollars')
    True
    >>> currency_in_text('11 USD')
    True
    >>> currency_in_text('')
    False
    >>> currency_in_text(' ')
    False
    """
    pattern = r'^\$[0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{1,2})?$|^\d+(?:\.\d{1,2})? (dollars|USD|EUR)$'
    return bool(re.fullmatch(pattern, text))


def download_image(url, save_path):
    """ Download an image when is not clear their type. """
    try:
        response = requests.get(url)
    except requests.exceptions.MissingSchema:
        logger.info(f'Failed to retrieve {url=}.')
    else:
        if response.status_code == 200:
            content_type = response.headers['Content-Type']

            if 'image/jpeg' in content_type:
                extension = 'jpg'
            elif 'image/png' in content_type:
                extension = 'png'
            elif 'image/webp' in content_type:
                extension = 'webp'
            else:
                logger.info('Unsupported image format:', content_type)
                return

            # Save the image with the appropriate extension
            with open(f"{save_path}.{extension}", 'wb') as file:
                file.write(response.content)
            logger.info(f"Image saved as {save_path}.{extension}")
        else:
            logger.info('Failed to retrieve image.')
