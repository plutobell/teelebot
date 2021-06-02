# 更新日志

#### 2021-06-02 ####

* v1.16.2 : 
  * 完善 Schedule 类
  * 完善 Buffer 类

#### 2021-05-16 ####

* v1.16.0 : 
  * 升级至 Bot API 5.2
    * 方法 sendInvoice 新增参数 max_tip_amount 和 suggested_tip_amounts
    * 方法 sendInvoice 的参数 start_parameter 变为可选
  * 新增方法 getChatMemberStatus
  * 新增 buffer 文件暂存区
  * 配置文件新增参数 buffer_size
  * 修复方法 getUpdates 参数 allowed_updates 无效的bug
  * 修复方法 setWebhook 参数 allowed_updates 无效的bug
  * 修复 webHook 模式下参数 allowed_updates 无效的bug
  * 完善方法 editMessageMedia

#### 2021-03-30 ####

* v1.15.1 : 
  * 修复插件模板创建工具的bug

#### 2021-03-10 ####

* v1.15.0 : 
  * 升级至 Bot API 5.1
    * 配置文件新增字段 updates_chat_member ，用以指定是否接受 chat_member 消息
    * 新增方法 createChatInviteLink
    * 新增方法 editChatInviteLink
    * 新增方法 revokeChatInviteLink
    * 新增消息类型 voice_started、voice_ended、voice_invited
    * 新增消息类型 message__timer_changed
    * 新增消息类型 my_chat_member_data
    * 新增消息类型 chat_member_data
    * 新增消息类型 new_chat_members、left_chat_member
    * 为 sendDice 方法适配新 emoji 动画：bowling
    * 为 kickChatMember 方法增加字段：revoke_messages
    * 为 promoteChatMember 方法增加字段：can_manage_chat、can_manage_voice_chats
  * 其他细节调整

#### 2021-03-03 ####

* v1.14.5 : 
  * 修复插件模板创建工具的bug

#### 2021-01-11 ####

* v1.14.4 : 
  * 修复命令行参数的bug

#### 2020-12-14 ####

* v1.14.3 : 
  * 增强日志
  * 细节优化

#### 2020-12-12 ####

* v1.14.2 : 
  * 移除了配置文件默认插件路径，插件路径现在为必须的字段
  * 移除了默认插件
  * 命令行参数调整
    * 将插件模板创建工具的参数从 -p/--plugin 调整为 -mp/--make_plugin
    * 新增参数 -p/--plugin，用于指定插件路径
  * 完善了插件模板创建工具
  * 修复了通过命令行参数更新配置文件无效的bug
  * 修复了命令行 debug 参数的bug
  * 修复了 Webhook 模式键盘中断的bug
  * 修复了 Polling 模式键盘中断无效的bug
  * 其他细节调整

#### 2020-11-27 ####

* v1.14.1 :
  * Bot类新增方法 timer，单次定时器
  * 修复方法 sendPoll 的bug
  * 修复方法 stopPoll 的bug

#### 2020-11-23 ####

* v1.14.0 :
  * 完全适配 local api server 模式
  * 新增命令行参数 -C/--close 和 -L/--logout，用于配合 local api server 使用
  * 新增方法 getChatCreator，可获取群组创建者的信息
  * 完善 webhook 模式，现在可以根据配置文件自动切换 http 和 https
  * 完善了 handler 模块
  * 完善了 request 模块
  * 配置文件新增字段 cert_key
  * 方法 getFileDownloadPath 适配 local api server 模式
  * 修复运行模式检测的bug
  * 修复Bot类方法sendMediaGroup的bug
  * 其他细节优化

#### 2020-11-19 ####

* v1.13.3 :
  * Bot类新增公共属性 bot_id，总计10个
  * 调整属性 root 命名为 root_id
  * 修复 handler 的bug
* v1.13.2 : 
  * 重构大量代码
  * Bot类公共属性调整为9个
    * root
    * author
    * version
    * plugin_dir
    * plugin_bridge
    * uptime
    * response_times
    * response_chats 
    * response_users
  * 新增配置文件自动生成
  * 新增命令行参数 -k/--key 和 r/--root
  * 新增对Webhook模式非自签证书的支持
  * 完善插件模板创建工具
  * 修复了 bridge 和 pluginRun 的bug
  * 其他细节优化

#### 2020-11-15 ####

* v1.12.0 :
  * 重构代码
  * 完善插件模板创建工具
  * 修复线程池溢出的bug

#### 2020-11-13 ####

* v1.11.5 : 
  * 修复 _pluginRun 的bug
  * 完善消息类型识别

* v1.11.4 : 
  * 调整消息发送类型函数的默认编码
  * 调整方法 add_schedule 的返回值
  * 新增方法 find_schedule，用于查找任务

#### 2020-11-12 ####

* v1.11.3 :
  * 重构 _pluginRun 方法
  * 修复插件 热更新 和 热装载 的bug

