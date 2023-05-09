# Function (teelebot version >= v2.0.0)

#### bot API methods

可用方法名及参数同Telegram官方文档保持一致：[**Telegram Bot API**](https://core.telegram.org/bots/api)



*特殊情况：*

* *bot.sendMediaGroup*()
* *bot.editMessageMedia*()

*使用以上两个方法上传本地文件时，请使用参数 `files` ，格式请参考 [inputmedia](https://core.telegram.org/bots/api#inputmedia)*



#### teelebot methods

*  bot.message_deletor(*time_gap*: int, *chat_id*: str, *message_id*: str) -> str
*  bot.timer(*time_gap*: int, *func*: Callable[..., None], *args*: tuple) -> str
*  bot.path_converter(*path*: str) -> str
*  bot.join_plugin_path(*path*: str, *plugin_name*: str = None) -> str
*  bot.get_plugin_info(*plugin_name*: str = None) -> dict
*  bot.getChatCreator(*chat_id*: str) -> Union[bool, dict]
*  bot.getChatMemberStatus(*chat_id*: str, *user_id*: str) -> Union[bool, str]
*  bot.getFileDownloadPath(*file_id*: str) -> Union[bool, str]
*  bot.getChatAdminsUseridList(*chat_id*, *skip_bot*: bool = True, *privilege_users*: list = None) -> Union[bool, list]
*  bot.schedule.add(*gap*: int, *func*: Callable[..., None], *args*: tuple) -> Tuple[bool, str]
*  bot.schedule.status() -> Tuple[bool, dict]
*  bot.schedule.find(*uid*: str) -> Tuple[bool, str]
*  bot.schedule.delete(*uid*: str) -> Tuple[bool, str]
*  bot.schedule.clear() -> Tuple[bool, str]
*  bot.buffer.status() -> Tuple[bool, dict]
*  bot.buffer.sizeof(*plugin_name*: str = None) -> Tuple[bool, Union[str, int]]
*  bot.buffer.read(*plugin_name*: str = None) -> Tuple[bool, Union[str, tuple, any]]
*  bot.buffer.write(*buffer*: any, *plugin_name*: str = None) -> Tuple[bool, Union[str, tuple]]



#### teelebot properties

*  bot.root_id
*  bot.bot_id
*  bot.author
*  bot.version
*  bot.plugin_dir
*  bot.plugin_bridge
*  bot.uptime
*  bot.response_times
*  bot.response_chats
*  bot.response_users
*  bot.proxies



