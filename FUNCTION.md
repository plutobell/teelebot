## Function (teelebot version >= v2.0.0)

**bot API methods**

可用方法名及参数同Telegram官方文档保持一致：[**Telegram Bot API**](https://core.telegram.org/bots/api)



*特殊情况：*

* *sendMediaGroup*
* *editMessageMedia*

*使用以上两个方法上传本地文件时，请使用参数 `files` ，格式请参考 [inputmedia](https://core.telegram.org/bots/api#inputmedia)*



**teelebot methods**

*  getFileDownloadPath(*file_id*)
*  getChatMemberStatus(*chat_id*, *user_id*)
*  getChatCreator(*chat_id*)
*  message_deletor(*time_gap*, *chat_id*, *message_id*)
*  path_converter(*path*)
*  timer(*time_gap*, *func*, *args*)
*  schedule.add(*gap*, *func*, *args*)
*  schedule.delete(*uid*)
*  schedule.find(*uid*)
*  schedule.clear()
*  schedule.status()
*  buffer.status()
*  buffer.sizeof(*plugin_name*=None)
*  buffer.read(*plugin_name*=None)
*  buffer.write(*buffer*, *plugin_name*=None)



**teelebot properties**

*  root_id
*  bot_id
*  author
*  version
*  plugin_dir
*  plugin_bridge
*  uptime
*  response_times
*  response_chats 
*  response_users
*  proxies



