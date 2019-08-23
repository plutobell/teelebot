# -*- coding:utf-8 -*-
import configparser, os

__version__ = "1.1.3"
__author__ = "github:plutobell"
plugin_dir = os.path.dirname(os.path.abspath(__file__)) + "/plugins/"

config = {}

conf = configparser.ConfigParser()
config_dir = os.path.dirname(os.path.abspath(__file__)) + "/config.cfg"
conf.read(config_dir)
options = conf.options("config")
for option in options:
	config[str(option)] = conf.get("config", option)

if any([ "version" in config.keys(), "author" in config.keys() ]):
    print("配置文件存在错误!")
    os._exit(0)

config["author"] = __author__
config["version"] = __version__
config["plugin_dir"] = plugin_dir

#print(config)