# -*- coding:utf-8 -*-
'''
@creation date: 2019-11-15
@last modify: 2020-11-18
'''
import threading
from uuid import uuid4

class _Schedule(object):
    """
    周期性任务类
    """
    def __init__(self, queue_size):
        self.__queue_size = queue_size
        self.__queue_mutex = threading.Lock()
        self.__queue = {}

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
            print(e)
            return False, str(e)

    def add(self, gap, func, args):
        """
        添加周期性任务
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

    def status(self):
        """
        获取周期性任务池的使用情况
        """
        try:
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
            return False, {"exception": e}

    def find(self, uid):
        """
        查找周期性任务
        """
        if len(self.__queue) <= 0:
            return False, "Empty"

        if str(uid) in self.__queue.keys():
            return True, str(uid)
        else:
            return False, "NotFound"

    def delete(self, uid):
        """
        移除周期性任务
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

    def clear(self):
        """
        移除所有周期性任务
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
                return False, str(e)
