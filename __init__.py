# -*- coding:utf-8 -*-

__all__ = ['Bot']

from .teelebot import Bot

def main():
    bot = Bot()
    bot._run()