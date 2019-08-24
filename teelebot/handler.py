# -*- coding:utf-8 -*-
import configparser, os, sys


def config():
    __version__ = "1.1.9"
    __author__ = "github:plutobell"

    config = {}

    if len(sys.argv) == 3 and sys.argv[1] in ("-c", "-C"):
        config_dir = os.path.abspath(sys.argv[2])
    elif len(sys.argv) == 1 or  len(sys.argv) == 2 and sys.argv[1] in ("check", "sdist", "bdist_wheel", "bdist_rpm"):
        if not os.path.exists(os.path.abspath(os.path.expanduser('~')) + "/.teelebot"):
            os.mkdir(os.path.abspath(os.path.expanduser('~')) + "/.teelebot")
        config_dir = os.path.abspath(os.path.expanduser('~')) + "/.teelebot/config.cfg"
        #config_dir = os.path.dirname(os.path.abspath(__file__)) + "/config.cfg"
    else:
        print("参数缺失或错误!")
        sys.exit(0)

    conf = configparser.ConfigParser()
    conf.read(config_dir)
    options = conf.options("config")
    for option in options:
        config[str(option)] = conf.get("config", option)

    if any([ "version" in config.keys(), "author" in config.keys() ]):
        print("配置文件存在错误!")
        os._exit(0)

    if "plugin_dir" in config.keys():
        plugin_dir = os.path.abspath(config["plugin_dir"]) + r'/'
    else:
        plugin_dir = os.path.dirname(os.path.abspath(__file__)) + "/plugins/"

    config["author"] = __author__
    config["version"] = __version__
    config["plugin_dir"] = plugin_dir
    config["plugin_bridge"] = __bridge(config["plugin_dir"])

    #print(config)
    return config

def __bridge(plugin_dir):
	plugin_bridge = {}
	plugin_list = []

	plugin_lis = os.listdir(plugin_dir)
	for plugi in plugin_lis:
		if os.path.isdir(plugin_dir + plugi) and plugi != "__pycache__":
			plugin_list.append(plugi)
	for plugin in plugin_list:
		with open(plugin_dir + plugin + r"/__init__.py", encoding="utf-8") as f:
			plugin_bridge[f.readline().strip()[1:]] = plugin

    #print(plugin_bridge)
	return plugin_bridge