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
