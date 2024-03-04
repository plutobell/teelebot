# -*- coding:utf-8 -*-
'''
@creation date: 2019-08-23
@last modification: 2024-02-28
'''
import configparser
import argparse
import re
import os
import sys
import copy
import shutil
import traceback
import requests

from pathlib import Path
from .metadata import _Metadata
from .logger import _logger
from .version import __author__, __github__, __version__
from .common import (
    __metadata_templates__,
    __metadata_version_in_use__,
    __cloud_api_server__,
    __common_pkg_prefix__,
    __inline_mode_prefix__,
    __config_template__,
    __plugin_init_func_name__
)

cloud_api_server = __cloud_api_server__
common_pkg_prefix = __common_pkg_prefix__
inline_mode_prefix = __inline_mode_prefix__
metadata_template = __metadata_templates__[__metadata_version_in_use__]


parser = argparse.ArgumentParser(description="teelebot console command list")
parser.add_argument("-c", "--config", type=str,
                    help="specify the configuration file")
parser.add_argument("-k", "--key", type=str,
                    help="specify the bot api token")
parser.add_argument("-r", "--root", type=str,
                    help="specify the telegram user user_id of bot admin")
parser.add_argument("-p", "--plugin", type=str,
                    help="specify the plugin path")
parser.add_argument("-mp", "--make_plugin", type=str,
                    help="create a plugin template")
parser.add_argument("-L", "--logout",
                    help="log out from the cloud Bot API server before running the bot locally",
                    action="store_true")
parser.add_argument("-C", "--close",
                    help="close the bot instance before transferring it between local servers",
                    action="store_true")
parser.add_argument(
    "-hi", "--hide_info", help="hide plugin info-level console logs", action="store_true")
parser.add_argument(
    "-d", "--debug", help="run teelebot in debug mode", action="store_true")
parser.add_argument(
    "-v", "--version", help="show the current version of teelebot", action="store_true")
args = parser.parse_args()

if len(sys.argv) == 2 and args.version:
    print("\nVersion: " + __version__)
    print("Author: " + __author__)
    print("Project: " + __github__)
    os._exit(0)


