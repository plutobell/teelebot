# 插件开发指南 (以 Hello 插件为例) v1.5

#### 一、插件结构

一个完整的 `teelebot` 插件应当呈现为一个文件夹，即一个Python包，以 `Hello` 插件为例，目录结构如下：

```Python
Hello/
  ./__init__.py
  ./Hello.py
  ./METADATA
  ./README.md
  ./Hello_screenshot.png
```

**Tip：可通过命令行指令创建插件模板**

#### 二、规则

##### 命名

在构建teelebot插件中应当遵守的规则是：每个插件目录下应当存在一个与插件同名的`.py` 文件，比如插件 `Hello ` 中的 `Hello.py` 文件，并且此文件中必须存在作为插件入口的同名函数，以插件 `Hello` 为例：

```python
file Hello/Hello.py

# -*- coding:utf-8 -*-

def Hello(bot, message):
    pass
```

函数 `Hello()` 即为插件的入口函数，参数 `bot` 为Bot接口库实例化对象，参数 `message` 用于接收消息数据。



**在 `v2.4.0` 及以上版本，插件引入了初始化函数 `Init(bot)`** ，参数 `bot` 为Bot接口库实例化对象。该函数类似Python类的 `__init__` 方法，在框架运行后，无论插件是否被触发，都会执行一次。**另外，插件的重装和修改都会重新触发此函数的执行**。以插件 `Hello` 的初始化函数为例：

```python
# 该函数会在框架运行后，在控制台输出字符串： Hello World!
def Init(bot):
    print("Hello World!")
```





##### 资源路径

1.若要打开某个插件目录下的文件资源，可以使用方法 `path_converter` ，此方法会根据操作系统转换路径格式：

```python
bot.path_converter(bot.plugin_dir + "<plugin dir name>/<resource address>")
```

2.**在 `v2.1.0` 及以上版本，引入了方法 `join_plugin_path` ,此方法会根据提供的路径自动拼接为插件目录的URI：**

```python
bot.join_plugin_path("<resource address>")
```

以获取 `Hello` 插件目录下的 `Hello_screenshot.png` 文件的路径为例：

```python
# 两种方式效果相同

bot.path_converter(bot.plugin_dir + "Hello/Hello_screenshot.png")

bot.join_plugin_path("Hello_screenshot.png")

```







#### 三、自定义触发指令

##### 插件指令

插件的触发指令可不同于插件名，允许自定义。以插件 `Hello` 为例，触发指令为 `/helloworld` 而不是 `Hello`。

修改插件目录下的 `METADATA` 文件的 `Command` 字段设置触发指令：

```yaml
file Hello/METADATA

Metadata-version: 1.1
Plugin-name: Hello
Command: /helloworld
Summary: Hello World插件例子
...
```



##### 不用作插件的特殊情况

通常情况下，位于 `plugins` 目录下的所有包都将被识别为插件并自动加载到 `teelebot` 中。但在某些情况下，存在并不用作插件而只是多个插件共用包的情况，若想该包不被 `teelebot` 加载为插件，请确保该包路径下存在 `METADATA` 文件，并将触发指令设置为 `~~`  。以 `tools` 共用包为例， `METADATA` 文件内容如下：

```yaml
fille tools/METADATA

Metadata-version: 1.1
Plugin-name: tools
Command: ~~
Summary: tools包简介
...
```

建议用作插件的包名遵守 `Pascal命名法`，即每个单词的首字母大写；而不用做插件的包名使用全小写的包名，每个单词之间以 `_` 分隔。以区分 `插件包` 和 `非插件包` ：

```python
- plugins
  - Menu    #插件包
  - tools   #非插件包
```



##### Inline Mode 下的插件指令

若要编写 **`Inline Mode`** 类型插件，请将**触发指令前缀**更改为 **`?:`** 。

以插件 `InlineModeDemo` 为例，`METADATA` 文件内容如下：

