# -*- coding:utf-8 -*-
'''
@creation date: 2019-8-23
@last modify: 2020-11-19
'''
import configparser
import argparse
import os
import sys
import shutil
from pathlib import Path
from .version import __author__, __github__, __version__

parser = argparse.ArgumentParser(description="teelebot console command list")
parser.add_argument("-c", "--config", type=str,
                    help="specify the configuration file")
parser.add_argument("-k", "--key", type=str,
                    help="Specify the bot key")
parser.add_argument("-r", "--root", type=str,
                    help="Specify the root user id")
parser.add_argument("-p", "--plugin", type=str,
                    help="create a plugin template")
parser.add_argument(
    "-d", "--debug", help="run teelebot in debug mode", action="store_true")
parser.add_argument(
    "-v", "--version", help="view the current version of teelebot", action="store_true")
args = parser.parse_args()

if len(sys.argv) == 2 and args.version:
    print("\nVersion: " + __version__)
    print("Author: " + __author__)
    print("Project: " + __github__)
    os._exit(0)


def _config():
    '''
    获取bot配置信息及初始化
    '''
    config = {}

    if len(sys.argv) == 3 and args.config:
        config_dir = os.path.abspath(str(Path(args.config)))
    else:
        config_dir = str(Path(os.path.abspath(
                os.path.expanduser('~')) + "/.teelebot/config.cfg"))
    (path, filename) = os.path.split(config_dir)
    (filename_, extension) = os.path.splitext(filename)
    if extension != ".cfg":
        print("only support configuration files with .cfg suffix.")
        os._exit(0)
    if not os.path.exists(str(Path(path))):
        os.makedirs(str(Path(path)))
    if not os.path.exists(str(Path(config_dir))):
        print("the configuration file does not exist.")
        key = ""
        if args.key:
            key = args.key
        root = ""
        if args.root:
            root = args.root
        with open(config_dir, "w") as conf_file:
            conf_file.writelines([
                "[config]" + "\n",
                "key=" + str(key) + "\n",
                "root_id=" + str(root) + "\n",
                "plugin_dir=" + "\n",
                "pool_size=40" + "\n",
                "debug=False" + "\n",
                "drop_pending_updates=False" + "\n",
                "webhook=False" + "\n",
                "self_signed=False" + "\n",
                "cert_pub=" + "\n",
                "server_address=" + "\n",
                "server_port=" + "\n",
                "local_address=" + "\n",
                "local_port="
            ])
            print("the configuration file has been created automatically.")
        if not args.key or not args.root:
            print("please modify the relevant parameters and restart the teelebot.")
            os._exit(0)
        # else:
        #     print("\n")
    # if len(sys.argv) == 1 or args.debug or len(sys.argv) == 2 and sys.argv[1] in ("check", "sdist", "bdist_wheel", "bdist_rpm"):

    conf = configparser.ConfigParser()
    conf.read(config_dir)
    options = conf.options("config")

    if args.debug:
        conf.set("config", "debug", str(True))
    if args.key:
        conf.set("config", "key", str(args.key))
    if args.root:
        conf.set("config", "root_id", str(args.root))

    if args.debug:
        default_args = ["key", "webhook", "root_id", "debug"]
    else:
        default_args = ["key", "webhook", "root_id"]
    for default_arg in default_args:
        if default_arg not in options:
            print("the configuration file is missing necessary parameters.",
                "\nnecessary parameters:" + default_args)
            os._exit(0)

    for option in options:
        config[str(option)] = conf.get("config", option)

    none_count = 0
    for default_arg in default_args:
        if config[default_arg] == "" or\
            config[default_arg] == None:
            none_count += 1
            print("field " + default_arg + " is not set in configuration file.")
    if none_count != 0:
        os._exit(0)

    if any(["version" in config.keys(), "author" in config.keys()]):
        print("error in configuration file.")
        os._exit(0)

    if config["webhook"] == "True":
        webhook_args = ["self_signed",
                        "server_address", "server_port",
                        "local_address", "local_port"]
        if "self_signed" not in config.keys():
            print("the self_signed field must exist in webhook mode.")
            os._exit(0)
        else:
            if "cert_pub" not in config.keys():
                print("the field cert_pub must exist when self_signed is true.")
                os._exit(0)
            else:
                webhook_args.append("cert_pub")
        for w in webhook_args:
            if w not in config.keys():
                print("please check if the following fields exist in the configuration file: \n" +
                    "cert_pub self_signed server_address server_port local_address local_port")
                os._exit(0)

    plugin_dir_in_config = False
    if "plugin_dir" in config.keys():
        if config["plugin_dir"] == "" or config["plugin_dir"] == None:
            plugin_dir = str(Path(os.path.dirname(os.path.abspath(__file__)) + r"/plugins/")) + os.sep
        else:
            plugin_dir = str(Path(os.path.abspath(config["plugin_dir"]))) + os.sep
            plugin_dir_in_config = True
    else:
        plugin_dir = str(Path(os.path.dirname(os.path.abspath(__file__)) + r"/plugins/")) + os.sep

    if os.path.exists(str(Path(os.path.dirname(
        os.path.abspath(__file__)) + r"/__pycache__"))):
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
                        "\n" + \
                        "    # root_id = bot.root_id\n" + \
                        "    # bot_id = bot.bot_id\n" + \
                        "    # author = bot.author\n" + \
                        "    # version = bot.version\n" + \
                        "    # plugin_dir = bot.plugin_dir\n" + \
                        "    # plugin_bridge = bot.plugin_bridge\n" + \
                        "    # uptime = bot.uptime\n" + \
                        "    # response_times = bot.response_times\n" + \
                        "    # response_chats = bot.response_chats\n" + \
                        "    # response_users = bot.response_users\n" + \
                        "\n" + \
                        '    chat_id = message["chat"]["id"]\n' + \
                        '    user_id = message["from"]["id"]\n' + \
                        '    message_id = message["message_id"]\n' + \
                        "\n" + \
                        '    message_type = message["message_type"]\n' + \
                        '    chat_type = message["chat"]["type"]\n' + \
                        "\n" + \
                        '    prefix = "/' + plugin_name.lower() + '"\n' + \
                        "\n\n" + \
                        "    # Write your plugin code below"
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
            if not os.path.exists(str(Path(plugin_dir + plugin_name + os.sep + "requirement.txt"))):
                with open(str(Path(plugin_dir + plugin_name + os.sep + "requirement.txt")), "w") as requirement:
                    pass

            print("plugin " + plugin_name + " was created successfully.")
        else:
            print("plugin " + plugin_name + " already exists.")
        os._exit(0)
    elif args.plugin and not plugin_dir_in_config:
        print("the plugin_dir is not set in the configuration file.")
        os._exit(0)

    if "pool_size" in config.keys():
        if int(config["pool_size"]) < 1 or int(config["pool_size"]) > 100:
            print("thread pool size is out of range (1-100).")
            os._exit(0)
    else:
        config["pool_size"] = "40"

    if "local_api_server" in config.keys():
        local_api_server = config["local_api_server"]
        if local_api_server == None or local_api_server == "" or len(local_api_server) < 7:
            config["local_api_server"] = "False"
        else:
            if "https://" in local_api_server:
                print("local api server address not support https.")
                os._exit(0)
            if "http://" not in local_api_server:
                print("local api server address incorrect.")
                os._exit(0)
            if local_api_server[len(local_api_server)-1] != "/":
                local_api_server += "/"
            config["local_api_server"] = local_api_server
    else:
        config["local_api_server"] = "False"

    if "self_signed" in config.keys():
        if config["self_signed"] == "True":
            config["self_signed"] = True
        elif config["self_signed"] == "False":
            config["self_signed"] = False
        else:
            print("The self_signed field value in the configuration file is wrong.")
            os._exit(0)
    else:
        config["self_signed"] = False

    if "drop_pending_updates" in config.keys():
        if config["drop_pending_updates"] == "True":
            config["drop_pending_updates"] = True
        elif config["drop_pending_updates"] == "False":
            config["drop_pending_updates"] = False
        else:
            print("The drop_pending_updates field value in the configuration file is wrong.")
            os._exit(0)
    else:
        config["drop_pending_updates"] = False

    if config["debug"] == "True":
        config["debug"] = True
    elif config["debug"] == "False":
        config["debug"] = False
    else:
        print("The debug field value in the configuration file is wrong.")
        os._exit(0)

    if config["webhook"] == "True":
        config["webhook"] = True
    elif config["webhook"] == "False":
        config["webhook"] = False
    else:
        print("The webhook field value in the configuration file is wrong.")
        os._exit(0)

    config["author"] = __author__
    config["version"] = __version__
    config["plugin_dir"] = plugin_dir
    config["plugin_bridge"] = _bridge(config["plugin_dir"])
    config["plugin_info"] = _plugin_info(
        config["plugin_bridge"].keys(), config["plugin_dir"])

    if args.debug:
        config["debug"] = True

    # print(config)
    return config

def _bridge(plugin_dir):
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
                plugin_bridge[plugin] = row_one

    # print(plugin_bridge)
    return plugin_bridge

def _plugin_info(plugin_list, plugin_dir):
    '''
    获取插件修改状态
    '''
    plugin_info = {}
    for plugin in plugin_list:
        mtime = os.stat(str(Path(plugin_dir + plugin + "/" + plugin + ".py"))).st_mtime
        plugin_info[plugin] = mtime

    return plugin_info
