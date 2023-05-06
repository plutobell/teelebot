# -*- coding:utf-8 -*-
'''
@creation date: 2019-08-23
@last modification: 2023-05-06
'''
import configparser
import argparse
import os
import sys
import shutil
import requests

from pathlib import Path
from .version import __author__, __github__, __version__

cloud_api_server = "https://api.telegram.org/"
common_pkg_prefix = "~~"
inline_mode_prefix = "?:"

parser = argparse.ArgumentParser(description="teelebot console command list")
parser.add_argument("-c", "--config", type=str,
                    help="specify the configuration file")
parser.add_argument("-k", "--key", type=str,
                    help="specify the bot key")
parser.add_argument("-r", "--root", type=str,
                    help="specify the root user id")
parser.add_argument("-p", "--plugin", type=str,
                    help="specify the plugin path")
parser.add_argument("-mp", "--make_plugin", type=str,
                    help="create a plugin template")
parser.add_argument("-L", "--logout",
                    help="use it to log out from the cloud Bot API server before launching the bot locally.",
                    action="store_true")
parser.add_argument("-C", "--close",
                    help="use it to close the bot instance before moving it from one local server to another.",
                    action="store_true")
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

    if args.config:
        config_dir = os.path.abspath(str(Path(args.config)))
    else:
        config_dir = str(Path(os.path.abspath(
                os.path.expanduser('~')) + "/.teelebot/config.cfg"))
    (path, filename) = os.path.split(config_dir)
    (filename_, extension) = os.path.splitext(filename)
    if extension != ".cfg":
        print("Only support configuration files with .cfg suffix.")
        os._exit(0)
    if not os.path.exists(str(Path(path))):
        os.makedirs(str(Path(path)))
    if not os.path.exists(str(Path(config_dir))):
        print("The configuration file does not exist.")
        plugin_dir = ""
        if args.plugin:
            plugin_dir = args.plugin
        key = ""
        if args.key:
            key = args.key
        root = ""
        if args.root:
            root = args.root
        debug = "False"
        if args.debug:
            debug = "True"
        with open(config_dir, "w", encoding="utf-8") as conf_file:
            conf_file.writelines([
                "[config]" + "\n",
                "key = " + str(key) + "\n",
                "root_id = " + str(root) + "\n",
                "plugin_dir = " + str(plugin_dir) + "\n",
                "pool_size = 40" + "\n",
                "buffer_size = 16" + "\n",
                "debug = " + str(debug) + "\n",
                "local_api_server = False" + "\n",
                "drop_pending_updates = False" + "\n",
                "updates_chat_member = False" + "\n",
                "webhook = False" + "\n",
                "self_signed = False" + "\n",
                "cert_key = " + "\n",
                "cert_pub = " + "\n",
                "server_address = " + "\n",
                "server_port = " + "\n",
                "local_address = " + "\n",
                "local_port = " + "\n",
                "proxy = "
            ])
            print("The configuration file has been created automatically.")
            print("Configuration file path: " + str(config_dir))
        if not args.key or not args.root:
            print("Please modify the relevant parameters and restart the teelebot.")
            os._exit(0)
        # else:
        #     print("\n")

    conf = configparser.ConfigParser()
    conf.read(config_dir)
    options = conf.options("config")

    if args.debug:
        conf.set("config", "debug", str(True))
    if args.plugin:
        conf.set("config", "plugin_dir", str(args.plugin))
    if args.key:
        conf.set("config", "key", str(args.key))
    if args.root:
        conf.set("config", "root_id", str(args.root))

    with open(config_dir, 'w', encoding="utf-8") as configfile:
        conf.write(configfile)

    if args.debug:
        default_args = ["plugin_dir", "key", "webhook", "root_id", "debug"]
    else:
        default_args = ["plugin_dir", "key", "webhook", "root_id"]
    for default_arg in default_args:
        if default_arg not in options:
            print("The configuration file is missing necessary parameters.",
                "\nnecessary parameters:", default_args)
            os._exit(0)

    for option in options:
        config[str(option)] = conf.get("config", option)

    none_count = 0
    for default_arg in default_args:
        if config[default_arg] == "" or\
            config[default_arg] == None:
            none_count += 1
            print("Field " + default_arg + " is not set in configuration file.")
    if none_count != 0:
        os._exit(0)

    if any(["version" in config.keys(), "author" in config.keys()]):
        print("Error in configuration file.")
        os._exit(0)

    if config["webhook"] == "True":
        webhook_args = ["self_signed",
                        "server_address", "server_port",
                        "local_address", "local_port",
                        "cert_pub", "cert_key"]
        for w in webhook_args:
            if w not in config.keys():
                print("Please check if the following fields exist in the configuration file: \n" +
                    "cert_pub cert_key self_signed server_address server_port local_address local_port")
                os._exit(0)

    plugin_dir_in_config = False
    if "plugin_dir" in config.keys():
        if config["plugin_dir"] == "" or config["plugin_dir"] == None:
            print("Field plugin_dir is not set in configuration file.")
            os._exit(0)
        else:
            plugin_dir = str(Path(os.path.abspath(config["plugin_dir"]))) + os.sep
            plugin_dir_in_config = True
    else:
        print("Field plugin_dir does not exist in configuration file.")
        os._exit(0)

    if os.path.exists(str(Path(os.path.dirname(
        os.path.abspath(__file__)) + r"/__pycache__"))):
        shutil.rmtree(str(Path(os.path.dirname(
            os.path.abspath(__file__)) + r"/__pycache__")))

    if not os.path.isdir(plugin_dir):  # 插件目录检测
        os.makedirs(plugin_dir)
        # os.mkdir(plugin_dir)
        with open(str(Path(plugin_dir + "__init__.py")), "w", encoding="utf-8") as f:
            pass
    elif not os.path.exists(str(Path(plugin_dir + "__init__.py"))):
        with open(str(Path(plugin_dir + "__init__.py")), "w", encoding="utf-8") as f:
            pass

    if args.make_plugin and plugin_dir_in_config: #插件模板创建
        plugin_name = args.make_plugin
        if not os.path.exists(str(Path(plugin_dir + plugin_name))):
            os.mkdir(str(Path(plugin_dir + plugin_name)))
            if not os.path.exists(str(Path(plugin_dir + plugin_name + os.sep + "__init__.py"))):
                with open(str(Path(plugin_dir + plugin_name + os.sep + "__init__.py")), "w", encoding="utf-8") as init:
                    init.writelines([
                        "#/" + plugin_name.lower() + "\n",
                        "#" + plugin_name + " Plugin\n"
                    ])
            if not os.path.exists(str(Path(plugin_dir + plugin_name + os.sep + plugin_name + ".py"))):
                with open(str(Path(plugin_dir + plugin_name + os.sep + plugin_name + ".py")), "w", encoding="utf-8") as enter:
                    enter.writelines([
                        "# -*- coding: utf-8 -*-\n",
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
                        "    # proxies = bot.proxies\n" + \
                        "\n" + \
                        '    chat_id = message["chat"]["id"]\n' + \
                        '    user_id = message["from"]["id"]\n' + \
                        '    message_id = message["message_id"]\n' + \
                        "\n" + \
                        '    message_type = message["message_type"]\n' + \
                        '    chat_type = message["chat"]["type"]\n' + \
                        "\n" + \
                        '    prefix = ""\n' + \
                        '    with open(bot.path_converter(bot.plugin_dir + "' + plugin_name + '/__init__.py"), "r", encoding="utf-8") as init:\n' + \
                        '        prefix = init.readline()[1:].strip()\n' + \
                        "\n\n" + \
                        "    # Write your plugin code below"
                    ])
            if not os.path.exists(str(Path(plugin_dir + plugin_name + os.sep + "README.md"))):
                with open(str(Path(plugin_dir + plugin_name + os.sep + "README.md")), "w", encoding='utf-8') as readme:
                    readme.writelines([
                        "# " + plugin_name + " #\n"
                    ])
            if not os.path.exists(str(Path(plugin_dir + plugin_name + os.sep + "METADATA"))):
                with open(str(Path(plugin_dir + plugin_name + os.sep + "METADATA")), "w", encoding='utf-8') as metadata:
                    metadata.writelines([
                        "Metadata-version: 1.0\n",
                        "Plugin-name: " + plugin_name + "\n",
                        "Version: 0.1.0\n",
                        "Summary: \n",
                        "Home-page: \n",
                        "Author: \n",
                        "Author-email: \n",
                        "License: \n",
                        "Keywords: \n",
                        "Requires-teelebot: >=" + __version__ + "\n",
                        "Requires-dist: \n",
                        "Source: "
                    ])

            print("Plugin " + plugin_name + " was created successfully.")
        else:
            print("Plugin " + plugin_name + " already exists.")
        os._exit(0)
    elif args.make_plugin and not plugin_dir_in_config:
        print("The plugin_dir is not set in the configuration file.")
        os._exit(0)

    if "pool_size" in config.keys():
        if int(config["pool_size"]) < 1 or int(config["pool_size"]) > 100:
            print("Thread pool size is out of range (1-100).")
            os._exit(0)
    else:
        config["pool_size"] = "40"

    if "buffer_size" in config.keys():
        if int(config["buffer_size"]) <= 0:
            print("Data buffer_size is out of range (> 0 MiB).")
            os._exit(0)
    else:
        config["buffer_size"] = "16"

    if "local_api_server" in config.keys():
        local_api_server = config["local_api_server"]
        if (local_api_server == None or
            local_api_server == "" or
            local_api_server == "False" or
            len(local_api_server) < 7):
            config["local_api_server"] = "False"
        else:
            if "https://" in local_api_server:
                print("Local api server address not support https.")
                os._exit(0)
            if "http://" not in local_api_server:
                print("Local api server address incorrect.")
                os._exit(0)
            if "telegram.org" in local_api_server:
                print("Local api server address incorrect.")
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

    if "updates_chat_member" in config.keys():
        if config["updates_chat_member"] == "True":
            config["updates_chat_member"] = True
        elif config["updates_chat_member"] == "False":
            config["updates_chat_member"] = False
        else:
            print("The updates_chat_member field value in the configuration file is wrong.")
            os._exit(0)
    else:
        config["updates_chat_member"] = False

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

    if "proxy" in config.keys():
        if str(config["proxy"]).strip() == "" or str(config["proxy"]).strip() == None:
            config["proxies"] = {"all": None}
        else:
            config["proxies"] = {"all": str(config["proxy"]).strip()}
        config.pop("proxy")
    else:
        config["proxies"] = {"all": None}

    config["author"] = __author__
    config["version"] = __version__
    config["plugin_dir"] = plugin_dir
    config["plugin_bridge"], config["non_plugin_list"] = _bridge(config["plugin_dir"])
    config["plugin_info"] = _plugin_info(
        config["plugin_bridge"].keys(), config["plugin_dir"])
    config["non_plugin_info"] = _plugin_info(
        config["non_plugin_list"], config["plugin_dir"])
    config["cloud_api_server"] = cloud_api_server
    config["common_pkg_prefix"] = common_pkg_prefix
    config["inline_mode_prefix"] = inline_mode_prefix

    # print(config)
    return config

