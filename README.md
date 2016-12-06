# 这是一个利用python3 + paramiko实现的简易类Fabric主机管理程序程序

### 作者介绍：
* author：Zhang Renfang
* E-mail: 78769488@qq.com

### 功能介绍及要求：
1. 运行程序列出主机组或者主机列表
2. 选择指定主机或主机组
3. 选择让主机或者主机组执行命令或者向其传输文件（上传/下载）

### 环境依赖：
* Python3.0 + linux + pylsy + paramiko

### 目录结构：

    ftp_server
    ├── __init__.py
    ├── Fabric.png  # 主要流程图
    ├── README.md
    ├── bin # 入口程序目录
    │   ├── __init__.py
    │   └── Fabric.py # 入口程序
    ├── conf # 配置文件目录
    │   ├── __init__.py
    │   ├── setting.py # 全局变量配置文件
    │   └── hosts.josn # 主机配置文件
    ├── core # 程序核心目录
    │   ├── __init__.py
    │   ├── main.py # 功能核心
    │   └── MyLogging.py # 日志功能模块
    ├── data # 数据文件目录
    └── logs # 日志目录


###运行说明：
* 修改conf/settings.py, 设置修改相关参数
* 修改conf/hosts.json, 按照给定格式, 增加主机组或者主机列表
* 运行bin/Fabric.py, 按照提示进行操作


