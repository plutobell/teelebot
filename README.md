# TeeleBot 
Python实现的Telegram Bot机器人框架







## 说明 ##

本项目是基于Python和Telegram Bot API实现的Telegram Bot框架，实现了基本的插件系统。目前自带插件有三个：

* Menu  -   自动生成的插件菜单
*   Chat  -   调用 [思知(OwnThink)](https://www.ownthink.com/)机器人开放API实现的对话功能
*  Hello  -   Hello World插件例子



目前此项目在 Python 3.6 及以上版本测试通过，如果您发现有任何问题，欢迎给我提 Issue 或 Pull Request。







## Telegram Bot API封装情况

### 已实现 ###

* getMe
* getUpdates
* sendMessage
* sendPhoto
* sendDocument



目标是封装官方所有的Method，任重道远呀~







## Demo ##

* Telegram群组： [TeeleBot体验群](http://t.m/isTeeleBot)









## 环境要求 ##

### Python版本

TeeleBot 只支持 Python3.x，不支持Python2.x。





## 使用 ##

1.克隆或点击下载本项目到本地，保证本机安装有`Python3.x`版本和包`requests`；

2.修改`config.py`文件中的密钥为你自己机器人的密钥；

3.终端下进入项目文件夹，输入`python3 teelebot.py`回车,正常情况下你应该能看见屏幕提示机器人开始运行。



服务器端可配合`supervisor`使用。







## 联系我 ##

* Email：hi@ojoll.com
* Telegram群组：[TeeleBot体验群](http://t.m/isTeeleBot)
* 其他：本repo 的 Issue







## 更新历史 ##

#### 2019-8-14 ####

* v1.0.1 : 修复了当接收数据为None时的错误
* v1.0.0 : 基本实现

