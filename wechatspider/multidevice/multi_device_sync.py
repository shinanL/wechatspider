import time

from appium import webdriver
import yaml
from time import ctime
import multiprocessing
from autocontact import autocontact
from bizinfo import biz_info_js
from comment import article_comment
from common import global_variable as glv

# 读取配置文件
with open('desired_caps.yaml', 'r') as file:
    data = yaml.load(file)


def appium_desired(port, udid):
    desired_caps = {
        'platformName': data['platformName'],
        'deviceName': udid,
        'appPackage': data['appPackage'],
        'noReset': data['noReset'],
        'udid': udid,
        'appActivity': data['appActivity'],
        'chromeOptions': data['chromeOptions'],
        'chromedriverExecutable': data['chromedriverExecutable'],
        'recreateChromeDriverSessions': data['recreateChromeDriverSessions'],
        'unicodeKeyboard': data['unicodeKeyboard'],
        'resetKeyboard': data['resetKeyboard'],
        'webContentsDebuggingEnabled': data['webContentsDebuggingEnabled'],
    }
    driver = webdriver.Remote('http://'+str(data['ip'])+':'+str(port)+'/wd/hub', desired_caps)
    driver.implicitly_wait(3)
    time.sleep(10)
    print('appium port:%s start run %s at %s' % (port, udid, ctime()))

    choice = glv.get('choice')
    print("========choice======="+str(choice))
    # 集成测试用例
    if choice == 1:
        autocontact.shard_action(driver, udid)
    elif choice == 2:
        biz_info_js.shard_action(driver, udid)
    elif choice == 3:
        article_comment.shard_action(driver, udid)

    # return driver


if __name__ == '__main__':

    # 启动多设备执行测试
    print('===devices_start_sync===')

    # 定义desired进程组
    desired_process = []

    # 加载desired进程
    for i in range(len(glv.get('devices'))):
        port = 4723 + 2 * i
        desired = multiprocessing.Process(target=appium_desired, args=(port, glv.get('devices')[i]))
        desired_process.append(desired)

    # 并发启动App
    for desired in desired_process:
        desired.start()
    for desired in desired_process:
        desired.join()