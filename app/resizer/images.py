import base64
from io import BytesIO

from PIL import Image


def image_from_bytes(image_b: bytes) -> Image.Image:
    with BytesIO(image_b) as stream:
        image = Image.open(stream).convert('RGB')

    return image


def bytes_from_image(image: Image.Image) -> bytes:
    with BytesIO() as stream:
        image.save(stream, format='jpeg')
        image_b = stream.getvalue()

    return image_b


def base64_from_bytes(image_b: bytes) -> bytes:
    image_b64 = base64.b64encode(image_b)

    return image_b64


def bytes_from_base64(image_b64: bytes) -> bytes:
    image_b = base64.b64decode(image_b64)

    return image_b
