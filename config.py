# -*- coding:utf-8 -*-
import configparser, sys

__version__ = "1.1.2"
__author__ = "github:plutobell"

config = {}

conf = configparser.ConfigParser()
conf.read("config.cfg")
options = conf.options("config")

for option in options:
	config[str(option)] = conf.get("config", option)

if any([ "version" in config.keys(), "author" in config.keys() ]):
    print("配置文件存在错误!")
    sys.exit(0)

config["author"] = __author__
config["version"] = __version__

#print(config)