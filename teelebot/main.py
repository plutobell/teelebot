'''
@creation date: 2025-05-26
@last modification: 2025-05-26
'''
import os
import requests
import urllib3

from .polling import _runUpdates
from .webhook import _runWebhook
from .logger import _init_logger
from .bot import Bot

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():

    bot = Bot()
    VERSION = bot.version

    _logger = _init_logger(file_log=bot._file_log, file_log_dir=bot._file_log_dir)

    if bot._local_api_server != "False":
        api_server = "Local"
    else:
        api_server = "Remote"

    TEELEBOT = "\033[1m\033[38;2;123;120;176m"
    RESET = "\033[0m"

    print(
        f"{TEELEBOT}    __            __     __          __  \n" +
        "   / /____  ___  / /__  / /_  ____  / /_ \n" +
        "  / __/ _ \\/ _ \\/ / _ \\/ __ \\/ __ \\/ __/ \n" +
        " / /_/  __/  __/ /  __/ /_/ / /_/ / /_   \n" +
        f" \\__/\\___/\\___/_/\\___/_.___/\\____/\\__/   \n{RESET}"
    )
    print(f" {TEELEBOT}-> Self-checking...{RESET}", end="\r")
    req = requests.post(url=f'{bot._url}getWebhookInfo', verify=False, proxies=bot.proxies)
    if not req.json().get("ok"):
        if (req.json().get("error_code") == 401 and \
            req.json().get("description") == "Unauthorized"):
            _logger.warning("\nIf you already logout the bot from the cloud Bot API server,please wait at least 10 minutes and try again.")
        else:
            _logger.error("\nFailed to get running mode!")
        os._exit(0)

    status = req.json().get("result")
    pending_update_count = status["pending_update_count"]
    allowed_updates = status.get("allowed_updates", [])

    if bot._webhook:
        protocol = "https://"
        if bot._local_api_server != "False":
            protocol = "http://"
        url = f'{protocol}{str(bot._server_address)}:{str(bot._server_port)}/bot{str(bot._key)}'
        if (bot._drop_pending_updates == True and pending_update_count != 0) \
            or (status["url"] != url) or (status["has_custom_certificate"] != bot._self_signed) \
            or status["max_connections"] != int(bot._pool_size) \
            or allowed_updates != bot._allowed_updates:
            if bot._self_signed:
                with open(bot._cert_pub, 'rb') as cert_pub:
                    cert_pub_bytes = cert_pub.read()
                    status = bot.setWebhook(
                        url=url,
                        certificate=cert_pub_bytes,
                        max_connections=bot._pool_size,
                        allowed_updates=bot._allowed_updates,
                        drop_pending_updates=bot._drop_pending_updates,
                        secret_token=bot._secret_token
                    )
            else:
                status = bot.setWebhook(
                    url=url,
                    max_connections=bot._pool_size,
                    allowed_updates=bot._allowed_updates,
                    drop_pending_updates=bot._drop_pending_updates,
                    secret_token=bot._secret_token
                )

            if not status:
                _logger.error("\nFailed to set Webhook!")
                os._exit(0)

        info = (
            f" -> The teelebot starts running\n"
            f" * Version : v{VERSION}\n"
            f" *    Mode : Webhook\n"
            f" * Threads : {str(bot._pool_size)}\n"
            f" *  Server : {api_server}\n"
            f" *  Config : {bot._config_dir}\n"
            f" *  Plugin : {bot.plugin_dir}\n"
        )
        if bot._file_log is True:
            info += f" *    Logs : {bot._file_log_dir}\n"
        if isinstance(bot._proxies, dict):
            if bot._proxies and bot._proxies != {"all": None}:
                info += f" *   Proxy : Yes\n"
        print(f"{TEELEBOT}{info}{RESET}")
        _runWebhook(bot=bot, host=bot._local_address, port=int(bot._local_port))

    else:
        if status["url"] != "" or status["has_custom_certificate"]:
            status = bot.deleteWebhook()
            if not status:
                _logger.error("\nFailed to set getUpdates!")
                os._exit(0)

        info = (
            f" -> The teelebot starts running\n"
            f" * Version : v{VERSION}\n"
            f" *    Mode : Polling\n"
            f" * Threads : {str(bot._pool_size)}\n"
            f" *  Server : {api_server}\n"
            f" *  Config : {bot._config_dir}\n"
            f" *  Plugin : {bot.plugin_dir}\n"
        )
        if bot._file_log is True:
            info += f" *    Logs : {bot._file_log_dir}\n"
        if isinstance(bot._proxies, dict):
            if bot._proxies and bot._proxies != {"all": None}:
                info += f" *   Proxy : Yes\n"
        print(f"{TEELEBOT}{info}{RESET}")
        if bot._drop_pending_updates == True and pending_update_count != 0:
            results = bot.getUpdates(
                offset=bot._offset,
                limit=100,
                timeout=bot._timeout,
                allowed_updates=bot._allowed_updates
            )
            bot._washUpdates(results)
        _runUpdates(bot=bot)
