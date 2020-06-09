# -*- coding:utf-8 -*-

name = "teelebot"
__all__ = ['Bot']

from .teelebot import Bot

def main():
    bot = Bot()
    bot._run()