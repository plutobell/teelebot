# -*- coding:utf-8 -*-
'''
@creation date: 2020-06-23
@last modification: 2023-12-26
'''
import os

from .logger import _logger


def _runUpdates(bot):

    _logger.info("Bot Start.")

    bot._update_plugins_init_status()
    bot._plugins_init(bot)

    while True:
        try:
            results = bot.getUpdates(
                offset=bot._offset,
                limit=100,
                timeout=bot._timeout,
                allowed_updates=bot._allowed_updates
            ) # Get the message queue 'messages'
            messages = bot._washUpdates(results)
            if messages is None or not messages:
                continue
            for message in messages:  # Retrieve a single message 'message'
                bot._pluginRun(bot, message)
        except KeyboardInterrupt:
            _logger.info("Bot Exit.")
            os._exit(0)


