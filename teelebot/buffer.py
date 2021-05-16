'''
@creation date: 2021-04-25
@last modify: 2021-04-26
'''
from __future__ import print_function
from sys import getsizeof, stderr
from itertools import chain
from collections import deque
try:
    from reprlib import repr
except ImportError:
    pass

import threading
import inspect
import os
from pathlib import Path


class _Buffer(object):
    """
    数据暂存器类
    """
    def __init__(self, buffer_size, plugin_names, plugin_dir):
        self.__buffer_size = buffer_size
        self.__plugin_names = plugin_names
        self.__plugin_dir = plugin_dir
        self.__buffer_mutex = threading.Lock()
        self.__buffer = {}

        for plugin_name in self.__plugin_names:
            self.__buffer[plugin_name] = {}

    def __del__(self):
        del self.__buffer

    def status(self):
        """
        获取数据暂存区的使用情况
        单位为字节
        """
        try:
            used = self.__total_size(self.__buffer)
            free = self.__buffer_size - used
            size = self.__buffer_size

            result = {
                "used": used,
                "free": free,
                "size": size
            }
            return True, result
        except Exception as e:
            return False, {"exception": e}

    def sizeof(self, plugin_name=None):
        """
        获取单个插件数据暂存区占用内存大小
        单位为字节
        """
        if plugin_name is None:
            plugin_name = str(inspect.stack()[1][3])

        if plugin_name in self.__buffer.keys():
            with self.__buffer_mutex:
                return True, self.__total_size(self.__buffer.get(plugin_name))
        else:
            return False, "NoPlugin"

    def read(self, plugin_name=None):
        """
        从暂存区读取数据
        """
        isSelf = False
        if plugin_name is None:
            isSelf = True
            plugin_name = str(inspect.stack()[1][3])

        if plugin_name in self.__buffer.keys():
            ok, permission = self.__permission_check(plugin_name)
            if ok:
                permission_read = permission[0]
                # permission_write = permission[1]
                if not permission_read and not isSelf:
                    return False, "NoPermissionToRead"
            else:
                return False, permission

            with self.__buffer_mutex:
                return True, self.__buffer.get(plugin_name, {}).copy()
        else:
            return False, "NoPlugin"

    def write(self, buffer, plugin_name=None):
        """
        写入数据到暂存区
        """
        isSelf = False
        if plugin_name is None:
            isSelf = True
            plugin_name = str(inspect.stack()[1][3])

        if plugin_name in self.__buffer.keys():
            ok, permission = self.__permission_check(plugin_name)
            if ok:
                # permission_read = permission[0]
                permission_write = permission[1]
                if not permission_write and not isSelf:
                    return False, "NoPermissionToWrite"
            else:
                return False, permission

            with self.__buffer_mutex:
                buffer_temp = buffer.copy()
                self.__buffer[plugin_name] = buffer

                ok, result = self.status()
                if ok:
                    used = result["used"]
                    size = result["size"]

                if used >= size:
                    self.__buffer[plugin_name] = buffer_temp
                    return False, "BufferAreaIsFull"
                else:
                    changed_size = self.__total_size(buffer)
                    return True, str(changed_size)
        else:
            return False, "NoPlugin"

    def _update(self, plugin_names):
        if str(inspect.stack()[1][3]) == "__load_plugin":
            with self.__buffer_mutex:
                for plugin_name in list(self.__buffer.keys()): # 清理已卸载插件
                    if plugin_name not in plugin_names:
                        self.__buffer.pop(plugin_name)

                for plugin_name in list(plugin_names):
                    if plugin_name not in self.__buffer.keys(): # 添加新插件
                        self.__buffer[plugin_name] = {}

            return True
        else:
            return False

    def __permission_check(self, plugin_name):
        if plugin_name in self.__buffer.keys():
            if plugin_name != str(inspect.stack()[1][3]): # 读写权限检查
                with open(Path(self.__plugin_dir + plugin_name + os.sep + "__init__.py"), "r", encoding="utf-8") as init:
                    lines = init.readlines()

                for i, _ in enumerate(lines):
                    lines[i].strip("\n")
                    lines[i].strip("\r")
                    lines[i].strip("")

                if len(lines) > 2:
                    permission = lines[2][1:]
                    if lines[2] == "#":
                        permission = "False:False"
                else:
                    permission = "False:False" # 格式 读:写

                if len(permission.split(":")) == 2:
                    permission_read = permission.split(":")[0]
                    permission_write = permission.split(":")[1]
                    if permission_read in ["True", "False", "true", "false"] and \
                        permission_write in ["True", "False", "true", "false"]:
                        bool_dict = {
                            "True": True,
                            "true": True,
                            "False": False,
                            "false": False
                        }
                        permission_read = bool_dict[permission_read]
                        permission_write = bool_dict[permission_write]
                        return True, tuple((permission_read, permission_write))
                    else:
                        return False, "PermissionFormatError"
                else:
                    return False, "PermissionFormatError"

    def __total_size(self, o, handlers={}, verbose=False):
        dict_handler = lambda d: chain.from_iterable(d.items())
        all_handlers = {tuple: iter,
                        list: iter,
                        deque: iter,
                        dict: dict_handler,
                        set: iter,
                        frozenset: iter,
                    }
        all_handlers.update(handlers)
        seen = set()
        default_size = getsizeof(0)

        def sizeof(o):
            if id(o) in seen:
                return 0
            seen.add(id(o))
            s = getsizeof(o, default_size)

            if verbose:
                print(s, type(o), repr(o), file=stderr)

            for typ, handler in all_handlers.items():
                if isinstance(o, typ):
                    s += sum(map(sizeof, handler(o)))
                    break
            return s

        return sizeof(o)