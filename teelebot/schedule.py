# -*- coding:utf-8 -*-
'''
@creation date: 2019-11-15
@last modification: 2023-07-12
'''
import threading
import traceback

from uuid import uuid4
from typing import Tuple, Callable

from .logger import _logger

class _Schedule(object):
    """
    Schedule Class
    """
    def __init__(self, queue_size):
        self.__queue_size = queue_size
        self.__queue_mutex = threading.Lock()
        self.__queue = {}

    def __del__(self):
        del self.__queue

    def __create(self, gap, func, args):
        class RepeatingTimer(threading.Timer):
            def run(self):
                while not self.finished.is_set():
                    self.function(*self.args, **self.kwargs)
                    self.finished.wait(self.interval)
        try:
            t = RepeatingTimer(gap, func, args)
            t.setDaemon(True)
            return True, t
        except Exception as e:
            _logger.error(str(e))
            traceback.print_exc()
            return False, str(e)

    def add(self, gap: int, func: Callable[..., None], args: tuple) -> Tuple[bool, str]:
        """
        Add schedule task
        """
        def __short_uuid():
            uuidChars = ("a", "b", "c", "d", "e", "f",
                    "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s",
                    "t", "u", "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5",
                    "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G", "H", "I",
                    "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V",
                    "W", "X", "Y", "Z")
            uuid = str(uuid4().hex)
            uid = ''
            for i in range(0,8):
                sub = uuid[i * 4: i * 4 + 4]
                x = int(sub,16)
                uid += uuidChars[x % 0x3E]
            return uid

        if len(self.__queue) == self.__queue_size:
            return False, "Full"

        ok, t = self.__create(gap, func, args)
        if ok:
            t.start()
            uid = __short_uuid()
            with self.__queue_mutex:
                self.__queue[uid] = t

            return True, uid
        else:
            return False, t

    def status(self) -> Tuple[bool, dict]:
        """
        Retrieve usage statistics of the Schedule task pool
        """
        try:
            with self.__queue_mutex:
                used = len(self.__queue)
                free = self.__queue_size - used
                size = self.__queue_size

            result = {
                "used": used,
                "free": free,
                "size": size
            }
            return True, result
        except Exception as e:
            _logger.error(str(e))
            traceback.print_exc()
            return False, {"exception": e}

    def find(self, uid: str) -> Tuple[bool, str]:
        """
        Find schedule tasks
        """
        with self.__queue_mutex:
            if len(self.__queue) <= 0:
                return False, "Empty"

            if str(uid) in self.__queue.keys():
                return True, str(uid)
            else:
                return False, "NotFound"

    def delete(self, uid: str) -> Tuple[bool, str]:
        """
        Remove schedule tasks
        """
        if len(self.__queue) <= 0:
            return False, "Empty"

        if str(uid) in self.__queue.keys():
            self.__queue[str(uid)].cancel()
            with self.__queue_mutex:
                self.__queue.pop(str(uid))

            return True, str(uid)
        else:
            return False, "NotFound"

    def clear(self) -> Tuple[bool, str]:
        """
        Remove all schedule tasks
        """
        if len(self.__queue) == 0:
            return False, "Empty"
        else:
            try:
                for uid in list(self.__queue.keys()):
                    self.__queue[str(uid)].cancel()

                with self.__queue_mutex:
                    self.__queue.clear()

                return True, "Cleared"
            except Exception as e:
                _logger.error(str(e))
                traceback.print_exc()
                return False, str(e)


