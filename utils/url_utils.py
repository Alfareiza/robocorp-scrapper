import datetime
import re
from urllib import parse
from datetime import datetime, timedelta



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


