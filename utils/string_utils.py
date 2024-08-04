import re


def get_extension_from_url_file(url_file: str) -> str:
    contents = url_file.rsplit('.', 1)
    return contents[-1]


def is_image_extension(ext: str) -> bool:
    image_extensions = ('jpeg', 'jpg', 'png', 'gif',
                        'webp', 'bmp', 'tiff', 'tif',
                        'svg', 'ico', 'heif', 'heic')
    return ext in image_extensions


def clean_text(text: str) -> str:
    text = text.replace('”', '"')
    text = text.replace('‘', '"')
    return ' '.join(text.strip().split())


def currency_in_text(text: str) -> bool:
    """
    >>> currency_in_text('October delivery fell $1.32 to $79.52 per')
    True
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
    pattern = r'\$?\d{1,3}(?:,\d{3})*(?:\.\d{2})?|\d+(?:\.\d+)?\s[A-Za-z]+'
    return bool(re.findall(pattern, text))
