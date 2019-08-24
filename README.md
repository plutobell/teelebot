# teelebot
Python实现的Telegram Bot机器人框架







## 说明 ##

本项目是基于Python和Telegram Bot API实现的Telegram Bot框架，实现了基本的插件系统。目前自带插件有以下几个：

* Menu  -   自动生成的插件菜单
*   Chat  -   调用 [青云客聊天机器人API](http://api.qingyunke.com/) 实现的对话功能
*  Hello  -   Hello World插件例子
*  Firefoxmoniter -  调用 [Firefox Moniter](https://monitor.firefox.com/) ,搜索自2007年起的公开数据外泄事件当中是否包含你的电子邮件。
*  Bing - 调用第三方Bing壁纸接口 [bing](https://github.com/xCss/bing) 获取每日必应壁纸



目前此项目在 Python 3.6 及以上版本测试通过，如果您发现有任何问题，欢迎给我提 Issue 或 Pull Request。







## Telegram Bot API封装情况

### 已实现（18/42） ###

* getMe
* getUpdates
* getFile & downloadFile
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



目标是封装官方所有的Method，任重道远呀~







## Demo ##

* Telegram群组： [teelebot体验群](http://t.me/isteelebot)（t.me/isteelebot）









## 环境要求 ##

### Python版本

teelebot 只支持 Python3.x，不支持Python2.x。





## 使用 ##

#### 一、源码运行 ####

1.克隆或点击下载本项目到本地，保证本机安装有`Python3.x`版本和包`requests`；



2.`config.cfg` 配置文件

配置文件格式:

```
[config]
key=your key
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
python -m teelebot -c/-C <configure file path>
```

路径必须为绝对路径。



3.运行

终端下进入teelebot文件夹所在目录。

* 对于使用程序配置文件默认路径的：

  输入`python -m teelebot` 回车,正常情况下你应该能看见屏幕提示机器人开始运行。

* 对于命令行手动指定配置文件路径的：

  输入`python -m teelebot -c/-C <configure file path>` 回车,正常情况下你应该能看见屏幕提示机器人开始运行。



#### 二、Pip安装运行

##### 安装 #####

* 确保本机Python环境拥有pip包管理工具。

* 在本项目Releases页面下载包文件。

* 本机命令行进入包文件所在目录，执行：

  ```
  pip install <teelebot package file name>
  
  or
  
  pip3 install <teelebot package file name>
  ```

由于API未封装完毕，暂未上传至 `PyPI` ,故不能在线安装，忘谅解。

##### 运行 #####

任意路径打开终端，输入以下命令：

- 对于使用程序配置文件默认路径的：

  输入`teelebot` 回车,正常情况下你应该能看见屏幕提示机器人开始运行。

- 对于命令行手动指定配置文件路径的：

  输入`teelebot -c/-C <configure file path>` 回车,正常情况下你应该能看见屏幕提示机器人开始运行。





服务器端可配合`supervisor`使用。







## 联系我 ##

* Email：hi#ojoll.com ( # == @ )
* Blog:    [北及](https://ojoll.com)
* Telegram群组：[teelebot体验群](http://t.me/isteelebot)（t.me/isteelebot）
* 其他：本repo 的 Issue







## 更新历史 ##

#### 2019-8-24 ####

* v1.1.9 : 项目代码结构优化，Bug修复，第一个 Release发布

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