def _config():
    '''
    Get the bot configuration information and initialize
    '''
    config = {}

    if args.config:
        config_dir = os.path.abspath(str(Path(args.config)))
    else:
        config_dir = str(Path(
            f"{os.path.abspath(os.path.expanduser('~'))}/.teelebot/config.cfg"))
    (path, filename) = os.path.split(config_dir)
    (filename_, extension) = os.path.splitext(filename)
    if extension != ".cfg":
        _logger.error("Only support configuration files with .cfg suffix.")
        os._exit(0)
    if not os.path.exists(str(Path(path))):
        os.makedirs(str(Path(path)))
    if not os.path.exists(str(Path(config_dir))):
        _logger.error("The configuration file does not exist.")
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
            config_data = copy.deepcopy(__config_template__)
            config_data["key"] = str(key)
            config_data["root_id"] = str(root)
            config_data["plugin_dir"] = str(plugin_dir)
            config_data["debug"] = str(debug)

            config_list = []
            for key, value in config_data.items():
                if key == "[config]":
                    config_list.append(f"{key}\n")
                else:
                    config_list.append(f"{key} = {value}\n")
            config_list[-1] = config_list[-1].strip()
            if config_list[-1].split("=")[1].strip() in [None, ""]:
                    config_list[-1] += " "

            conf_file.writelines(config_list)
            os.system("")
            _logger.info("The configuration file has been created automatically.")
            _logger.info(f"Configuration file path: \033[1;32m{str(config_dir)}\033[0m") # Green
        if not args.key or not args.root:
            _logger.warn("Please modify the relevant parameters and restart the teelebot.")
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
    if args.hide_info:
        conf.set("config", "hide_info", str(True))


    with open(config_dir, 'w', encoding="utf-8") as configfile:
        conf.write(configfile)

    if args.debug:
        default_args = ["plugin_dir", "key", "webhook", "root_id", "debug"]
    else:
        default_args = ["plugin_dir", "key", "webhook", "root_id"]
    for default_arg in default_args:
        if default_arg not in options:
            _logger.error("The configuration file is missing necessary parameters.",
                "\nnecessary parameters:", default_args)
            os._exit(0)

    for option in options:
        config[str(option)] = conf.get("config", option)

    none_count = 0
    for default_arg in default_args:
        if config[default_arg] == "" or\
            config[default_arg] == None:
            none_count += 1
            _logger.error(f"Field {default_arg} is not set in configuration file.")
    if none_count != 0:
        os._exit(0)

    if any(["version" in config.keys(), "author" in config.keys()]):
        _logger.error("Error in configuration file.")
        os._exit(0)

    if config["webhook"] == "True":
        webhook_args = ["self_signed",
                        "server_address", "server_port",
                        "local_address", "local_port",
                        "cert_pub", "cert_key"] # Optional: secret_token, load_cert
        for w in webhook_args:
            if w not in config.keys():
                _logger.error("Please check if the following fields exist in the configuration file: \n" +
                    "cert_pub cert_key self_signed server_address server_port local_address local_port")
                os._exit(0)
        if "secret_token" in config.keys() and config["secret_token"] not in [None, "", " "]:
            pattern = r"^[A-Za-z0-9_-]{1,256}$"
            if not re.match(pattern, config["secret_token"]):
                _logger.error("The format of secret_token is wrong (1-256 characters, only characters A-Z, a-z, 0-9, _ and - are allowed).")
                os._exit(0)
        if "load_cert" in config.keys() and config["load_cert"] not in [None, "", " "]:
            if config["load_cert"] == "True":
                config["load_cert"] = True
            elif config["load_cert"] == "False":
                config["load_cert"] = False
            else:
                _logger.error("The load_cert field value in the configuration file is wrong.")
                os._exit(0)
        else:
            config["load_cert"] = False
            

    plugin_dir_in_config = False
    if "plugin_dir" in config.keys():
        if config["plugin_dir"] == "" or config["plugin_dir"] == None:
            _logger.error("Field plugin_dir is not set in configuration file.")
            os._exit(0)
        else:
            plugin_dir = f'{str(Path(os.path.abspath(config["plugin_dir"])))}{os.sep}'
            plugin_dir_in_config = True
    else:
        _logger.error("Field plugin_dir does not exist in configuration file.")
        os._exit(0)

    pycache_path = f'{os.path.dirname(os.path.abspath(__file__))}/__pycache__'
    if os.path.exists(str(Path(pycache_path))):
        shutil.rmtree(str(Path(pycache_path)))

    if not os.path.isdir(plugin_dir):  # Plugin directory detection
        os.makedirs(plugin_dir)
    sys.path.append(plugin_dir)

    if args.make_plugin and plugin_dir_in_config: # Plugin template creation
        plugin_name = args.make_plugin
        if not os.path.exists(str(Path(plugin_dir + plugin_name))):
            os.mkdir(str(Path(plugin_dir + plugin_name)))

            if not os.path.exists(str(Path(f'{plugin_dir}{plugin_name}{os.sep}{plugin_name}.py'))):
                with open(str(Path(f'{plugin_dir}{plugin_name}{os.sep}{plugin_name}.py')), "w", encoding="utf-8") as enter:
                    enter.writelines([
                        "# -*- coding: utf-8 -*-\n",
                        "\n",
                        "# def " + __plugin_init_func_name__ + "(bot):\n",
                        "#     pass",
                        "\n\n",
                        "def " + plugin_name + "(bot, message):\n",
                        "\n",
                        "    # root_id = bot.root_id\n",
                        "    # bot_id = bot.bot_id\n",
                        "\n",
                        "    # author = bot.author\n",
                        "    # version = bot.version\n",
                        "\n",
                        "    # plugin_dir = bot.plugin_dir\n",
                        "    # plugin_bridge = bot.plugin_bridge\n",
                        "\n",
                        "    # uptime = bot.uptime\n",
                        "    # response_times = bot.response_times\n",
                        "    # response_chats = bot.response_chats\n",
                        "    # response_users = bot.response_users\n",
                        "\n",
                        "    # proxies = bot.proxies\n",
                        "\n",
                        '    chat_id = message.get("chat", {}).get("id")\n',
                        '    user_id = message.get("from", {}).get("id")\n',
                        '    message_id = message.get("message_id")\n',
                        "\n",
                        '    message_type = message.get("message_type")\n',
                        '    chat_type = message.get("chat", {}).get("type")\n',
                        "\n",
                        '    command = ""\n',
                        '    ok, metadata = bot.metadata.read()\n',
                        '    if ok:\n',
                        '        command = metadata.get("Command")\n',
                        "\n\n",
                        "    # Write your plugin code below"
                    ])
            if not os.path.exists(str(Path(f'{plugin_dir}{plugin_name}{os.sep}README.md'))):
                with open(str(Path(f'{plugin_dir}{plugin_name}{os.sep}README.md')), "w", encoding='utf-8') as readme:
                    readme.writelines([
                        f"# {plugin_name}\n"
                    ])
            if not os.path.exists(str(Path(f'{plugin_dir}{plugin_name}{os.sep}METADATA'))):
                with open(str(Path(f'{plugin_dir}{plugin_name}{os.sep}METADATA')), "w", encoding='utf-8') as meta:
                    metadata_data = copy.deepcopy(metadata_template)
                    metadata_data["Plugin-name"] = plugin_name
                    metadata_data["Command"] = f"/{plugin_name.lower()}"
                    metadata_data["Buffer-permissions"] = "False:False"
                    metadata_data["Version"] = "0.1.0"
                    metadata_data["Summary"] = f"{plugin_name} Plugin"
                    metadata_data["Requires-teelebot"] = f">={__version__}"

                    metadata_list = []
                    for key, value in metadata_data.items():
                        metadata_list.append(f"{key}: {value}\n")
                    metadata_list[-1] = metadata_list[-1].strip()
                    if metadata_list[-1].split(":")[1].strip() in [None, ""]:
                            metadata_list[-1] += " "

                    meta.writelines(metadata_list)

            _logger.info(f"Plugin {plugin_name} was created successfully.")
        else:
            _logger.warn(f"Plugin {plugin_name} already exists.")
        os._exit(0)
    elif args.make_plugin and not plugin_dir_in_config:
        _logger.error("The plugin_dir is not set in the configuration file.")
        os._exit(0)

    if "pool_size" in config.keys():
        if int(config["pool_size"]) < 1 or int(config["pool_size"]) > 150:
            _logger.error("Thread pool size is out of range (1-150).")
            os._exit(0)
    else:
        config["pool_size"] = "40"

    if "buffer_size" in config.keys():
        if int(config["buffer_size"]) <= 0:
            _logger.error("Data buffer_size is out of range (> 0 MiB).")
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
                _logger.error("Local api server address not support https.")
                os._exit(0)
            if "http://" not in local_api_server:
                _logger.error("Local api server address incorrect.")
                os._exit(0)
            if "telegram.org" in local_api_server:
                _logger.error("Local api server address incorrect.")
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
            _logger.error("The self_signed field value in the configuration file is wrong.")
            os._exit(0)
    else:
        config["self_signed"] = False

    if "drop_pending_updates" in config.keys():
        if config["drop_pending_updates"] == "True":
            config["drop_pending_updates"] = True
        elif config["drop_pending_updates"] == "False":
            config["drop_pending_updates"] = False
        else:
            _logger.error("The drop_pending_updates field value in the configuration file is wrong.")
            os._exit(0)
    else:
        config["drop_pending_updates"] = False

    if "updates_chat_member" in config.keys():
        if config["updates_chat_member"] == "True":
            config["updates_chat_member"] = True
        elif config["updates_chat_member"] == "False":
            config["updates_chat_member"] = False
        else:
            _logger.error("The updates_chat_member field value in the configuration file is wrong.")
            os._exit(0)
    else:
        config["updates_chat_member"] = False
    
    if "hide_info" in config.keys():
        if config["hide_info"] == "True":
            config["hide_info"] = True
        elif config["hide_info"] == "False":
            config["hide_info"] = False
        else:
            _logger.error("The hide_info field value in the configuration file is wrong.")
            os._exit(0)
    else:
        config["hide_info"] = False

    if config["debug"] == "True":
        config["debug"] = True
    elif config["debug"] == "False":
        config["debug"] = False
    else:
        _logger.error("The debug field value in the configuration file is wrong.")
        os._exit(0)

    if config["webhook"] == "True":
        config["webhook"] = True
    elif config["webhook"] == "False":
        config["webhook"] = False
    else:
        _logger.error("The webhook field value in the configuration file is wrong.")
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
    Get the mapping between plugins and commands
    '''
    plugin_bridge = {}
    non_plugin_list = []
    plugin_list = []
    corrupted_plugin_list = []

    plugin_lis = os.listdir(plugin_dir)
    for plugi in plugin_lis:
        if os.path.isdir(str(Path(f'{plugin_dir}{plugi}'))) and plugi != "__pycache__" and plugi[0] != '.':
            
            entrance_exist = False
            entrance_count = 0
            initfunc_exist = False
            initfunc_count = 0
            try:
                with open(str(Path(f"{plugin_dir}{plugi}{os.sep}{plugi}.py")), "r", encoding="utf-8") as e:
                    content = e.read()
                    if f"def {plugi}(bot, message):" in content or \
                        f"def {plugi}(message, bot):" in content or \
                        f"def {plugi}(bot,message):" in content or \
                        f"def {plugi}(message,bot):" in content:
                        entrance_exist = True
                    if entrance_exist:
                        entrance_count += content.count(f"def {plugi}(bot, message):")
                        entrance_count += content.count(f"def {plugi}(message, bot):")
                        entrance_count += content.count(f"def {plugi}(bot,message):")
                        entrance_count += content.count(f"def {plugi}(message,bot):")

                    if f"def {__plugin_init_func_name__}(bot):" in content or \
                        f"def {__plugin_init_func_name__}(bot,):" in content or \
                        f"def {__plugin_init_func_name__}(bot, ):" in content:
                        initfunc_exist = True
                    if initfunc_exist:
                        initfunc_count += content.count(f"def {__plugin_init_func_name__}(bot):")
                        initfunc_count += content.count(f"def {__plugin_init_func_name__}(bot,):")
                        initfunc_count += content.count(f"def {__plugin_init_func_name__}(bot, ):")
            except Exception as e:
                os.system("")
                _logger.error("\033[1;31mThe " + plugi + " plugin is corrupted: " + "\033[0m" + str(e))
                traceback.print_exc()
                
            metadata_ok = False
            metadata = _Metadata(plugin_dir=plugin_dir)
            ok, metadata_data = metadata.read(plugin_name=plugi)
            if ok:
                if list(metadata_data.keys()) == list(metadata_template.keys()):
                    metadata_ok = True

                    if metadata_data["Command"] == common_pkg_prefix: # Skip plugin integrity checks
                        continue
            else:
                os.system("")
                _logger.error(f"\033[1;31mThe {plugi} plugin is corrupted: \033[0m{str(metadata_data)}")

            package_file_list = os.listdir(str(Path(f'{plugin_dir}{plugi}')))
            if plugi + ".py" in package_file_list and \
                "METADATA" in package_file_list and \
                entrance_exist and entrance_count == 1 and \
                initfunc_count <= 1 and metadata_ok:
                plugin_list.append(plugi)
            else:
                corrupted_plugin_list.append(plugi)

                missing_files_count = 0
                error = f"plugin missing "
                if f"{plugi}.py" not in package_file_list:
                    error += f"'{plugi}.py' "
                    missing_files_count += 1
                if "METADATA" not in package_file_list:
                    error += "'METADATA' "
                    missing_files_count += 1
                if missing_files_count != 0:
                    os.system("")
                    _logger.error(f"\033[1;31mThe {plugi} plugin is corrupted: \033[0m{error}")
                
                if not entrance_exist:
                    error = f"plugin not found entrance function '{plugi}'"
                    os.system("")
                    _logger.error(f"\033[1;31mThe {plugi} plugin is corrupted: \033[0m{error}")
                elif entrance_exist and entrance_count != 1:
                    error = f"multiple entrance functions exist in plugin"
                    os.system("")
                    _logger.error(f"\033[1;31mThe {plugi} plugin is corrupted: \033[0m{error}")
                
                if initfunc_exist and initfunc_count != 1:
                    error = f"multiple {__plugin_init_func_name__} functions exist in plugin"
                    os.system("")
                    _logger.error(f"\033[1;31mThe {plugi} plugin is corrupted: \033[0m{error}")


                if not metadata_ok:
                    error = f"metadata format error"
                    os.system("")
                    _logger.error(f"\033[1;31mThe {plugi} plugin is corrupted: \033[0m{error}")

    for plugin in plugin_list:
        metadata_data = {}
        metadata = _Metadata(plugin_dir=plugin_dir)
        ok, data = metadata.read(plugin_name=plugin)
        if ok:
            if list(data.keys()) == list(metadata_template.keys()):
                metadata_data = data
        else:
            os.system("")
            _logger.error(f"\033[1;31mThe {plugi} plugin is corrupted: \033[0m{data}")
            continue
        
        if metadata_data["Command"] != common_pkg_prefix:  # Hidden plugin
            plugin_bridge[plugin] = metadata_data["Command"]
        else:
            if plugin in corrupted_plugin_list:
                if (f'{plugin_dir}{plugin}') in sys.path:
                    sys.path.remove(f'{plugin_dir}{plugin}')
                if (f'{plugin_dir}{plugin}') in sys.modules:
                    sys.modules.pop(f'{plugin_dir}{plugin}')
            else:
                non_plugin_list.append(plugin)
                if (f'{plugin_dir}{plugin}') not in sys.path:
                    sys.path.append(f'{plugin_dir}{plugin}')

    # print(sys.path)
    # print(plugin_bridge, non_plugin_list)
    return plugin_bridge, non_plugin_list

def _plugin_info(plugin_list, plugin_dir):
    '''
    Get the status of the plugin modification
    '''
    plugin_info = {}
    for plugin in plugin_list:
        mtime = os.stat(str(Path(f"{plugin_dir}{plugin}{os.sep}{plugin}.py"))).st_mtime
        plugin_info[plugin] = mtime

    return plugin_info


if args.close and args.logout:
    _logger.error("Only one of logout and close can be used at the same time.")
    os._exit(0)

elif args.logout and not args.close:
    config = _config()
    logout_url = f'{cloud_api_server}bot{config["key"]}/logOut'
    try:
        req = requests.post(url=logout_url, verify=False)
    except:
        _logger.error("Error request the cloud Bot API server.")
        os._exit(0)
    if req.json().get("ok"):
        _logger.info("Successfully logout from the cloud Bot API server.")
    elif not req.json().get("ok"):
        _logger.error("Error logout from the cloud Bot API server.")
        if (req.json().get("error_code") == 401 and
            req.json().get("description") == "Unauthorized"):
            _logger.error("If you already logout the bot from the cloud Bot API server,please wait at least 10 minutes and try again.")
    os._exit(0)

elif args.close and not args.logout:
    config = _config()
    if config["local_api_server"] == "False":
        _logger.error("The close can only be used when local_api_server is configured.")
        os._exit(0)

    close_url = f'{config["local_api_server"]}bot{config["key"]}/close'
    try:
        req = requests.post(url=close_url, verify=False)
    except:
        _logger.error("Error request the the local API server.")
        os._exit(0)
    if req.json().get("ok"):
        _logger.info("Successfully close from the local API server.")
    elif not req.json().get("ok"):
        _logger.error("Error close from the local API server.")
        if req.json().get("error_code") == 429:
            _logger.error(f'Too many requests, please retry after {str(req.json().get("parameters")["retry_after"])} seconds.')
    os._exit(0)


