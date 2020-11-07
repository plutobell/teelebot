# -*- coding:utf-8 -*-
'''
@creation date: 2019-8-23
@last modify: 2020-11-8
'''
import configparser
import argparse
import os
import sys
import shutil
from pathlib import Path

__version__ = "1.9.20_dev"
__author__ = "github:plutobell"

parser = argparse.ArgumentParser(description="teelebot console command list")
parser.add_argument("-c", "--config", type=str,
                    help="specify the configuration file path")
parser.add_argument("-p", "--plugin", type=str,
                    help="create a plugin template")
parser.add_argument(
    "-d", "--debug", help="run teelebot in debug mode", action="store_true")
parser.add_argument(
    "-v", "--version", help="view the current version of teelebot", action="store_true")
args = parser.parse_args()

if len(sys.argv) == 2 and args.version:
    os.system("")
    print("version: \033[1;36;40m" + __version__ + "\033[0m")
    print("author: \033[1;36;40m" + __author__ + "\033[0m")
    print("")
    os._exit(0)


def config():
    '''
    获取bot配置信息
    '''
    config = {}

    if len(sys.argv) == 3 and args.config:
        config_dir = os.path.abspath(str(Path(args.config)))
    else:
        if not os.path.exists(str(Path(os.path.abspath(os.path.expanduser('~')) + "/.teelebot"))):
            os.mkdir(str(Path(os.path.abspath(os.path.expanduser('~')) + "/.teelebot")))
        if not os.path.exists(str(Path(os.path.abspath(
            os.path.expanduser('~')) + "/.teelebot/config.cfg"))):
            print("配置文件不存在!")
            os._exit(0)
        else:
            config_dir = str(Path(os.path.abspath(
                os.path.expanduser('~')) + "/.teelebot/config.cfg"))

    # if len(sys.argv) == 1 or args.debug or len(sys.argv) == 2 and sys.argv[1] in ("check", "sdist", "bdist_wheel", "bdist_rpm"):

    conf = configparser.ConfigParser()
    conf.read(config_dir)
    options = conf.options("config")

    if args.debug:
        default_args = ["key", "webhook", "root", "timeout", "debug"]
    else:
        default_args = ["key", "webhook", "root", "timeout"]
    for default_arg in default_args:
        if default_arg not in options:
            print("配置文件缺失必要的参数!")
            return False

    for option in options:
        config[str(option)] = conf.get("config", option)

    if any(["version" in config.keys(), "author" in config.keys()]):
        print("配置文件存在错误!")
        os._exit(0)

    if config["webhook"] == "True":
        webhook_args = ["cert_pub", "server_address",
                        "server_port", "local_address", "local_port"]
        for w in webhook_args:
            if w not in config.keys():
                print("请检查配置文件中是否存在以下字段：\n" +
                    "cert_pub server_address server_port local_address local_port")
                return False

    plugin_dir_in_config = False

    if "plugin_dir" in config.keys():
        plugin_dir = str(Path(os.path.abspath(config["plugin_dir"]))) + os.sep
        plugin_dir_in_config = True
    else:
        plugin_dir = str(Path(os.path.dirname(os.path.abspath(__file__)) + r"/plugins/")) + os.sep

    if os.path.exists(str(Path(os.path.dirname(os.path.abspath(__file__)) + r"/__pycache__"))):
        shutil.rmtree(str(Path(os.path.dirname(
            os.path.abspath(__file__)) + r"/__pycache__")))

    if not os.path.isdir(plugin_dir):  # 插件目录检测
        # os.makedirs(plugin_dir)
        os.mkdir(plugin_dir)
        with open(str(Path(plugin_dir + "__init__.py")), "w") as f:
            pass
    elif not os.path.exists(str(Path(plugin_dir + "__init__.py"))):
        with open(str(Path(plugin_dir + "__init__.py")), "w") as f:
            pass

    if args.plugin and plugin_dir_in_config: #插件模板创建
        plugin_name = args.plugin
        if not os.path.exists(str(Path(plugin_dir + plugin_name))):
            os.mkdir(str(Path(plugin_dir + plugin_name)))
            if not os.path.exists(str(Path(plugin_dir + plugin_name + os.sep + plugin_name + ".py"))):
                with open(str(Path(plugin_dir + plugin_name + os.sep + plugin_name + ".py")), "w") as enter:
                    enter.writelines([
                        "# -*- coding:utf-8 -*-\n",
                        "\n",
                        "def " + plugin_name + "(bot, message):\n",
                        "    pass\n"
                    ])
            if not os.path.exists(str(Path(plugin_dir + plugin_name + os.sep + "__init__.py"))):
                with open(str(Path(plugin_dir + plugin_name + os.sep + "__init__.py")), "w") as init:
                    init.writelines([
                        "#/" + plugin_name.lower() + "\n",
                        "#" + plugin_name + " Plugin\n"
                    ])
            if not os.path.exists(str(Path(plugin_dir + plugin_name + os.sep + "readme.md"))):
                with open(str(Path(plugin_dir + plugin_name + os.sep + "readme.md")), "w") as readme:
                    readme.writelines([
                        "# " + plugin_name + " #\n"
                    ])

            print("plugin " + plugin_name + " was created successfully.")
        else:
            print("plugin " + plugin_name + " already exists.")
        os._exit(0)
    elif args.plugin and not plugin_dir_in_config:
        print("the plugin path is not set in the configuration file.")
        os._exit(0)

    if "pool_size" in config.keys():
        if int(config["pool_size"]) < 1 or int(config["pool_size"]) > 100:
            print("线程池尺寸超出范围!(1-100)")
            return False
    else:
        config["pool_size"] = "40"

    if config["debug"] == "True":
        config["debug"] = True
    elif config["debug"] == "False":
        config["debug"] = False

    if config["webhook"] == "True":
        config["webhook"] = True
    elif config["webhook"] == "False":
        config["webhook"] = False

    config["author"] = __author__
    config["version"] = __version__
    config["plugin_dir"] = plugin_dir
    config["plugin_bridge"] = bridge(config["plugin_dir"])
    config["plugin_info"] = plugin_info(
        config["plugin_bridge"].values(), config["plugin_dir"])

    if args.debug:
        config["debug"] = True

    # print(config)
    return config


def bridge(plugin_dir):
    '''
    获取插件和指令的映射
    '''
    plugin_bridge = {}
    plugin_list = []

    plugin_lis = os.listdir(plugin_dir)
    for plugi in plugin_lis:
        if os.path.isdir(str(Path(plugin_dir + plugi))) and plugi != "__pycache__" and plugi[0] != '.':
            plugin_list.append(plugi)
    for plugin in plugin_list:
        with open(str(Path(plugin_dir + plugin + r"/__init__.py")), encoding="utf-8") as f:
            row_one = f.readline().strip()[1:]
            if row_one != "~~":  # Hidden plugin
                plugin_bridge[row_one] = plugin

    # print(plugin_bridge)
    return plugin_bridge


def plugin_info(plugin_list, plugin_dir):
    '''
    获取插件修改状态
    '''
    plugin_info = {}
    for plugin in plugin_list:
        mtime = os.stat(str(Path(plugin_dir + plugin + "/" + plugin + ".py"))).st_mtime
        plugin_info[plugin] = mtime

    return plugin_info