def _bridge(plugin_dir):
    '''
    获取插件和指令的映射
    '''
    plugin_bridge = {}
    non_plugin_list = []
    plugin_list = []
    corrupted_plugin_list = []

    plugin_lis = os.listdir(plugin_dir)
    for plugi in plugin_lis:
        if os.path.isdir(str(Path(plugin_dir + plugi))) and plugi != "__pycache__" and plugi[0] != '.':
            package_file_list = os.listdir(str(Path(plugin_dir + plugi)))
            if plugi + ".py" in package_file_list and \
                "__init__.py" in package_file_list and \
                "METADATA" in package_file_list:
                plugin_list.append(plugi)
            else:
                os.system("")
                print("\033[1;31mThe " + plugi + " plugin is corrupted." + "\033[0m")
                corrupted_plugin_list.append(plugi)

    for plugin in plugin_list:
        with open(str(Path(plugin_dir + plugin + r"/__init__.py")), encoding="utf-8") as f:
            row_one = f.readline().strip()[1:]
            if row_one != common_pkg_prefix:  # Hidden plugin
                plugin_bridge[plugin] = row_one
            else:
                if plugin in corrupted_plugin_list:
                    if (plugin_dir + plugin) in sys.path:
                        sys.modules.pop(plugin_dir + plugin)
                        sys.path.remove(plugin_dir + plugin)
                else:
                    non_plugin_list.append(plugin)
                    if (plugin_dir + plugin) not in sys.path:
                        sys.path.append(plugin_dir + plugin)

    # print(sys.path)
    # print(plugin_bridge, non_plugin_list)
    return plugin_bridge, non_plugin_list

