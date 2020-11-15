# teelebot
Python实现的Telegram Bot**机器人框架**，具有**插件系统**，插件支持**热更新**和**热装载**。





## 说明 ##

本项目是基于Python和Telegram Bot API实现的Telegram Bot**框架**，具有**插件系统**。目前预置插件有以下几个：

1. Menu - 自动生成的插件菜单

2. Chat - 调用 [青云客聊天机器人API](http://api.qingyunke.com/) 实现的对话功能
3. About - 关于
4. Uptime - 获取Bot运行状态
5. ID - 获取你的用户ID
6. PluginCTL - 插件开关控制
7. Hello - Hello World插件例子



**更多插件请前往：[官方插件仓库](https://github.com/plutobell/teelebot-plugins)**







## 更新日志 ##

* **[更新日志](./CHANGELOG.md)**





## 已升级至 Telegram Bot API 5.0（2020/11/9）

**Getting updates**

* getUpdates
* setWebhook
* deleteWebhook
* getWebhookInfo

**Available methods**

* getMe
* getFile
* logOut
* close
* sendMessage
* sendPhoto
* sendDocument
* kickChatMember
* unbanChatMember
* leaveChat
* getChat
* getChatAdministrators
* getChatMembersCount
* getChatMember
* setChatPermissions
* restrictChatMember
* promoteChatMember
* pinChatMessage
* unpinChatMessage
* unpinAllChatMessages
* sendVoice
* sendAnimation
* sendAudio
* sendVideo
* sendPoll
* sendDice
* sendVideoNote
* getUserProfilePhotos
* setChatTitle
* setChatDescription
* setChatPhoto
* deleteChatPhoto
* sendLocation
* sendContact
* sendVenue
* sendChatAction
* forwardMessage
* copyMessage
* kickChatMember
* unbanChatMember
* restrictChatMember
* setChatAdministratorCustomTitle
* exportChatInviteLink
* setChatStickerSet
* deleteChatStickerSet
* sendMediaGroup
* getMyCommands
* setMyCommands
* editMessageLiveLocation
* stopMessageLiveLocation

**Inline mode**

* answerCallbackQuery

**Updating messages**

* editMessageText
* editMessageCaption
* editMessageMedia
* editMessageReplyMarkup
* stopPoll
* deleteMessage

**Inline mode**

* answerInlineQuery

**Stickers**

* sendSticker
* getStickerSet
* uploadStickerFile
* createNewStickerSet
* addStickerToSet
* setStickerPositionInSet
* deleteStickerFromSet
* setStickerSetThumb

**Payments**

* sendInvoice
* answerShippingQuery
* answerPreCheckoutQuery

**Telegram Passport**

* setPassportDataErrors

**Games**

* sendGame
* setGameScore
* getGameHighScores



**teelebot method**

*  getFileDownloadPath
* message_deletor
* uptime
* response_times
* response_chats 
* response_users
* path_converter
* add_schedule
* del_schedule
* find_schedule
* clear_schedule
* stat_schedule





## Demo ##

* Telegram群组： [teelebot体验群](http://t.me/teelebot_chat)（t.me/teelebot_chat）
* Bot : [teelebot](http://t.me/teelebot)（t.me/teelebot）







## 环境要求 ##

### Python版本

teelebot 只支持 Python3.x，不支持Python2.x。

本项目在 Python 3.5 及以上版本测试通过。





## 使用 ##

#### 一、运行模式

`teelebot` 支持以 `Webhook` 模式和 `Polling` 模式运行。生产环境推荐使用 `Webhook` 模式，而 `Polling` 则仅用于开发环境。

##### 1、Webhook 模式

`teelebot` 的 Webhook 目前仅支持 **`自签名证书`**。若要以 `Webhook` 模式运行，请将配置文件字段 `webhook` 设置为 `True` ，并且添加以下字段：

```python
[config]
webhook=True
cert_pub=your public certificate dir //Optional while webhook is False
server_address=your server ip address or domain //Optional while webhook is False
server_port=your server port //Optional while webhook is False
local_address=webhook local address //Optional while webhook is False
local_port=webhook local port ////Optional while webhook is False
```

`cert_pub` 为你的公钥路径(绝对路径)，`server_address` 为你的服务器公网IP, `server_port` 为服务器的端口(目前 telegram 官方仅支持 443,  80,  88,  8443)，`local_address` 为Webhook 本地IP地址， `local_port` 为 Webhook 本地运行的端口。

推荐搭配 `nginx` 使用，自签名证书生成请参考：[Generating a self-signed certificate pair (PEM)](https://core.telegram.org/bots/self-signed#generating-a-self-signed-certificate-pair-pem)



##### 2、Polling 模式

要以 Polling 模式运行，只需要保证配置文件 `webhook` 字段为 `False` 即可。



##### 3、最基本的配置文件 (以Polling模式为例)

```python
[config]
key=bot key
pool_size=40
webhook=False
root=your user id
debug=False
timeout=60
plugin_dir=your plugin dir //[Optional]
```







#### 二、源码运行 ####

1.克隆或点击下载本项目到本地，保证本机安装有`Python3.x`版本和包`requests` ；



2.`config.cfg` 配置文件

配置文件格式:

```python
[config]
key=bot key
pool_size=40 //the thread pool size, default 40, range(1, 101)
webhook=False
cert_pub=your public certificate dir //Optional while webhook is False
server_ip=your server ip address //Optional while webhook is False
server_port=your server port //Optional while webhook is False
local_address=webhook local address //Optional while webhook is False
local_port=webhook local port //Optional while webhook is False
root=your user id
debug=False
timeout=60
plugin_dir=your plugin dir //[Optional]
local_api_server=local api server address //[Optional]
```

* Linux

在 `/root` 目录下创建文件夹 `.teelebot` ,并在其内新建配置文件 `config.cfg` ,按照上面的格式填写配置文件

* Windows

在 `C:\Users\<username>`  目录下创建文件夹 `.teelebot` ,并在其内新建配置文件 `config.cfg` ,按照上面的格式填写配置文件

* 指定配置文件

Linux 和 Windows 都可在命令行通过参数手动指定配置文件路径，命令格式：

```
python -m teelebot -c/--config <configure file path>
```

路径必须为绝对路径。

**更多指令请通过 `-h/--help` 查看。**



3.运行

终端下进入teelebot文件夹所在目录。

* 对于使用程序配置文件默认路径的：

  输入`python -m teelebot` 回车,正常情况下你应该能看见屏幕提示机器人开始运行。

* 对于命令行手动指定配置文件路径的：

  输入`python -m teelebot -c/--config <configure file path>` 回车,正常情况下你应该能看见屏幕提示机器人开始运行。(更多指令请通过 `-h/--help` 查看)



#### 三、Pip安装运行

##### 安装 #####

* 确保本机Python环境拥有pip包管理工具。

* 在本项目Releases页面下载包文件。

* 本机命令行进入包文件所在目录，执行：

  ```
  pip install <teelebot package file name>
  
  or
  
  pip3 install <teelebot package file name>
  ```

由于API未封装完毕，暂未上传至 `PyPI` ,故不能在线安装，望谅解。

##### 运行 #####

任意路径打开终端，输入以下命令：

- 对于使用程序配置文件默认路径的：

  输入`teelebot` 回车,正常情况下你应该能看见屏幕提示机器人开始运行。

- 对于命令行手动指定配置文件路径的：

  输入`teelebot -c/--config <configure file path>` 回车,正常情况下你应该能看见屏幕提示机器人开始运行。(更多指令请通过 `-h/--help` 查看)



可配合`supervisor`使用。





## 插件开发指南 (以 Hello 插件为例) BETA 0.8

#### 一、插件结构

一个完整的 `teelebot` 插件应当呈现为一个文件夹，即一个Python包，以 `Hello` 插件为例，最基本的目录结构如下：

```Python
Hello/
  ./__init__.py
  ./Hello.py
  ./Hello_screenshot.png
  ./readme.md
  ./requirement.txt
```

#### 二、规则

##### 命名

在构建teelebot插件中应当遵守的规则是：每个插件目录下应当存在一个与插件同名的`.py` 文件，比如插件 `Hello ` 中的 `Hello.py` 文件，并且此文件中必须存在作为插件入口的同名函数，以插件 `Hello` 为例：

```python
#file Hello/Hello.py

# -*- coding:utf-8 -*-

def Hello(bot, message):
    pass
```

函数 `Hello()` 即为插件的入口函数，参数 `bot` 为Bot接口库实例化对象，参数 `message` 用于接收消息数据。



##### 资源路径

若要打开某个插件目录下的文件资源，需要使用的路径应当遵循以下的格式：

```python
bot.path_converter(bot.plugin_dir + "<plugin dir name>/<resource address>")
```

方法 `path_converter` 根据操作系统转换路径格式。



#### 三、自定义触发指令

##### 插件指令

插件的触发指令可不同于插件名，允许自定义。以插件 `Hello` 为例，触发指令为 `/helloworld` 而不是 `Hello`。

修改插件目录下的 `__init__.py` 文件设置触发指令：

```python
#file Hello/__init__.py

#/helloworld
#Hello World插件例子
```

第一行为触发指令，默认以 `/`  作为前缀；第二行为插件简介。



##### 不用作插件的特殊情况

通常情况下，位于 `plugins` 目录下的所有包都将被识别为插件并自动加载到 `teelebot` 中。但在某些情况下，存在并不用作插件而只是多个插件共用包的情况，若想该包不被 `teelebot` 加载，请将触发指令设置为 `~~`  。以 `tools` 共用包为例， `__init__.py` 文件内容如下：

```python
#fille tools/__init__.py

#~~
#tools 包的简介
```

建议用作插件的包名遵守 `Pascal命名法`，即每个单词的首字母大写；而不用做插件的包名使用全小写的包名，每个单词之间以`_`  分隔。以区分 `插件包` 和 `非插件包` ：

```python
- plugins
  - Menu    #插件包
  - tools   #非插件包
```



#### 四、插件模板创建工具

在 `v1.9.20_dev` 及以上版本，可以通过命令行指令**一键创建**插件模板。

##### 一、源码运行

```python
python -m teelebot -p/--plugin <plugin name>
```

##### 二、Pip安装运行

```python
teelebot -p/--plugin <plugin name>
```

该指令会使用框架配置文件(config.cfg)中的插件路径作为所创建插件模板的存放路径。



#### 五、周期性任务

在 `v1.11.1` 及以上版本，可以创建**周期性任务**，功能类似**循环定时器**。

可获得的方法：

*  **schedule.add** : 添加任务
*  **schedule.delete** : 移除任务
*  **schedule.find** : 查找任务
*  **schedule.clear** : 清空任务池
*  **schedule.status** : 查看任务池状态

例：

```python
ok, uid = bot.schedule.add(gap, event, (bot, ))
ok, uid = bot.schedule.delete(uid)
ok, uid = bot.schedule.find(uid)
ok, uid = bot.schedule.clear()
ok, uid = bot.schedule.status()
```



周期性任务池的大小为全局线程池的**三分之一** ，线程池大小则可通过配置文件指定。



## 联系我 ##

* Email：hi#ojoll.com ( # == @ )
* Blog:    [北及](https://ojoll.com)
* Telegram群组：[teelebot体验群](http://t.me/teelebot_chat)（t.me/teelebot_chat）
* 其他：本repo 的 Issue







