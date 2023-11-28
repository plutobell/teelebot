<h1 align="center">
  <br>
  <a href="#" alt="logo" ><img src="./LOGO.png" width="150"/></a>
  <br>
  teelebot
  <br>
</h1>
<h4 align="center">Python实现的Telegram Bot机器人框架，具有插件系统，插件支持热更新和热装载。</h4>

```bash
    __            __     __          __
   / /____  ___  / /__  / /_  ____  / /_
  / __/ _ \/ _ \/ / _ \/ __ \/ __ \/ __/
 / /_/  __/  __/ /  __/ /_/ / /_/ / /_
 \__/\___/\___/_/\___/_.___/\____/\__/

```





## 说明

**teelebot** 是Python编写的Telegram Bot框架。**teelebot** 具有**插件系统**，Bot功能以插件的形式组织，你只需要实现具有特定功能的插件，其余细节交给 **teelebot** 框架处理，极大地提高了Bot的开发部署效率。**你可以自由地组合插件，来搭建具有特定功能的Bot**。



**插件请前往：[官方插件仓库](https://github.com/plutobell/teelebot-plugins)**

**推荐插件：**

* **Menu** - 自动生成的插件菜单

* **Uptime** - 获取Bot运行状态

* **PluginCTL** - 插件分群开关控制

* **PluginManagementTools** - 插件包管理工具

* **Guard** - 广告过滤， 使用 DFA 对消息进行过滤；入群验证码人机检测

  





## 更新日志

* **[更新日志](./CHANGELOG.md)**



## 方法列表

* **[方法列表](./FUNCTION.md)**



## 插件开发指南

* **[插件开发指南](./PLUGINGUIDE.md)**



## Demo

* **Telegram Group：[teelebot official](https://t.me/teelebot_official)（t.me/teelebot_official）**
* **Bot : [teelebotBot](https://t.me/teelebotBot)（t.me/teelebotBot）**
* ~~Telegram Group： [teelebot体验群](http://t.me/teelebot_chat)（t.me/teelebot_chat）~~
* ~~Bot : [teelebot](http://t.me/teelebot)（t.me/teelebot）~~







## 环境要求

### Python版本

teelebot 只支持 Python3.x，不支持Python2.x。

本项目在 Python 3.6 及以上版本测试通过。





## 安装

**1.Pip**

```bash
pip install teelebot
```

**此方式推荐使用Python虚拟环境安装**



**2.Docker**

```bash
# 无代理
docker run -it \
	--name teelebot \
	--restart always \
	-v /path/to/teelebot/config:/config \
	-v /path/to/teelebot/plugins:/plugins \
	ghcr.io/plutobell/teelebot:latest
	
# 有代理
docker run -it \
	--name teelebot \
	--restart always \
	--network host \
	-e http_proxy="http://ip:port" \
	-e https_proxy="http://ip:port" \
	-v /path/to/teelebot/config:/config \
	-v /path/to/teelebot/plugins:/plugins \
	ghcr.io/plutobell/teelebot:latest
```

**Tip: 容器创建后请完善配置文件参数，然后重启容器**







## 升级

**1.Pip**

```
pip install teelebot --upgrade
```

**2.Docker**

```bash
# 与Docker容器升级方法相同
```

另外，可通过 `exec` 指令在容器中执行命令 `pip install teelebot --upgrade` 进行升级





## 使用

#### 一行命令启动 (Polling Mode)

请自行替换 `< ... >` 的内容

```
teelebot -c/--config <config file path> -p/--plugin <plugin path> -k/--key <bot key> -r/--root <your user id>
```

**此命令会自动生成在Polling模式下适用的配置文件，并且，-c/--config 参数可以省略(省略将使用默认配置文件路径)。**



#### 一、运行模式

`teelebot` 支持以 `Webhook` 模式和 `Polling` 模式运行。生产环境推荐使用 `Webhook` 模式，而 `Polling` 则仅用于开发环境。



##### 1、Webhook 模式

要以 `Webhook` 模式运行，请将配置文件字段 `webhook` 设置为 `True` ，此模式涉及的配置文件字段如下：

```python
[config]
webhook=True
self_signed=False
cert_key=your private cert path
cert_pub=your public cert path
load_cert=False
server_address=your server ip address or domain
server_port=your server port
local_address=webhook local address
local_port=webhook local port
secret_token=webhook secret token
```

`self_signed` 用于设置是否使用自签名证书，而 `cert_key` 和 `cert_pub` 是你的证书路径(绝对路径)，`load_cert` 则用于设置 Webhook 是否加载本地证书； `server_address` 为你的服务器公网IP, `server_port` 为服务器的端口(目前 telegram 官方仅支持 443,  80,  88,  8443)，`local_address` 为Webhook 本地监听地址， `local_port` 为 Webhook 本地运行的端口；`secret_token` 则用于设置 Webhook 的secret token。

自签名证书生成请参考：[Generating a self-signed certificate pair (PEM)](https://core.telegram.org/bots/self-signed#generating-a-self-signed-certificate-pair-pem)



##### 2、Polling 模式

要以 Polling 模式运行，只需要保证配置文件 `webhook` 字段为 `False` 即可。此模式最基本的配置文件如下:

```
[config]
key=bot key
root_id=your user id
pool_size=40
webhook=False
debug=False
plugin_dir=your plugin dir
```







#### 二、运行

任意路径打开终端，输入以下命令：

- 对于使用程序配置文件默认路径的：

  输入`teelebot` 回车,正常情况下你应该能看见屏幕提示机器人开始运行。

- 对于命令行手动指定配置文件路径的：

  输入`teelebot -c/--config <configure file path>` 回车,正常情况下你应该能看见屏幕提示机器人开始运行。
  
  **更多指令请通过 `-h/--help` 查看：**
  
  ```bash
  usage: -m [-h] [-c CONFIG] [-k KEY] [-r ROOT] [-p PLUGIN] [-mp MAKE_PLUGIN]
            [-L] [-C] [-d] [-v]
  
  teelebot console command list
  
  options:
    -h, --help            show this help message and exit
    -c CONFIG, --config CONFIG
                          specify the configuration file
    -k KEY, --key KEY     specify the bot api token
    -r ROOT, --root ROOT  specify the telegram user user_id of bot admin
    -p PLUGIN, --plugin PLUGIN
                          specify the plugin path
    -mp MAKE_PLUGIN, --make_plugin MAKE_PLUGIN
                          create a plugin template
    -L, --logout          use it to log out from the cloud Bot API server before
                          launching the bot locally
    -C, --close           use it to close the bot instance before moving it from
                          one local server to another
    -d, --debug           run teelebot in debug mode
    -v, --version         show the current version of teelebot
  ```
  
  







#### 三、配置文件

**完整的配置文件**如下所示:

```python
[config]
key=bot key
root_id=your user id
plugin_dir=your plugin dir
pool_size=40 # the thread pool size, default 40, range(1, 101)
buffer_size=16 # the buffer area size, default 16(MB)
webhook=False
self_signed=False # Optional while webhook is False
cert_key=your private cert path # Optional while webhook is False
cert_pub=your public cert path # Optional while webhook is False
load_cert=False # Optional while webhook is False
server_ip=your server ip address # Optional while webhook is False
server_port=your server port # Optional while webhook is False
local_address=webhook local address # Optional while webhook is False
local_port=webhook local port # Optional while webhook is False
secret_token=webhook secret token
debug=False
drop_pending_updates=False
local_api_server=local api server address # [Optional]
updates_chat_member=False # [Optional]
proxy=socks5h://user:pass@host:port # [Optional]
```

**在 `1.13.0` 及以上版本，支持自动生成配置文件。（默认为Polling模式）**

1.在命令行未指定配置文件路径的情况下，会在默认配置文件路径下不存在配置文件时自动生成配置文件 `config.cfg`。

* 在Linux下，会自动在用户目录下创建文件夹 `.teelebot` ，并生成配置文件 `config.cfg`

* 在Windows下，则会在 `C:\Users\<username>`  目录下创建文件夹 `.teelebot` ，并生成配置文件 `config.cfg` 

2.指定配置文件

Linux 和 Windows 都可在命令行通过参数手动指定配置文件路径，命令格式：

```
teelebot -c/--config <configure file path>
```

路径必须为绝对路径，并且配置文件名也应当包含在路径内，此情况下会在指定的配置文件不存在时自动生成配置文件 。



#### 四、导入使用

```python
# 导入Bot类
from teelebot import Bot

# 实例化Bot类
# 不传参数时会使用teelebot默认配置文件路径下的配置文件实例化Bot类
# 在v2.2.0及以上版本，可传递参数覆盖配置文件的设定，可覆盖的参数:
#     Bot(key: str = None, debug: bool = False, proxies: dict = None)
bot = Bot()

# 使用Bot类
bot.sendMessage(chat_id="chat_id", text="Hello World!")
```

**Tip: 导入使用时需要确保默认配置文件路径中存在配置文件,并且必须的字段已经填写**





## 联系我

* Email：hi#ojoll.com ( # == @ )
* Blog:    [北及](https://ojoll.com)
* Telegram Group：[teelebot official](https://t.me/teelebot_official)（t.me/teelebot_official）
* ~~Telegram Group：[teelebot体验群](http://t.me/teelebot_chat)（t.me/teelebot_chat）~~
* 其他：本repo 的 Issue







