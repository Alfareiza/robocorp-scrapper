from urllib import parse

import requests

from robocorp import log


def extract_hostname_from_url(rawurl):
    if not rawurl:
        return
    protocols = ("http://", "https://")
    if not rawurl.startswith(protocols):
        rawurl = f"http://{rawurl}"

    return parse.urlparse(rawurl).hostname.replace("www.", "")


def download_image(url, save_path) -> str:
    """ Download an image when is not clear their type. """
    try:
        response = requests.get(url)
    except requests.exceptions.MissingSchema as e:
        print(f'Failed to retrieve {url=}.')
        raise
    else:
        return extract_image_from_response(response, save_path)


def extract_image_from_response(response, save_path) -> str:
    """ Given a response from a recent fetch URL, extract
    the Image and return a formatted name with extension """
    if response.status_code != 200:
        raise Exception('Failed to retrieve image.')
    content_type = response.headers['Content-Type']

    if 'image/jpeg' in content_type:
        extension = 'jpg'
    elif 'image/png' in content_type:
        extension = 'png'
    elif 'image/webp' in content_type:
        extension = 'webp'
    else:
        raise Exception(f'Unsupported image format: {content_type}')

    # Save the image with the appropriate extension
    with open(f"{save_path}.{extension}", 'wb') as file:
        file.write(response.content)

    print(f"Image saved as {save_path}.{extension}")
    return f"{save_path}.{extension}"
