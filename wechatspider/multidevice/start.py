
from time import sleep
import multiprocessing
from multidevice import multi_appium_sync
from multidevice import multi_device_sync
from common import global_variable as glv
import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)


def start_appium_action(port, udid):
    multi_appium_sync.start_appium(port, udid)


def start_devices_action(port, udid):
    multi_device_sync.appium_desired(port, udid)


def appium_start_sync():
    """
    并行启动appium服务
    """
    print('====appium_start_sync=====')

    # 构建appium进程组
    appium_process = []

    # 加载appium进程

    for i in range(len(devices_list)):
        port = 4723 + 2 * i

        appium = multiprocessing.Process(target=start_appium_action, args=(port, devices_list[i]))
        appium_process.append(appium)

    # 启动appium服务
    for appium in appium_process:
        appium.start()
    for appium in appium_process:
        appium.join()

    sleep(5)


def devices_start_sync():
    '''并发启动设备'''
    print('===devices_start_sync===')

    #定义desired进程组
    desired_process = []

    #加载desired进程
    for i in range(len(devices_list)):
        port = 4723 + 2 * i
        desired = multiprocessing.Process(target=start_devices_action, args=(port, devices_list[i]))
        desired.start()
        # desired_process.append(desired)

    #并发启动App
    # for desired in desired_process:
    #     desired.start()
    # for desired in desired_process:
    #     desired.join()


if __name__ == '__main__':
    pc = input('请输入系统 win or mac：')
    choice = input('----------选择程序----------' + '\n'
                        '1、自动关注公众号' + '\n'
                        '2、自动获取公众号历史消息' + '\n'
                        '3、自动获取文章内容及评论' + '\n'
                   )
    # devices_list = ['FA6BJ0305835', 'FA69J0308895', 'FA7280301336']
    # devices_list = ['FA6BJ0305835', 'FA7280301336']
    devices_list = ['FA6BJ0305835', 'FA7280301336']
    # devices_list = ['FA6BJ0305835']
    glv._init()
    glv.set('system', pc)
    glv.set('choice', int(choice))
    glv.set('devices', devices_list)


    # appium_start_sync()
    devices_start_sync()