* v1.11.2 :
  * 修复 drop_pending_updates 开启后在 Polling 模式下的bug
  * 修复方法 add_schedule 的bug
  * 移除方法 dropPendingUpdates

#### 2020-11-11

* v1.11.1 :
  * 新增周期性任务，可循环定时执行任务
    * 新增方法 add_schedule，用于添加任务至任务池
    * 新增方法 del_schedule，用于从任务池中移除一个任务
    * 新增方法 clear_schedule，用于清空任务池
    * 新增方法 stat_schedule，用于获取任务池的状态：容量、使用情况
  * 修复 dropPendingUpdates 的bug
  * 其他细节优化

#### 2020-11-10 ####

* v1.10.1 :
  * 配置文件新增参数 drop_pending_updates，以控制是否在启动时抛弃所有挂起的更新
  * Bot类新增方法 response_chats 和 response_users
  * 增强插件 Uptime

#### 2020-11-9 ####

* v1.10.0 :
  * 升级至 Bot API 5.0
    * 配置文件新增字段 local_api_server，用以指定本地API服务器地址
    * 新增方法 logOut
    * 新增方法 close
    * 新增方法 unpinAllChatMessages
    * 新增方法 copyMessage
    * 新增方法 sendPoll
    * 新增方法 sendDice
    * 新增方法 addStickerToSet
    * 为部分 消息发送 类型的方法增加字段：allow_sending_without_reply、caption_entities、allow_sending_without_reply
    * 为 unbanChatMember 方法增加字段 only_if_banned
    * 为 deleteWebhook 方法增加字段 drop_pending_updates
    * 为 setWebhook 方法增加字段：ip_address 、drop_pending_updates
    * 为 sendDocument 方法增加字段 disable_content_type_detection
    * 为 sendLocation 方法增加字段：heading、horizontal_accuracy
    * 为 editMessageLiveLocation 方法增加字段：heading、horizontal_accuracy
    * 为 promoteChatMember 方法增加字段 is_anonymous
    * 为 editMessageText 方法增加字段 entities
    * 为 editMessageCaption 方法增加字段 caption_entities
    * 为 sendMessage 方法增加字段 entities
    * 其他细节调整
  * 完善Bot类方法 sendVenue

#### 2020-11-8 ####

* v1.9.20 :
  * 新增插件模板一键创建工具，插件开发更快捷
  * 迁移现存插件到单独存储库，建立官方插件仓库
  * 修复方法 setWebhook 的bug
  * 修复插件 ID 的bug

#### 2020-11-6 ####

* v1.9.19 :
  * Bot类新增方法 path_converter
  * 现存插件适配 path_converter
  * 修复插件 Guard 的bug
  * 优化插件 Menu 和 About

#### 2020-11-5 ####

* v1.9.18 : 
  * 新增根据操作系统生成对应格式的配置文件和插件路径
  * 修复插件 PluginCTL 的bug
  * 调整插件 Guard 的 guardadd 功能的操作权限
  * 更新了一些默认插件

#### 2020-10-31 ####

* v1.9.17 : 
  * 方法 sendMessage 新增字段 disable_web_page_preview
  * 调整 Guard 插件日志消息显示细节

#### 2020-10-29 ####

* v1.9.16 : 
  * 修复 debug模式 失效的问题
  * 插件 Guard 新增操作日志记录

#### 2020-10-24

* v1.9.15 :
  * 调整代码格式，使符合PEP8
  * 提升代码复用率
  * 修复方法 upLoadStickerFile 的bug
  * 修复方法 washUpdates 的bug
  * 插件 Uptime 细节优化

#### 2020-7-31

* v1.9.14 : 
  * 修复插件热更新失效的bug
  * 插件 Top 细节优化

#### 2020-7-29

* v1.9.13 : 
  * 修复影响使用的由插件热更新和热装载引起的bug
  * 新增插件 Whois

#### 2020-7-23

* v1.9.11 : 
  * 优化未安装任何插件场景下的日志消息
  * Guard 插件新增功能：新用户垃圾消息监测以及封禁
  * 修复 Sticker 插件的bug（tgs类型贴纸）

#### 2020-7-22

* v1.9.10 : 
  * 新增插件热更新和热装载场景下的日志消息
  * 修复框架bug
  * 修复 Guard 插件的bug（forward_from_message）

#### 2020-7-18

* v1.9.9 : 
  * 重构debug模式以及日志系统
  * 完善自定义消息字段 `message_type`
  * 细节优化

#### 2020-7-17

* v1.9.6 : 
  * 框架新增在未安装任何插件时的提示消息
  * 修复插件 About 的bug

#### 2020-7-11

* v1.9.5 : 
  * 框架代码优化
  * Guard 插件新增功能：检测并封禁群链接广告

#### 2020-7-4

* v1.9.4 : 优化Bot类代码

#### 2020-6-30

* v1.9.3 : 
  * Bot类新增 **19个** Telegram Bot API方法，Telegram Bot API现存方法已全部实现
  * 完善Bot类方法 `sendLocation` ；修复Bot类方法 `setChatPermissions` 的bug

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