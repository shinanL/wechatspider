# coding=utf-8
import time
import os
import multiprocessing
from multidevice import start
from common import global_variable as glv

"""
Mac命令行后台启动服务
nohup appium -a 127.0.0.1 -p 4730 -U FA6BJ0305835 --no-reset &

"""


def stop_appium(port=4723):
    """
    关闭指定端口appium服务
    :param port: 端口号
    :return:
    """
    pc = glv.get('system')
    if pc.upper() =='WIN':
        p = os.popen('netstat  -ano| findstr %s' % port)
        p0 = p.read().strip()
        print(p0)
        if p0 != '' and 'LISTENING' in p0:
            p1 = int(p0.split('LISTENING')[1].strip()[0:4])  # 获取进程号
            os.popen('taskkill /F /PID %s' % p1)  # 结束进程
            print('appium server已结束')
    elif pc.upper() == 'MAC':
        p = os.popen('lsof -i tcp:%s' % port)
        p0 = p.read()
        print(p0)
        if p0.strip() != '':
            p1 = int(p0.split('\n')[1].split()[1])  # 获取进程号
            os.popen('kill %s' % p1)  # 结束进程
            print('appium server已结束')


def start_appium(port, udid):
    """
    在指定端口开启appium服务
    :param port: 端口号
    :param udid: 设备标识
    :return:
    """
    stop_appium(port)    # 先判断端口是否被占用，如果被占用则关闭该端口号

    bootstrap_port = str(port + 1)

    # 根据系统，启动对应的服务
    cmd_dict = {

        # 'WIN': ' start /b appium -a 127.0.0.1 -p %s -U %s --bootstrap-port %s --log appium.log --local-timezone '
        #        % (port, udid, bootstrap_port),
        # 'MAC': 'nohup appium -a 127.0.0.1 -p %s -U %s --bootstrap-port %s --log appium.log --local-timezone  &'
        #        % (port, udid, bootstrap_port)
        # 'WIN': ' start /b appium -a 127.0.0.1 -p %s --bootstrap-port %s --log appium.log --local-timezone '
        #        % (port, bootstrap_port),
        # 'MAC': 'nohup appium -a 127.0.0.1 -p %s --bootstrap-port %s --log appium.log --local-timezone &'
        #        % (port, bootstrap_port)
        'WIN': ' start /b appium -a 127.0.0.1 -p %s --bootstrap-port %s '
               % (port, bootstrap_port),
        'MAC': 'nohup appium -a 127.0.0.1 -p %s --bootstrap-port %s &'
               % (port, bootstrap_port)
    }
    os.system(cmd_dict[glv.get('system').upper()])
    time.sleep(3)  # 等待启动完成
    print('设备 %s  %s appium server 启动成功' % (udid, port))


if __name__ == "__main__":
    # 传入需要启动的设备列表
    print('====appium_start_sync=====')

    # 构建appium进程组
    appium_process = []

    # 加载appium进程

    for i in range(len(start.devices_list)):
        port = 4723 + 2 * i

        appium = multiprocessing.Process(target= start_appium, args=(port, start.devices_list[i]))
        appium_process.append(appium)

    # 启动appium服务
    for appium in appium_process:
        appium.start()
    for appium in appium_process:
        appium.join()

    time.sleep(3)


