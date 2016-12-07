#!/usr/bin/env python
# -*- coding=utf-8 -*-
# Author: Zhangrf
# E-mail: 78769488@qq.com
# Create: 2016/12/1
import sys
import time
import json
import paramiko
import threading
from pylsy import pylsytable
from conf.settings import *
from core.MyLogging import logger

exec_cmd_results = []
send_file_results = []
down_file_results = []


class MyThread(threading.Thread):
    """自定义执行命令多线程,  处理客户端的命令, 接收服务端上传的文件, (单独做为一个类的话, 可以在其他模块中直接导入使用)"""
    def __init__(self, target, args):
        super().__init__()
        self.target = target
        self.args = args
        self.item = None

    def run(self):
        func = getattr(self, self.target)
        func(self.args)

    def exec_cmd(self, kwargs):
        try:
            paramiko.util.log_to_file(os.path.join(base_dir, "logs", 'paramiko.log'))
            # 创建SSH对象
            ssh = paramiko.SSHClient()

            # 允许连接不在know_hosts文件中的主机
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            name = kwargs["Name"]
            hostname = kwargs["Host"]
            port = kwargs["Port"]
            username = kwargs["UserName"]
            password = kwargs["PassWord"]
            command = kwargs["command"]
            # 连接服务器
            ssh.connect(hostname=hostname, port=port, username=username, password=password)

            # 执行命令
            stdin, stdout, stderr = ssh.exec_command(command=command)
            out, error = stdout.read(), stderr.read()
            result = out if out else error
            self.item = "[%s-%s] thread done! Result of commands:[%s]" % (name, hostname, command)
            # logger.info(host_cmd.center(150, "-"))
            # logger.info(result.decode())
            global exec_cmd_results
            exec_cmd_results.append((self.item, result.decode()))
            # 关闭连接
            ssh.close()
            time.sleep(0.5)
        except Exception as e:
            exec_cmd_results.append((self.item, e))
            logger.info("Err is: %s" % e)

    def send_file(self, kwargs):
        """
        实现ssh sftp传输文件功能
        :param kwargs: 服务端及文件参数
        :return:
        """
        # logger.info("trans_file:::%s" % kwargs)
        try:
            # 创建Transport对象(session)
            transport = paramiko.Transport((kwargs["Host"], kwargs["Port"]))

            # 连接服务器
            transport.connect(username=kwargs["UserName"], password=kwargs["PassWord"])

            # 创建一个sftp传输文件通道
            sftp = paramiko.SFTPClient.from_transport(transport)

            # 将本地文件上传(复制)到服务端指定的文件(必须包含文件名)
            name = kwargs["Name"]
            hostname = kwargs["Host"]
            local_path = kwargs["local_file"]
            remote_path = kwargs["remote_file"]
            result = sftp.put(localpath=local_path, remotepath=remote_path)
            if result:
                # logger.info("trans_file")
                # logger.info("result==", result)
                self.item = "Send File from [%s] to [%s-%s-%s]" % (local_path, name, hostname, remote_path)
                global send_file_results
                send_file_results.append((self.item, result))
            transport.close()
            time.sleep(1)
        except Exception as e:
            send_file_results.append((self.item, e))
            logger.info("Err is : %s" % e)

    def down_file(self, kwargs):
        """
        实现ssh sftp传输文件功能
        :param kwargs: 服务端及文件参数
        :return:
        """
        # logger.info("trans_file:::%s" % kwargs)
        try:
            # 创建Transport对象(session)
            transport = paramiko.Transport((kwargs["Host"], kwargs["Port"]))

            # 连接服务器
            transport.connect(username=kwargs["UserName"], password=kwargs["PassWord"])

            # 创建一个sftp传输文件通道
            sftp = paramiko.SFTPClient.from_transport(transport)

            # 将本地文件上传(复制)到服务端指定的文件(必须包含文件名)
            name = kwargs["Name"]
            hostname = kwargs["Host"]
            local_path = kwargs["local_file"]
            remote_path = kwargs["remote_file"]
            self.item = "Down File from [%s-%s-%s] to [%s]" % (name, hostname, remote_path, local_path)
            sftp.get(remotepath=remote_path, localpath=local_path)
            global down_file_results
            down_file_results.append((self.item, "Down Ok!"))
            transport.close()
            time.sleep(1)
        except Exception as e:
            down_file_results.append((self.item, e))
            logger.info("Err is : %s" % e)


