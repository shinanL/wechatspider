# -*- coding:utf-8 -*-

# 功能：根据关键词获取公众号列表（或根据已有公众号列表进行爬取），遍历爬取一周内更新的公众号文章，获取标题名、摘要，文章url，
# 该方法一方面爬取速度慢，另一方面操作频繁导致系统繁忙获取信息失败
from selenium import webdriver
import time
import json
import requests
import re
import random
import traceback
from fake_useragent import UserAgent
from common import dbutil
# 微信公众号账号
user = "2943039341@qq.com"
# 公众号密码
password = "meihaoxinqing0305"
# 设置要爬取的公众号列表
gzlist = ['财经']
conn = dbutil.connectdb()


# 登录微信公众号，获取登录之后的cookies信息，并保存到本地文本中
def weChat_login():
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
    # query为要爬取的公众号关键词
    cookies, token = get_token()

    # 搜索微信公众号的接口地址
    search_url = 'https://mp.weixin.qq.com/cgi-bin/searchbiz?'

    # 搜索微信公众号接口需要传入的参数，有三个变量：微信公众号token、随机数random、搜索的微信公众号名字，count最大为10，做多搜索到十个公众号
    query_id = {
        'action': 'search_biz',
        'token': token,
        'lang': 'zh_CN',
        'f': 'json',
        'ajax': '1',
        'random': random.random(),
        'query': query,
        'begin': '0',
        'count': '10'
    }
    # 打开搜索微信公众号接口地址，需要传入相关参数信息如：cookies、params、headers
    search_response = requests.get(search_url, cookies=cookies, headers=get_header(), params=query_id)
    # 搜索到的公众号
    official_accounts = search_response.json().get('list')
    print('搜索到%s个公众号' % str(len(official_accounts)))
    data = []
    for official_account in official_accounts:
        biz = {
            'biz': official_account.get('fakeid'),
            'nickname': official_account.get('nickname')
        }
        data.append(biz)
    print(str(data))
    dbutil.insert_by_many_biz(conn, data)
    return official_accounts


# 爬取微信公众号文章，并存在本地文本中
def get_content():

    sql = 'SELECT biz from bizinfo WHERE classify=2 AND spider is null'
    official_accounts = dbutil.query(conn, sql)

    cookies, token = get_token()

    for bizid in official_accounts:
        time_begin = time.time()
        articles = []
        print("开始爬取公众号")
        time_start = time.localtime(time.time())
        std_time = time.strftime("%Y%m%d_%H%M", time_start)
        print('开始时间' + std_time)
        # 获取这个公众号的fakeid，后面爬取公众号文章需要此字段
        print("公众号bizid：%s" % bizid)

        # 微信公众号文章接口地址
        appmsg_url = 'https://mp.weixin.qq.com/cgi-bin/appmsg?'
        # 搜索文章  需要传入几个参数：登录的公众号token、要爬取文章的公众号fakeid、随机数random
        query_id_data = {
            'token': token,
            'lang': 'zh_CN',
            'f': 'json',
            'ajax': '1',
            'random': random.random(),
            'action': 'list_ex',
            'begin': '0',  # 不同页，此参数变化，变化规则为每页加5
            'count': '5',
            'query': '',
            'fakeid': bizid,
            'type': '9'
        }
        # 打开搜索的微信公众号文章列表页
        appmsg_response = requests.get(appmsg_url, cookies=cookies, headers=get_header(), params=query_id_data)
        # 获取文章总数
        max_num = appmsg_response.json().get('app_msg_cnt')
        if max_num is None:
            print("操作频繁，稍后再试======="+str(time.time()))
            time.sleep(10)
            continue
        # 无搜索结果
        if max_num == 0:
            print('无搜索结果')
            continue
        print('文章总数max_num：' + str(max_num))
        # 每页至少有5条，获取文章总的页数，爬取时需要分页爬
        page_num = len(appmsg_response.json().get('app_msg_list'))
        print("页数page_num：" + str(page_num))
        num = int(int(max_num) / 5)
        # 起始页begin参数，往后每页加5
        begin = 0
        while num + 1 > 0:
            query_id_data = {
                'token': token,
                'lang': 'zh_CN',
                'f': 'json',
                'ajax': '1',
                'random': random.random(),
                'action': 'list_ex',
                'begin': '{}'.format(str(begin)),
                'count': '5',
                'query': '',
                'fakeid': bizid,
                'type': '9'
            }
            print('Page turning:------------', begin)

            # 获取每一页文章的标题和链接地址，并写入本地文本中
            query_fakeid_response = requests.get(appmsg_url, cookies=cookies, headers=get_header(), params=query_id_data)
            fakeid_list = query_fakeid_response.json().get('app_msg_list')
            # 操作频繁被禁之后，报异常：TypeError: 'NoneType' object is not subscriptable
            if fakeid_list:
                # update_time = fakeid_list[0].get('update_time')
                # time_diff = int(time.time() - update_time)
                # spider_time = 5 * 24 * 60 * 60
                # # print('time difference=' + str(time_diff))
                # if int(time_diff) > spider_time:
                #     break
                tmp = []
                print('文章数：%s' % str(len(fakeid_list)))
                for item in fakeid_list:
                    link = item.get('link')
                    contenturl = link[0:link.find('chksm') - 1]
                    article = {
                        'biz': bizid,
                        'title': item.get('digest'),
                        'contenturl': contenturl,
                        'datetime': item.get('update_time')
                    }
                    # print('文章title:%s' % item.get('digest'))
                    # print('文章链接:%s' % contenturl)
                    # print(item.get('update_time'))
                    # print(type(item.get('update_time')))
                    articles.append(article)
                    tmp.append(article)
                    # print(str(tmp))
                num -= 1
                begin = int(begin)
                begin += 5
                # print('数组长度：%s' % str(len(tmp)))
                # print(str(tmp))

                dbutil.insert_by_many_content_url(conn, tmp)
            else:
                print("操作太频繁，账号被封，休息三个小时")
                time.sleep(60*60*3)
            # 随机生成休息时间，防止被封
            sleep_time = random.randint(10, 20)
            time.sleep(sleep_time)
            print('休息%s秒' % str(sleep_time))
        time_end = time.time()
        time_consume = int(time_end - time_begin)
        print("一个公众号爬取完成,耗时 %s 秒" % str(time_consume))
        # dbutil.insert_by_many_content_url(conn, articles)
        print('总共爬取文章数：%d' % len(articles))
        dbutil.update_bizinfo_spider(conn, bizid)


if __name__ == '__main__':
    try:
        # 登录微信公众号，获取登录之后的cookies信息，并保存到本地文本中
        weChat_login()
        get_content()

    except Exception as e:
        traceback.print_exc()
