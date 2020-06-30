# teelebot
Python实现的Telegram Bot机器人框架







## 说明 ##

本项目是基于Python和Telegram Bot API实现的Telegram Bot框架，实现了基本的插件系统。目前自带插件有以下几个：

* Menu - 自动生成的插件菜单
*   Chat - 调用 [青云客聊天机器人API](http://api.qingyunke.com/) 实现的对话功能
*   About - 关于
*   Uptime - 获取Bot持续运行时间
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



本项目在 Python 3.5 及以上版本测试通过。









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
key=your key
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







## 更新日志 ##

#### 2020-6-30

* v1.9.3 : 
  * Bot类新增 **19个** Telegram Bot API方法，Telegram Bot API现存方法已全部实现
  * 完善Bot类方法 `sendLocate` ；修复Bot类方法 `setChatPermissions` 的bug

#### 2020-6-28

* v1.8.8 : 
  * 修复当插件目录下存在非插件文件夹时会报错的bug
  * 增强命令行命令，使用 `-h/--help` 查看帮助
  * Bot类新增方法 `response_times` ，以统计框架启动后的累计指令响应次数
  * 优化插件的 `热更新` 和 `热装载` 
  * 插件 `Uptime` 新增显示累计指令响应次数

#### 2020-6-27

* v1.8.6 : 插件支持在框架运行的状态下安装和卸载

* v1.8.5 : 插件支持热更新；调整插件 Uptime 文案

#### 2020-6-26

* v1.8.3 : 
  * Bot类新增方法 `__debug_info`，在debug模式开启的情况下将显示详细错误信息
  * Bot类新增方法 `uptime` ,可获取框架持续运行时间
  * 新增插件 `Uptime` 
  * 完善插件目录检测
  * 优化消息自毁方法 `message_deletor`
  * 运行模式 `getUpdates` 更名为 `Polling`
  * 提升 `Polling` 模式响应速度

#### 2020-6-23

* v1.8.0 : 
  * 框架重构，增强性能，提升速度，进一步封装
  * 插件入口函数新增参数 `bot` ，Bot类不再需要手动导入
  * 分离 `polling` 运行模式
  * Bot类新增属性 `config` ，config 不再需要手动导入
  * 新增函数 `__connection_session()` ，引入连接池，统一管理连接
  * 新增消息自毁函数 `message_deletor()` ，消息自毁不再需要手动实现
  * 完善日志显示和 debug 模式
  * 现有插件适配此版本框架，此版本开始不再向下兼容旧版框架的插件
  
* v1.7.5 : 重构 requests 请求方式；完善日志显示

#### 2020-6-21

* v1.7.3 : 修复Guard插件长时间运行后 占用 100% CPU 的bug，感谢 [ZHLH](https://github.com/ZHLHZHU) 、[Macronut](https://github.com/macronut) 和 某位匿名朋友 的帮助

#### 2020-6-19

* v1.7.2 : 框架主体代码优化；部分插件优化；修复插件 Translate 的bug( [#1](https://github.com/plutobell/teelebot/pull/1) )，感谢 [ZHLH](https://github.com/ZHLHZHU)

#### 2020-6-17

* v1.7.1 : 修复线程池内线程异常不报错的bug，完善日志显示；修复插件 PluginCTL 的bug

#### 2020-6-16

* v1.7.0 : 新增插件 PluginCTL，插件现支持手动开关；_pluginRun 函数 支持插件 PluginCTL； 插件 Menu 适配插件 PluginCTL

#### 2020-6-15

* v1.6.8 : 线程使用线程池，提高性能和稳定性；部分插件优化；bug修复

#### 2020-6-14

* v1.6.6 : 优化 `webhook` 模式多线程，减少资源占用

#### 2020-6-13

* v1.6.5 : 完全重构 `webhook` 实现，去除依赖 Flask；修复 Guard 插件验证码选项重复的bug
* v1.6.2 : teelebot method 部分函数名字更改；优化插件 requests 请求关闭方式

#### 2020-6-12

* v1.6.1 : 优化 requests 请求关闭方式

* v1.6.0 : 新增 `Webhook` 模式运行；新增函数 washUpdates 和 pluginRun

#### 2020-6-11

* v1.5.6 : 新增函数接口 setWebhook、deleteWebhook 和 getWebhookInfo

* v1.5.5 : Agc 插件新增随图片随机显示一条一言句子

* v1.5.4 : 优化插件 Firefoxmoniter、IPinfo、Qrcode、Top

* v1.5.3 : 新增插件 TodayInHistory；新增插件 Dwz；新增插件 Acg；重构 Bing 插件

#### 2020-6-10

* v1.5.2 : 修复媒体文件类发送函数发送本地文件时被识别为 file_id 类型的bug；修复插件 Sticker 的bug；完善插件 IPinfo 的地址格式检查
* v1.5.1 : 删除函数 downloadFile，新增函数 getFileDownloadPath；新增插件 Sticker
* v1.5.0 : 媒体文件类发送函数新增通过 file_id 发送文件；新增插件 About

* v1.4.9 : 新增插件 IPinfo; 调整 ID插件消息文案
* v1.4.8 : 修复插件 Guard 验证码选项显示不全的bug；ID 插件新增查询其他用户ID的功能

* v1.4.7 : 重构插件 Guard 的 captcha，调整人机验证方式

#### 2020-6-9

* v1.4.6 : 新增插件 Qrcode；插件 Top 新增消息自毁

#### 2020-6-8

* v1.4.5 : Menu 插件新增翻页显示；优化部分函数返回值；修复 Guard 插件接收非自身 callback_query 消息的bug

#### 2020-6-7

* v1.4.4 : 新增识别 `plugins` 目录下非插件包的功能，非插件包将不被 `teelebot` 装载

* v1.4.3 : Admin 插件新增Bot权限检测；修复插件 Guard 和 Admin 的 bug；Guard 插件 captcha 时间调整

#### 2020-6-6

* v1.4.2 : 重构插件 Guard 部分代码，新增消息自毁,修复 captcha 可绕过验证的bug；修复 Admin 插件禁言时间显示bug；修复重构后插件 Guard 删除所有用户消息的 bug 

#### 2020-6-5

* v1.4.1 : 修复部分接口bug，完善 Admin 插件
* v1.4.0 : 修复 Guard 插件 captcha 验证码手动刷新无回调的bug；新增插件 Admin

#### 2020-6-4

* v1.3.9 : Guard 插件新增功能 captcha ，对入群用户进行人机检测，文案调整；插件 Menu 新增消息定时自毁

* v1.3.8 : 修复获取 callback_query 消息时无法获取触发 query 的用户的信息的bug

* v1.3.7 :  bug修复，消息轮询增加对部分Media类消息(photo、sticker、video、audio、document)的识别

#### 2020-6-2

* v1.3.6 : 新增 Updating messages 类型函数接口；bug修复

#### 2020-6-1

* v1.3.5 : 文件发送类函数支持直接发送 Bytes 流，完善 send 类函数返回值

#### 2020-5-30

* v1.3.4 : 修复插件 Guard 若干 bug；细节优化

* v1.3.3 : 插件 Guard 新增功能 guardadd,可通过Bot添加过滤关键词；代码优化

#### 2020-5-29

* v1.3.2 : 修复 kickMember 和 restrictChatMember 函数 until_date 时间问题，Guard 插件细节优化

* v1.3.1 : 修复 Firefoxiremoniter 插件 email 地址bug，插件Guard部分细节优化

#### 2020-5-28

* v1.3.0 : 新增插件 Guard，消息轮询增加对 new_chat_member 和 left_chat_participant 类型消息的识别
* v1.2.9 : 修复插件 Firefoxiremoniter 和 Top 的bug，新增插件 Translate

#### 2020-5-26

* v1.2.8 : 完善 getUpdates 函数，消息轮询增加对 callback_query 类型消息的识别，README增加插件开发指南(BETA 0.5)

* v1.2.7 : 为消息发送类函数添加 reply_markup 按钮功能，新增接口函数answerCallbackQuery

* v1.2.6 : 为消息发送类函数添加 reply_to_message_id 功能；插件适配reply_to_message_id 

#### 2020-3-22

* v1.2.5 : 修复debug模式控制失效的bug，部分插件的优化，增加每个插件的功能演示截图

* v1.2.4 : 增加插件 Top，bug修复

#### 2020-3-15

* v1.2.3 : 对Inline mode的初步支持，bug修复

* v1.2.2 : 封装2个接口，修复插件 Bing

#### 2020-3-14

* v1.2.1 : 新增插件 ID

* v1.2.0 : 封装8.5个接口，添加测试用例

#### 2019-8-25 ####

* v1.1.18 : 代码优化，Bug修复，一大波媒体相关接口的封装；Chat聊天插件增加机器人输入状态显示(还有小彩蛋)

#### 2019-8-24 ####

* v1.1.9 : 项目代码结构优化，Bug修复，第一个 Release发布(已删除)

#### 2019-8-23 ####

* v1.1.8 : 项目包化；支持自定义插件文件夹路径；配置文件存储路径优化，支持命令行输入

* v1.1.3 : 项目从TeeleBot更名为teelebot，文件路径和代码结构优化

#### 2019-8-22 ####

* v1.1.2 : 优化配置文件存储方式

#### 2019-8-21 ####

* v1.1.1 : 优化部分函数代码，添加插件Bing

* v1.1.0 : 一大波群管理相关接口的封装，代码优化

#### 2019-8-17 ####

* v1.0.8 : 修复程序编码问题，添加插件Firefoxmoniter

#### 2019-8-15 ####

* v1.0.7 : 重构部分代码，添加下载图片的功能

#### 2019-8-14 ####

* v1.0.1 : 修复了当接收数据为None时的错误
* v1.0.0 : 基本实现

