# -*- coding:utf-8 -*-
import configparser

config = {}

conf = configparser.ConfigParser()
conf.read("config.cfg")
options = conf.options("config")

for option in options:
	config[str(option)] = conf.get("config", option)


config["version"] = '1.1.2'

#print(config)