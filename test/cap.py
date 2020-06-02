from captcha.image import ImageCaptcha
from random import randint
import string
from io import BytesIO


def captcha_img(width=320, height=120, font_sizes=(100, 110, 120, 200, 210, 220), fonts=None):

    captcha_len = 5
    captcha_range = string.digits + string.ascii_letters
    captcha_range_len = len(captcha_range)
    captcha_text = ""
    for i in range(captcha_len):
        captcha_text += captcha_range[randint(0, captcha_range_len-1)]

    img = ImageCaptcha(width=width, height=height, font_sizes=font_sizes)
    image = img.generate_image(captcha_text)

    #save to bytes
    bytes_image= BytesIO()
    image.save(bytes_image, format='png')
    bytes_image= bytes_image.getvalue()

    return bytes_image, captcha_text

if __name__ == "__main__":
    bytes_image, captcha_text = captcha_img()
    #print(bytes_image, captcha_text)