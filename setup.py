from setuptools import setup, find_packages
from teelebot.version import (
    __author__,
    __email__,
    __blog__,
    __description__,
    __version__
)

with open('README.md', "r", encoding="utf-8") as README_md:
    README = README_md.read()

setup(
    name='teelebot',
    version=__version__,
    description=__description__,
    keywords=' '.join([
        'teelebot',
        'telegram bot',
        'telegram bot api',
        "telegram"
    ]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    url=__blog__,
    author=__author__,
    author_email=__email__,
    long_description=README,
    long_description_content_type="text/markdown",
    license='GPLv3',
    packages=find_packages(exclude=['plugins', 'plugins.*', 'test', 'test.*']),
    package_data={
        'teelebot': [
            'README.md',
            'LICENSE',
            'plugins/Chat/hello.ogg',
            'plugins/Hello/helloworld.png',
            'plugins/About/icon.png',
        ],
    },
    python_requires='>=3.6',
    install_requires=['requests[socks]'],
    entry_points={
        'console_scripts': [
            'teelebot=teelebot.main:main',
        ]
    },
    zip_safe=True
)
