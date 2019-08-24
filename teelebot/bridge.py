# -*- coding:utf-8 -*-
import os
from .config import config

def bridge():
	plugin_bridge = {}
	plugin_list = []

	plugin_lis = os.listdir(config["plugin_dir"])
	for plugi in plugin_lis:
		if os.path.isdir(config["plugin_dir"] + plugi) and plugi != "__pycache__":
			plugin_list.append(plugi)
	for plugin in plugin_list:
		with open(config["plugin_dir"] + plugin + r"/__init__.py", encoding="utf-8") as f:
			plugin_bridge[f.readline().strip()[1:]] = plugin
	return plugin_bridge

#print(bridge())