# coding:utf-8

from appium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from common import global_variable as glv

PLATFROM = 'Android'
APP_PACKAGE = 'com.tencent.mm'
APP_ACTIVITY = 'com.tencent.mm.ui.LauncherUI'
DEVICE_SERVER = 'http://127.0.0.1:4723/wd/hub'
TIMEOUT = 10


class WeChat(object):
    def __init__(self, i, port):
        devices = glv.get('devices')
        self.desired_caps = {
            'platformName': PLATFROM,
            'deviceName': devices[i],
            'udid': devices[i],
            'appPackage': APP_PACKAGE,
            'appActivity': APP_ACTIVITY,
            'noReset': True,
            'chromeOptions': {
                'androidProcess': 'com.tencent.mm:toolsmp'  # 这里注意更改
                # 'androidProcess': 'com.tencent.mm:tools'
            },
            'chromedriverExecutable': '/usr/local/bin/chromedriver',
            'recreateChromeDriverSessions': True,
            'unicodeKeyboard': True,
            'resetKeyboard': True,
            'webContentsDebuggingEnabled': True
        }

        self.driver = webdriver.Remote('http://127.0.0.1:%s/wd/hub' % port, self.desired_caps)
        self.wait = WebDriverWait(self.driver, TIMEOUT)