class MyFabric:
    """
    Fabric 程序
    """
    def __init__(self, conf_path):
        self.conf_path = conf_path
        self.all_hosts = {}
        self.groups = []  # 主机组列表
        self.host_list = []  # 需要操作的主机列表
        self.group_hosts = []  # 主机组包含的主机列表
        self.group_name = None  # 主机组名称
        self.break_flag = False
        self.menu_list = ["查看主机列表", "执行命令", "上传文件", "下载文件", "返回上级", "退出程序"]
        self.menu_dict = {
            "0": "show_host",
            "1": "exec_cmd",
            "2": "send_file",
            "3": "down_file",
            "4": "back",
            "5": "quit"}
        with open(conf_path, "r", encoding="utf-8") as conf_obj:
            self.all_hosts = json.load(conf_obj)
        self.group_or_host()

    def group_or_host(self):
        """
        处理主机组/主机列表/用户选择操作
        :return:
        """
        try:
            while True:
                for index, group_name in enumerate(self.all_hosts):
                    self.groups.append(group_name)
                    print(index, group_name)
                # user_input = "0"
                user_input = input("Chose one group to operate[q=Quit]:\n>>>").strip()  # 选择主机组
                if user_input == "q":
                    self.quit()
                elif not user_input.isdigit():
                    logger.info("Wrong input, try again...")
                    continue
                elif int(user_input) >= len(self.groups):
                    logger.info("Wrong input, try again...")
                    continue
                else:
                    group_name = self.groups[int(user_input)]
                    self.group_hosts = self.all_hosts[group_name]

                    # 后面会对self.host_list 重新赋值, 使用self.host_list = sel.group_hosts 会把self.group_host也修改
                    self.host_list = [host for host in self.group_hosts]

                while True:
                    # 选择操作
                    for num, item in enumerate(self.menu_list):
                        print(num, item)
                    operation = input("Chose your operate\n>>>").strip()
                    # self.group_name = self.groups[int(user_input)]
                    attr = self.menu_dict.get(operation, None)
                    # logger.info("%s-%s" % (attr, operation))
                    if not attr:
                        logger.info("Wrong input, try again...")
                        continue

                    else:
                        func = getattr(self, attr, None)
                        # logger.info(func, operation)
                        if func:
                            func()
                        else:
                            logger.info("There are some err...")
                            continue
                        if self.break_flag:
                            break
        except Exception as e:
            logger.info("Err is: %s" % e)

    def show_host(self):
        """
        打印用户选择的主机组下主机列表信息, 处理用户需要操作的主机列表
        :return:
        """
        attributes = ["ID", "Name", "Host", "Port", "UserName"]
        table = pylsytable(attributes)
        index = 0
        # logger.info("self.group_hosts=== %s" % self.group_hosts)
        for host_info in self.group_hosts:
            table.append_data("ID", index)
            table.append_data("Name", host_info.get("Name", None))
            table.append_data("Host", host_info.get("Host", None))
            table.append_data("Port", host_info.get("Port", None))
            table.append_data("UserName", host_info.get("UserName", None))
            index += 1
        print(table)
        # 选择要操作的主机或全部
        while True:
            user_input = input("input number of the host you want to operate[a=all or '1,3,5', b=Back, "
                               "q=Quit]:\n>>>").strip()
            if user_input == "b":
                break
            elif user_input == "q":
                self.quit()
            elif user_input == "a":
                pass
                # self.host_list = self.group_hosts
            else:
                try:
                    self.host_list.clear()
                    for i in user_input.split(","):
                        self.host_list.append(self.group_hosts[int(i)])
                except Exception as e:
                    logger.info("%s\nWrong input, try again..." % e)
                    continue

            while True:
                # 选择要进行的操作
                for i, item in enumerate(self.menu_list):
                    if i > 0:
                        print(i, item)
                user_input = input("Input your operate\n>>>").strip()
                attr = self.menu_dict.get(user_input, None)
                if not attr:
                    logger.info("Wrong input, try again...")
                    continue
                else:
                    func = getattr(self, attr, None)
                    if func:
                        func()
                    else:
                        logger.info("There are some err...")
                        continue

                    if self.break_flag:
                        break

    def exec_cmd(self):
        """
        处理用户选择执行命令操作
        :return:
        """
        try:
            while True:
                global exec_cmd_results
                exec_cmd_results.clear()
                cmd = input("Input commands which you want to exec on server[b=Back, q=Quit]:\n>>>").strip()
                if cmd == "b":
                    break
                elif cmd == "q":
                    self.quit()
                t_objs = []  # 存线程实例
                for host in self.host_list:
                    host["command"] = cmd
                    t = MyThread(target="exec_cmd", args=host)
                    t_objs.append(t)  # 为了不阻塞后面线程的启动，不在这里join，先放到一个列表里
                    t.start()
                for t in t_objs:
                    t.join()
                logger.info(exec_cmd_results)
                for item in exec_cmd_results:
                    print(item[0].center(150, "-"))
                    print(item[1])
                logger.info("All exec_cmd thread done.")
        except Exception as e:
            logger.info("Error is: %s" % e)

    def send_file(self):
        """
        处理用户选择上传文件操作
        :return:
        """
        # for item in enumerate(self.host_list):
        #     logger.info(item)
        try:
            while True:
                global send_file_results
                send_file_results.clear()
                local_file = input("Input local file of send to server[b=Back, q:quit]:\n>>>").strip()
                if local_file == "b":
                    break
                elif local_file == "q":
                    self.quit()
                remote_file = input("Input remote file [b=Back, q:quit]:\n>>>").strip()
                if remote_file == "b":
                    break
                elif remote_file == "q":
                    self.quit()
                t_objs = []  # 存线程实例
                for host in self.host_list:
                    host["local_file"] = local_file
                    host["remote_file"] = remote_file
                    t = MyThread(target="send_file", args=host)
                    t_objs.append(t)  # 为了不阻塞后面线程的启动，不在这里join，先放到一个列表里
                    t.start()
                for t in t_objs:
                    t.join()
                logger.info(send_file_results)
                for item in send_file_results:
                    print(item[0].center(150, "-"))
                    print(item[1])
                logger.info("All send file thread done")
        except Exception as e:
            logger.info("Error is: %s" % e)

    def down_file(self):
        """
        处理用户选择下载文件操作
        :return:
        """
        # for item in enumerate(self.host_list):
        #     logger.info(item)
        try:
            while True:
                global down_file_results
                down_file_results.clear()
                local_file = input("Input the path on the local host to save file[b=Back, q:quit]:\n>>>").strip()
                if local_file == "b":
                    break
                elif local_file == "q":
                    self.quit()
                remote_file = input("Input the remote file to down [b=Back, q:quit]:\n>>>").strip()
                if remote_file == "b":
                    break
                elif remote_file == "q":
                    self.quit()
                t_objs = []  # 存线程实例
                for host in self.host_list:
                    new_local_file = local_file + "_%s" % host["Host"]  # 区分从哪个IP地址下载的文件
                    host["local_file"] = new_local_file
                    host["remote_file"] = remote_file
                    t = MyThread(target="down_file", args=host)
                    t_objs.append(t)  # 为了不阻塞后面线程的启动，不在这里join，先放到一个列表里
                    t.start()
                for t in t_objs:
                    t.join()
                logger.info(down_file_results)
                for item in down_file_results:
                    print(item[0].center(150, "-"))
                    print(item[1])
                logger.info("All down file thread done")
        except Exception as e:
            logger.info("Error is: %s" % e)

    def back(self):
        self.break_flag = True
        return self.break_flag

    @staticmethod
    def quit():
        sys.exit("You chose quit.")


def main():
    logger.info("Main thread start ....")
    hosts_file = os.path.join(base_dir, "conf", "hosts.json")
    logger.info("配置文件:%s" % hosts_file)
    mf = MyFabric(hosts_file)
    mf.group_or_host()
    logger.info("Main thread stop ...")

if __name__ == '__main__':
    main()