def _plugin_info(plugin_list, plugin_dir):
    '''
    获取插件修改状态
    '''
    plugin_info = {}
    for plugin in plugin_list:
        mtime = os.stat(str(Path(plugin_dir + plugin + "/" + plugin + ".py"))).st_mtime
        plugin_info[plugin] = mtime

    return plugin_info


if args.close and args.logout:
    print("Only one of logout and close can be used at the same time.")
    os._exit(0)

elif args.logout and not args.close:
    config = _config()
    logout_url = f'{cloud_api_server}bot{config["key"]}/logOut'
    try:
        req = requests.post(url=logout_url, verify=False)
    except:
        print("Error request the cloud Bot API server.")
        os._exit(0)
    if req.json().get("ok"):
        print("Successfully logout from the cloud Bot API server.")
    elif not req.json().get("ok"):
        print("Error logout from the cloud Bot API server.")
        if (req.json().get("error_code") == 401 and
            req.json().get("description") == "Unauthorized"):
            print("If you already logout the bot from the cloud Bot API server,please wait at least 10 minutes and try again.")
    os._exit(0)

elif args.close and not args.logout:
    config = _config()
    if config["local_api_server"] == "False":
        print("The close can only be used when local_api_server is configured.")
        os._exit(0)

    close_url = f'{config["local_api_server"]}bot{config["key"]}/close'
    try:
        req = requests.post(url=close_url, verify=False)
    except:
        print("Error request the the local API server.")
        os._exit(0)
    if req.json().get("ok"):
        print("Successfully close from the local API server.")
    elif not req.json().get("ok"):
        print("Error close from the local API server.")
        if req.json().get("error_code") == 429:
            print("Too many requests, please retry after " + str(req.json().get("parameters")["retry_after"]) + " seconds.")
    os._exit(0)


