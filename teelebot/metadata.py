'''
@creation date: 2023-05-12
@last modification: 2024-02-28
'''
import os
import copy
import inspect
import traceback
import threading

from pathlib import Path
from typing import Tuple, Union

from .logger import _logger
from .common import __metadata_templates__, __metadata_version_in_use__

class _Metadata(object):
    """
    METADATA Class
    """
    def __init__(self, plugin_dir):
        self.__plugin_dir = plugin_dir
        self.__metadata_mutex = threading.RLock()
        self.__metadata_template = __metadata_templates__[__metadata_version_in_use__]

    def __del__(self):
        del self.__metadata_mutex
        del self.__metadata_template

    def read(self, plugin_name: str = None,
            plugin_dir: str = None) -> Tuple[bool, Union[dict, str]]:
        """
        Read the METADATA data
        """
        if plugin_name in [None, "", " "]:
            plugin_name = os.path.splitext(os.path.basename(inspect.stack()[1][1]))[0]

        if plugin_dir in [None, "", " "]:
            plugin_dir = self.__plugin_dir
        else:
            plugin_dir = f'{Path(plugin_dir)}{os.sep}'

        if not os.path.isdir(str(Path(plugin_dir))) or \
            not os.path.exists(Path(plugin_dir)):
            return False, "PluginDirNotFound"

        if not os.path.isdir(str(Path(f"{plugin_dir}{plugin_name}"))) or \
            not os.path.exists(Path(f"{plugin_dir}{plugin_name}")):
            return False, "PluginNotFound"
        
        metadata = {}
        try:
            with self.__metadata_mutex:
                with open(Path(f"{plugin_dir}{plugin_name}{os.sep}METADATA"), "r", encoding="utf-8") as meta:
                    lines = meta.readlines()
                    for line in lines:
                        line = line.strip("\n").strip(" ")
                        if line in [None, "", " "]:
                            continue
                        line_list = line.split(":", 1)
                        if len(line_list) == 2:
                            metadata[line_list[0].replace(" ", "")] = line_list[1].strip(" ")
                        elif len(line_list) == 1:
                            metadata[line_list[0].replace(" ", "")] = ""

                    if "Metadata-version" in list(metadata.keys()):
                        if metadata["Metadata-version"] != self.__metadata_template["Metadata-version"]:
                            return False, "MetadataVersionError"

                    if len(metadata["Buffer-permissions"].split(":")) == 2:
                        permissions_read = metadata["Buffer-permissions"].split(":")[0]
                        permissions_write = metadata["Buffer-permissions"].split(":")[1]
                        if permissions_read in ["True", "False", "true", "false"] and \
                            permissions_write in ["True", "False", "true", "false"]:
                            pass
                        else:
                            return False, "BufferPermissionsFormatError"
                    else:
                        return False, "BufferPermissionsFormatError"

                    if not (list(metadata.keys()) == list(self.__metadata_template.keys())):
                        return False, "MetadataFormatError"
                    else:
                        return True, metadata
        except Exception as e:
            os.system("")
            _logger.error(f"\033[1;31mError to read metadata of {plugin_name} plugin:\033[0m {str(e)}")
            traceback.print_exc()
            return False, "ReadMetadataError"
                
    def write(self, metadata: dict,
            plugin_name: str = None, plugin_dir: str = None) -> Tuple[bool, Union[dict, str]]:
        """
        Write the METADATA data
        """
        if plugin_name in [None, "", " "]:
            plugin_name = os.path.splitext(os.path.basename(inspect.stack()[1][1]))[0]

        if plugin_dir in [None, "", " "]:
            plugin_dir = self.__plugin_dir
        else:
            plugin_dir = f'{Path(plugin_dir)}{os.sep}'

        if not os.path.isdir(str(Path(plugin_dir))) or \
            not os.path.exists(Path(plugin_dir)):
            return False, "PluginDirNotFound"

        if not os.path.isdir(str(Path(f"{plugin_dir}{plugin_name}"))) or \
            not os.path.exists(Path(f"{plugin_dir}{plugin_name}")):
            return False, "PluginNotFound"
        
        if not isinstance(metadata, dict):
            return False, "MetadataMustBeDict"
        if not "Metadata-version" in list(metadata.keys()):
            return False, "MetadataFormatError"
        if metadata["Metadata-version"] != self.__metadata_template["Metadata-version"]:
            return False, "MetadataVersionError"
        if not (list(metadata.keys()) == list(self.__metadata_template.keys())):
            return False, "MetadataFormatError"
        
        metadata_type_ok = True
        for key, value in metadata.items():
            if not isinstance(key, str) or not isinstance(value, str):
                metadata_type_ok = False
        if not metadata_type_ok:
            return False, "MetadataKeyandValueMustBeString"

        if len(metadata["Buffer-permissions"].split(":")) == 2:
            permissions_read = metadata["Buffer-permissions"].split(":")[0]
            permissions_write = metadata["Buffer-permissions"].split(":")[1]
            if permissions_read in ["True", "False", "true", "false"] and \
                permissions_write in ["True", "False", "true", "false"]:
                pass
            else:
                return False, "BufferPermissionsFormatError"
        else:
            return False, "BufferPermissionsFormatError"

        metadata_list = []
        for key, value in metadata.items():
                metadata_list.append(f"{key}: {value}\n")
        metadata_list[-1] = metadata_list[-1].strip()
        if metadata_list[-1].split(":")[1].strip() in [None, ""]:
            metadata_list[-1] += " "
        
        try:
            with self.__metadata_mutex:
                with open(Path(f"{plugin_dir}{plugin_name}{os.sep}METADATA"), "w", encoding="utf-8") as meta:
                    meta.writelines(metadata_list)
            return True, ""
        except Exception as e:
            os.system("")
            _logger.error(f"\033[1;31mError to write metadata of {plugin_name} plugin:\033[0m {str(e)}")
            traceback.print_exc()
            return False, "WriteMetadataError"
        
    def template(self, version: str = None) -> Tuple[bool, Union[dict, str]]:
        """
        Get METADATA data template
        """
        try:
            if version in [None, "", " "]:
                version = __metadata_version_in_use__
            return True, copy.deepcopy(__metadata_templates__[__metadata_version_in_use__])
        except Exception as e:
            os.system("")
            _logger.error(f"\033[1;31mError to get metadata template:\033[0m {str(e)}")
            traceback.print_exc()
            return False, "GetMetadataTemplateError"