```yaml
file InlineModeDemo/METADATA

Metadata-version: 1.1
Plugin-name: InlineModeDemo
Command: ?:search:
Summary: InlineMode插件例子
...
```

根据`METADATA` 文件的触发指令，在Telegram客户端使用插件 `InlineModeDemo` 应遵循以下格式:

```bash
@bot_username search:<search content>
```



另外，也可以去掉触发指令 `search:` ，只保留前缀，插件 `InlineModeDemo` 将响应所有`inline_query` 消息：

```yaml
file InlineModeDemo/METADATA

Metadata-version: 1.1
Plugin-name: InlineModeDemo
Command: ?:
Summary: InlineMode插件例子
...
```

此时，在Telegram客户端使用插件 `InlineModeDemo` 应遵循以下格式:

```bash
@bot_username <search content>
```





#### 四、插件模板创建工具

在 `v1.9.20_dev` 及以上版本，可以通过命令行指令**一键创建**插件模板。

* 1.14.1 以前的版本

```python
teelebot -p/--plugin <plugin name>
```

* **1.14.1 以后的版本**

```python
teelebot -mp/--make_plugin <plugin name>
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



#### 六、数据暂存器

在 `v1.16.0` 及以上版本，每个插件将拥有一个用于**临时存储数据**的暂存区，可通过以下方法对暂存区进行操作。

可获得的方法:

* **buffer.status** : 获取数据暂存区的使用情况， 单位为字节
* **buffer.sizeof** : 获取单个插件数据暂存区占用内存大小，单位为字节
* **buffer.read** : 从暂存区读取数据，返回的数据类型为字典
* **buffer.write** : 写入数据到暂存区，写入的数据类型为字典

例：

```python
ok, buf = bot.buffer.status()
ok, buf = bot.buffer.sizeof(plugin_name="")
ok, buf = bot.buffer.read(plugin_name="")
ok, buf = bot.buffer.write(buffer=buf, plugin_name="")
```

**所有方法的参数 `plugin_name` 为可选参数，默认为调用插件的名字**



可通过每个插件的 `METADATA` 文件的`Buffer-permissions` 字段**控制其他插件对本插件暂存区的访问权限** ，格式如下 **(读:写)**：

```yaml
file Hello/METADATA

Metadata-version: 1.1
Plugin-name: Hello
Command: /helloworld
Buffer-permissions: True:False
...
```

**在上面的配置下，其他插件可以读取 `Hello` 插件的暂存区，但是不能修改其暂存区。**

**留空的默认权限为 `False:False`**



#### 七、METADATA文件 （Metadata-version: 1.1）

在 `v1.17.0` 及以上版本，插件包引入了文件 `METADATA` ，以存储插件信息， **此文件在使用插件模板创建工具创建插件时会自动生成**。

以`Hello` 插件为例， `METADATA`文件内容如下：

```python
Metadata-version: 1.1
Plugin-name: Hello
Command: /helloworld
Buffer-permissions: False:False
Version: 1.2.0
Summary: Hello World插件例子
Home-page: https://github.com/plutobell/teelebot
Author: Pluto (github.com/plutobell)
Author-email: hi#ojoll.com (#==@)
License: GPLv3
Keywords: Hello World
Requires-teelebot: >=2.3.0
Requires-dist: 
Source: https://github.com/plutobell/teelebot-plugins
```

其中，`Requires-dist:` 为插件包的依赖（例如：requests），各个依赖间请使用英文字符 **","** 进行分隔。

**另外，在v2.3.0及以上版本，新增了获取和修改插件信息的方法。**

可获得的方法:

* **metadata.read** : 读取插件METADATA信息
* **metadata.write** : 写入插件METADATA信息
* **metadata.template** : 获取METADATA数据模板

例：

```python
ok, data = bot.metadata.read(plugin_name="")
ok, data = bot.metadata.write(metadata=data, plugin_name="")
ok, data = bot.metadata.template(version="")
```





