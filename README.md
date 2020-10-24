# teelebot
Python实现的Telegram Bot机器人框架，拥有插件系统，插件支持热更新和热装载。





## 说明 ##

本项目是基于Python和Telegram Bot API实现的Telegram Bot框架，实现了插件系统。目前自带插件有以下几个：

* Menu - 自动生成的插件菜单
*   Chat - 调用 [青云客聊天机器人API](http://api.qingyunke.com/) 实现的对话功能
*   About - 关于
*   Uptime - 获取Bot运行状态
*   PluginCTL - 插件开关控制
*  Hello - Hello World插件例子
*  Firefoxmoniter - 调用 [Firefox Moniter](https://monitor.firefox.com/) ,搜索自2007年起的公开数据外泄事件当中是否包含你的电子邮件
*  Bing - 调用第三方Bing壁纸接口 [Bing](https://asilu.com) 获取每日必应壁纸
*  ID - 获取你的用户ID
*  Top - 调用top命令查看服务器状态
*  Translate - 调用 [有道翻译](http://fanyi.youdao.com/) API 对文字进行翻译
*  Guard - 广告过滤， 使用 DFA 对消息进行过滤；入群验证码人机检测
*  Admin - 群管插件，管理员可通过指令对群进行管理(踢人、禁言等)
*  Qrcode - 二维码生成插件，调用 [Goole API](https://google.com) 生成二维码
*  IPinfo - 查询IP地址信息，调用 [ip-api](https://ip-api.com/) 查询IP信息
*  Sticker - Sticker插件，获取贴纸图片
*  TodayInHistory - TodayInHistory插件，调用 [Kate.API](https://api.66mz8.com/) 查看历史上的今天
*  Dwz - Dwz插件，调用 [ALAPI](https://www.alapi.net/) 生成短网址
*  Acg - Acg插件，调用 [ALAPI](https://www.alapi.net/) 随机获取一张ACG图
*  Whois - Whois插件，调用 [ALAPI](https://www.alapi.net/) 查询域名whois信息



本项目在 Python 3.5 及以上版本测试通过。





## 更新日志 ##

* [更新日志](./CHANGELOG.md)





## Telegram Bot API现存方法已全部实现 （2020/6/30）

**Getting updates**

* getUpdates
* setWebhook
* deleteWebhook
* getWebhookInfo

**Available methods**

* getMe
* getFile
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
* sendVoice
* sendAnimation
* sendAudio
* sendVideo
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





## Demo ##

* Telegram群组： [teelebot体验群](http://t.me/teelebot_chat)（t.me/teelebot_chat）









## 环境要求 ##

### Python版本

teelebot 只支持 Python3.x，不支持Python2.x。





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
plugin_dir=your plugin dir   //[Optional]
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





## 插件开发指南 (以 Hello 插件为例) BETA 0.6

#### 一、插件结构

一个完整的 `teelebot` 插件应当呈现为一个文件夹，即一个Python包，以 `Hello` 插件为例，最基本的目录结构如下：

```Python
Hello/
  ./__init__.py
  ./Hello.py
  ./Hello_screenshot.png
  ./readme.md
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
bot.plugin_dir + "<plugin dir name>/<resource address>"
```

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







## 联系我 ##

* Email：hi#ojoll.com ( # == @ )
* Blog:    [北及](https://ojoll.com)
* Telegram群组：[teelebot体验群](http://t.me/teelebot_chat)（t.me/teelebot_chat）
* 其他：本repo 的 Issue







