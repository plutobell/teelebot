'''
@creation date: 2021-04-25
@last modification: 2024-04-14
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
        self.__buffer_mutex = threading.RLock()
        self.__buffer = {}
        self.__metadata = _Metadata(self.__plugin_dir)

        for plugin_name in self.__plugin_names:
            self.__buffer[plugin_name] = {}
            self.__buffer[plugin_name]["default"] = {}

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

    def create(self, plugin_name: str = None, buffer_name: str = "default"
            ) -> Tuple[bool, Union[str, tuple, any]]:
        """
        Create a buffer area
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
            try:
                with self.__buffer_mutex:
                    if buffer_name in self.__buffer[plugin_name].keys():
                        return False, "BufferExisted"
                    else:
                        self.__buffer[plugin_name][buffer_name] = {}
                        return True, ""
            except Exception as e:
                _logger.error(e)
                traceback.print_exc()
                return False, str(e)
        else:
            return False, "PluginNotFound"
        
    def drop(self, plugin_name: str = None, buffer_name: str = None
            ) -> Tuple[bool, Union[str, tuple, any]]:
        """
        Destroy a buffer area
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
            
            try:
                with self.__buffer_mutex:
                    if buffer_name in self.__buffer[plugin_name].keys():
                        self.__buffer[plugin_name].pop(buffer_name)
                        return True, ""
                    else:
                        return False, "BufferNotFound"
            except Exception as e:
                _logger.error(e)
                traceback.print_exc()
                return False, str(e)
        else:
            return False, "PluginNotFound"
    
    def show(self, plugin_name: str = None) -> Tuple[bool, Union[str, tuple, dict]]:
        """
        Show all buffer area for single plugin
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
            
            buffers = {}
            with self.__buffer_mutex:
                for key, value in self.__buffer[plugin_name].items():
                    buffers[key] = {
                        "used": self.__total_size(value),
                        "count": len(value)
                    }
                    
            return True, buffers
        else:
            return False, "PluginNotFound"

    def insert(self, plugin_name: str = None, buffer_name: str = "default",
            data: dict = {}) -> Tuple[bool, Union[str, tuple]]:
        """
        Insert data into the buffer area
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

            try:
                with self.__buffer_mutex:
                    if buffer_name not in self.__buffer[plugin_name].keys():
                        if buffer_name == "default":
                            self.__buffer[plugin_name][buffer_name] = {}
                        else:
                            return False, "BufferNotFound"

                    old_total_used = self.__total_size(self.__buffer)
                    old_buffer_used = self.__total_size(self.__buffer[plugin_name])
                    new_buffer_used = self.__total_size(data)

                    if (old_total_used - old_buffer_used) + new_buffer_used > self.__buffer_size:
                        return False, "BufferAreaIsFull"
                    else:
                        last_id = -1
                        if len(self.__buffer[plugin_name][buffer_name].keys()) > 0:
                            last_id = max(self.__buffer[plugin_name][buffer_name].keys())
                        self.__buffer[plugin_name][buffer_name][last_id+1] = copy.deepcopy(data)
                        return True, last_id+1
            except Exception as e:
                _logger.error(e)
                traceback.print_exc()
                return False, str(e)
        else:
            return False, "PluginNotFound"

    def delete(self, plugin_name: str = None, buffer_name: str = "default",
            idx: int = None, conditions: dict = {}) -> Tuple[bool, Union[str, tuple, any]]:
        """
        Delete data from the buffer area
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

            selected_logs_idx = []
            changed_size = 0
            try:
                with self.__buffer_mutex:
                    if buffer_name not in self.__buffer[plugin_name].keys():
                        if buffer_name == "default":
                            self.__buffer[plugin_name][buffer_name] = {}
                        else:
                            return False, "BufferNotFound"

                    if idx != None:
                        if idx in self.__buffer[plugin_name][buffer_name].keys():
                            selected_logs_idx.append(idx)
                    else:
                        for id_x, log in self.__buffer[plugin_name][buffer_name].items():
                            conditions_ok_count = 0
                            for key, value in conditions.items():
                                if key in list(log.keys()) and log[key] == value:
                                    conditions_ok_count += 1
                            if conditions_ok_count == len(conditions):
                                    selected_logs_idx.append(id_x)

                    for id_x in selected_logs_idx:
                        changed_size += self.__total_size(self.__buffer[plugin_name][buffer_name][id_x])
                        self.__buffer[plugin_name][buffer_name].pop(id_x)
                    
                return True, str(changed_size)
            except Exception as e:
                _logger.error(e)
                traceback.print_exc()
                return False, str(e)
        else:
            return False, "PluginNotFound"

    def update(self, plugin_name: str = None, buffer_name: str = "default",
            idx: int = None, conditions: dict = {}, data: dict = {}
            ) -> Tuple[bool, Union[str, tuple, any]]:
        """
        Update data of the buffer area
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
                    return False, "NoPermissionToRead"
            else:
                return False, permissions

            selected_logs_idx = []
            changed_size = 0
            try:
                with self.__buffer_mutex:
                    if buffer_name not in self.__buffer[plugin_name].keys():
                        if buffer_name == "default":
                            self.__buffer[plugin_name][buffer_name] = {}
                        else:
                            return False, "BufferNotFound"

                    old_total_used = self.__total_size(self.__buffer)
                    old_buffer_used = self.__total_size(self.__buffer[plugin_name])
                    new_buffer_used = self.__total_size(data)

                    if (old_total_used - old_buffer_used) + new_buffer_used > self.__buffer_size:
                        return False, "BufferAreaIsFull"
                    else:
                        if idx != None:
                            if idx in self.__buffer[plugin_name][buffer_name].keys():
                                selected_logs_idx.append(idx)
                        else:
                            for id_x, log in self.__buffer[plugin_name][buffer_name].items():
                                conditions_ok_count = 0
                                for key, value in conditions.items():
                                    if key in list(log.keys()) and log[key] == value:
                                        conditions_ok_count += 1
                                if conditions_ok_count == len(conditions):
                                        selected_logs_idx.append(id_x)

                        for id_x in selected_logs_idx:
                            for key, value in data.items():
                                self.__buffer[plugin_name][buffer_name][id_x][key] = copy.deepcopy(data[key])
                                changed_size += self.__total_size(data[key])
                return True, str(changed_size)
            except Exception as e:
                _logger.error(e)
                traceback.print_exc()
                return False, str(e)
        else:
            return False, "PluginNotFound"

    def select(self, plugin_name: str = None, buffer_name: str = "default",
            idx: int = None, conditions: dict = {}
            ) -> Tuple[bool, Union[str, tuple, dict, any]]:
        """
        Select data from the buffer area
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

            selected_logs = {}
            try:
                with self.__buffer_mutex:
                    if buffer_name not in self.__buffer[plugin_name].keys():
                        if buffer_name == "default":
                            self.__buffer[plugin_name][buffer_name] = {}
                        else:
                            return False, "BufferNotFound"

                    if idx != None:
                        if idx in self.__buffer[plugin_name][buffer_name].keys():
                            selected_logs[idx] = copy.deepcopy(self.__buffer[plugin_name][buffer_name][idx])
                    else:
                        if len(conditions) == 0 or conditions == {}:
                            return True, copy.deepcopy(self.__buffer[plugin_name][buffer_name])

                        for id_x, log in self.__buffer[plugin_name][buffer_name].items():
                            conditions_ok_count = 0
                            for key, value in conditions.items():
                                if key in list(log.keys()) and log[key] == value:
                                    conditions_ok_count += 1
                            if conditions_ok_count == len(conditions):
                                    selected_logs[id_x] = copy.deepcopy(self.__buffer[plugin_name][buffer_name][id_x])
                    
                return True, selected_logs
            except Exception as e:
                _logger.error(e)
                traceback.print_exc()
                return False, str(e)
        else:
            return False, "PluginNotFound"

    def clear(self, plugin_name: str = None, buffer_name: str = None
            ) -> Tuple[bool, Union[str, tuple, any]]:
        """
        Empty the buffer area
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
            
            changed_size = 0
            try:
                with self.__buffer_mutex:
                    if plugin_name != None and buffer_name != None:
                        if buffer_name not in self.__buffer[plugin_name].keys():
                            return False, "BufferNotFound"

                        changed_size = self.__total_size(self.__buffer[plugin_name][buffer_name])
                        self.__buffer[plugin_name][buffer_name].clear()
                    elif plugin_name != None and buffer_name == None:
                        changed_size = self.__total_size(self.__buffer[plugin_name])
                        self.__buffer[plugin_name].clear()

                return True, str(changed_size)
            except Exception as e:
                _logger.error(e)
                traceback.print_exc()
                return False, str(e)
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
    

    