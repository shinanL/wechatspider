# -*- coding:utf-8 -*-

from selenium import webdriver
import time
import json
import requests
import re
import random
import traceback
from fake_useragent import UserAgent
from common import dbutil

"""
根据搜索关键词获取指定公众号类
"""

user = "your offical account"  # 微信公众号账号
password = "your password of official account"  # 公众号密码
# 设置要爬取的公众号列表
gzlist = ['新华社', '人民网', '环球时报', '参考消息', '瞭望智库', '侠客岛', '中国之声', '都市快报', '新京报评论', '每日精选', '现代快报', '今日话题', '今日评说',
             '宁南山', '冯站长之家', '都市快报', '凤凰网南方都市报', '中国青年报', '北京青年报', '南方都市报', '每日关注', '华尔街见闻', '占豪', '凤凰网', '中央电视台',
             '中国之声', '南方周末', 'Vista看天下', '现代快报', '今日话题', '半月谈', '远方青木', '天涯时事', '后沙', '呦呦鹿鸣', '狐狸罐头', '时事纵横', '政事堂2019',
             '每日读报', '虎嗅APP', '观察者网', '今日焦点透视']

conn = dbutil.connectdb_wechatcluster()


def weChat_login():
    """ 登录微信公众号，获取登录之后的cookies信息保存到本地文本 """
    # 定义一个空的字典，存放cookies内容
    post = {}

    # 用webdriver启动谷歌浏览器
    print("启动浏览器，打开微信公众号登录界面")
    driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver')
    # 打开微信公众号登录页面
    driver.get('https://mp.weixin.qq.com/')
    # 等待5秒钟
    time.sleep(5)
    print("正在输入微信公众号登录账号和密码......")
    # 清空账号框中的内容
    driver.find_element_by_xpath("./*//input[@name='account']").clear()
    # 自动填入登录用户名
    driver.find_element_by_xpath("./*//input[@name='account']").send_keys(user)
    # 清空密码框中的内容
    driver.find_element_by_xpath("./*//input[@name='password']").clear()
    # 自动填入登录密码
    driver.find_element_by_xpath("./*//input[@name='password']").send_keys(password)

    # 在自动输完密码之后需要手动点一下记住我
    print("请在登录界面点击:记住账号")
    time.sleep(10)
    # 自动点击登录按钮进行登录
    driver.find_element_by_xpath("./*//a[@class='btn_login']").click()
    # 拿手机扫二维码！
    print("请拿手机扫描二维码登录公众号")
    time.sleep(20)
    print("登录成功")
    # 重新载入公众号登录页，登录之后会显示公众号后台首页，从这个返回内容中获取cookies信息
    driver.get('https://mp.weixin.qq.com/')
    # 获取cookies
    cookie_items = driver.get_cookies()

    # 获取到的cookies是列表形式，将cookies转成json形式并存入本地名为cookie的文本中
    for cookie_item in cookie_items:
        post[cookie_item['name']] = cookie_item['value']
    cookie_str = json.dumps(post)
    # 覆盖写入
    with open('cookie.txt', 'w+') as f:
        f.write(cookie_str)
    print("cookies信息已保存到本地")


def get_token():
    """获取登录之后的token"""
    # 公众号主页
    url = 'https://mp.weixin.qq.com'
    # 读取上一步获取到的cookies
    with open('cookie.txt', 'r') as f:
        cookie = f.read()
    cookies = json.loads(cookie)

    # 登录之后的微信公众号首页url变化为：https://mp.weixin.qq.com/cgi-bin/home?t=home/index&lang=zh_CN&token=1849751598，从这里获取token信息
    response = requests.get(url=url, cookies=cookies)
    print(str(response.url))
    token = re.findall(r'token=(\d+)', str(response.url))[0]
    print("token=" + token)
    return cookies, token

def get_header():
    # useragent池 随机切换useragent
    ua = UserAgent()
    # 设置headers
    header = {
        "HOST": "mp.weixin.qq.com",
        "User-Agent": ua.random
    }
    return header


def search_biz(query):
    """ 根据guery关键词获取公众号唯一标识、中文昵称、英文昵称、服务类型、头像"""
    # query为要爬取的公众号关键词
    cookies, token = get_token()

    # 搜索微信公众号的接口地址
    search_url = 'https://mp.weixin.qq.com/cgi-bin/searchbiz?'

    # 搜索微信公众号接口需要传入的参数，有三个变量：微信公众号token、随机数random、搜索的微信公众号名字，count最大为10，做多搜索到十个公众号
    offset = 0  # 设置偏移量
    while True:
        query_id = {
            'action': 'search_biz',
            'token': token,
            'lang': 'zh_CN',
            'f': 'json',
            'ajax': '1',
            'random': random.random(),
            'query': query,
            'begin': offset,
            'count': '10'
        }
        # 打开搜索微信公众号接口地址，需要传入相关参数信息如：cookies、params、headers
        search_response = requests.get(search_url, cookies=cookies, headers=get_header(), params=query_id)
        # 搜索到的公众号
        official_accounts = search_response.json().get('list')
        print('搜索到%s个公众号' % str(len(official_accounts)))
        data = []
        for official_account in official_accounts:
            # print('单个公众号：%s' % official_account)
            biz = {
                'biz': official_account.get('fakeid'),
                'nickname': official_account.get('nickname'),
                'classify': 1,
                'service_type': official_account.get('service_type'),
                'round_head_img': official_account.get('round_head_img'),
                'alias': official_account.get('alias')
            }
            data.append(biz)
        print(str(data))
        dbutil.insert_by_many_biz(conn, data)
        offset += 10
        # 随机生成休息时间，防止被封
        sleep_time = random.randint(10, 20)
        time.sleep(sleep_time)
        print('休息%s秒' % str(sleep_time))
        print('下一个偏移量：%d' % offset)


if __name__ == '__main__':
    try:
        # 登录微信公众号，获取登录之后的cookies信息，并保存到本地文本中
        weChat_login()
        for keyword in gzlist:
            search_biz(keyword)
    except Exception as e:
        traceback.print_exc()
