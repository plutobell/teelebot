from setuptools import setup, find_packages, Extension
from distutils.core import setup, Extension
from teelebot.handler import config

config = config()

# read the contents of the README
with open('README.md', "r", encoding="utf-8") as README_md:
    README = README_md.read()

setup(
    name='teelebot',
    version=config["version"],
    description='基于Telegram Bot API的机器人框架,拥有插件系统，扩展方便。',
    keywords=' '.join([
        'teelebot',
        'telegram bot',
        'telegram api'
    ]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    url='https://github.com/plutobell/teelebot',
    author='Pluto',
    author_email='hi@ojoll.com',
    long_description=README,
    long_description_content_type="text/markdown",
    license='GPLv3',
    packages=find_packages(exclude=['plugins', 'plugins.*']),
    package_data={
        'teelebot':['README.md'],
        'teelebot':['LICENSE'],
		'teelebot':['plugins/Hello/helloworld.png'],
		'teelebot':['plugin/Chat/hello.ogg']
    },
    install_requires=['requests'],
    entry_points={
        'console_scripts': [
            'teelebot=teelebot:main',
        ]
    },
    zip_safe=False
)