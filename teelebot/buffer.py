'''
@creation date: 2021-04-25
@last modification: 2023-07-12
'''
from __future__ import print_function
from sys import getsizeof, stderr
from itertools import chain
from collections import deque
from pathlib import Path
from typing import Tuple, Union
try:
    from reprlib import repr
except ImportError:
    pass

import threading
import inspect
import traceback
import os
import copy

from .metadata import _Metadata
from .logger import _logger

class _Buffer(object):
    """
    Buffer Class
    """
    def __init__(self, buffer_size, plugin_names, plugin_dir):
        self.__buffer_size = buffer_size
        self.__plugin_names = plugin_names
        self.__plugin_dir = plugin_dir
        self.__buffer_mutex = threading.Lock()
        self.__buffer = {}
        self.__metadata = _Metadata(self.__plugin_dir)

        for plugin_name in self.__plugin_names:
            self.__buffer[plugin_name] = {}

    def __del__(self):
        del self.__buffer
        del self.__buffer_mutex

    def status(self) -> Tuple[bool, dict]:
        """
        Get the usage information of the buffer area,
        measured in bytes
        """
        try:
            with self.__buffer_mutex:
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
            _logger.error(e)
            traceback.print_exc()
            return False, {"exception": e}

    def sizeof(self, plugin_name: str = None) -> Tuple[bool, Union[str, int]]:
        """
        Get the memory size occupied by the buffer area of a single plugin,
        measured in bytes
        """
        if plugin_name in [None, "", " "]:
            plugin_name = os.path.splitext(os.path.basename(inspect.stack()[1][1]))[0]

        if plugin_name in self.__buffer.keys():
            with self.__buffer_mutex:
                return True, self.__total_size(self.__buffer.get(plugin_name))
        else:
            return False, "PluginNotFound"

    def read(self, plugin_name: str = None) -> Tuple[bool, Union[str, tuple, any]]:
        """
        Read data from buffer area
        """
        isSelf = False
        if plugin_name in [None, "", " "]:
            isSelf = True
            plugin_name = os.path.splitext(os.path.basename(inspect.stack()[1][1]))[0]

        if plugin_name in self.__buffer.keys():
            ok, permissions = self.__permissions_check(plugin_name)
            if ok:
                permissions_read = permissions[0]
                # permissions_write = permissions[1]
                if not permissions_read and not isSelf:
                    return False, "NoPermissionToRead"
            else:
                return False, permissions

            with self.__buffer_mutex:
                return True, copy.deepcopy(self.__buffer.get(plugin_name, {}))
        else:
            return False, "PluginNotFound"

    def write(self, buffer: any, plugin_name: str = None) -> Tuple[bool, Union[str, tuple]]:
        """
        Write data into the buffer area
        """
        isSelf = False
        if plugin_name in [None, "", " "]:
            isSelf = True
            plugin_name = os.path.splitext(os.path.basename(inspect.stack()[1][1]))[0]

        if plugin_name in self.__buffer.keys():
            ok, permissions = self.__permissions_check(plugin_name)
            if ok:
                # permissions_read = permissions[0]
                permissions_write = permissions[1]
                if not permissions_write and not isSelf:
                    return False, "NoPermissionToWrite"
            else:
                return False, permissions

            with self.__buffer_mutex:
                old_total_used = self.__total_size(self.__buffer)
                old_buffer_used = self.__total_size(self.__buffer[plugin_name])
                new_buffer_used = self.__total_size(buffer)

                if (old_total_used - old_buffer_used) + new_buffer_used > self.__buffer_size:
                    return False, "BufferAreaIsFull"
                else:
                    self.__buffer[plugin_name] = copy.deepcopy(buffer)
                    changed_size = self.__total_size(buffer)
                    return True, str(changed_size)
        else:
            return False, "PluginNotFound"

    def _update(self, plugin_names):
        if str(inspect.stack()[1][3]) == "__load_plugin":
            with self.__buffer_mutex:
                for plugin_name in list(self.__buffer.keys()): # Clean up uninstalled plugins
                    if plugin_name not in plugin_names:
                        self.__buffer.pop(plugin_name)

                for plugin_name in list(plugin_names):
                    if plugin_name not in self.__buffer.keys(): # Add new plugins
                        self.__buffer[plugin_name] = {}

            return True
        else:
            return False

    def __permissions_check(self, plugin_name):
        if plugin_name in self.__buffer.keys():
            if plugin_name != os.path.splitext(os.path.basename(inspect.stack()[1][1]))[0]: # Read/write access check
                permissions = "False:False"
                ok, data = self.__metadata.read(plugin_name=plugin_name)
                if ok:
                    if data["Buffer-permissions"] not in [None, "", " "]:
                        permissions = data["Buffer-permissions"]
                    bool_dict = {
                        "True": True,
                        "true": True,
                        "False": False,
                        "false": False
                    }
                    permissions_read = bool_dict[permissions.split(":")[0]]
                    permissions_write = bool_dict[permissions.split(":")[1]]

                    return True, tuple((permissions_read, permissions_write))
                else:
                    return False, data

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
                _logger.error(s, type(o), repr(o), file=stderr)

            for typ, handler in all_handlers.items():
                if isinstance(o, typ):
                    s += sum(map(sizeof, handler(o)))
                    break
            return s

        return sizeof(o)
    

    