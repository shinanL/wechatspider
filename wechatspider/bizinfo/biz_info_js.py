# coding:utf-8
import os
import sys
import time
import logging
cur_path = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.abspath(os.path.dirname(cur_path) + os.path.sep + ".")
sys.path.append(root_path)
from common import dbutil
from common import utils
from common import wxdriver
from autocontact import autocontact
from common import global_variable as glv
from bs4 import BeautifulSoup as bs4


"""h5页面获取公众号主体信息和历史消息：js注入不断上滑"""

CONFIG_FILE = '/Users/liushinan/PycharmProjects/wechatspider/bizinfo/bizinfo_config.yaml'

class Bizinfo(object):
    def __init__(self):
        self.biz_info = {
            'biz': '',
            'nickname': '',
            'icon_url': '',
            'operator': '',
            'data_url': '',
            'profile_desc': '',
            'article': []
        }

        self.article = {
            'biz': '',
            'title': '',
            'contenturl': '',
            'ext_info': ''
        }


    def getBizInfo(self, driver, biz):
        """
        h5界面 获取公众号主体信息
        :param driver:
        :param biz:
        :return:
        """
        driver.implicitly_wait(6)
        time.sleep(10)
        utils.switch_to_context(driver, 'WEBVIEW_com.tencent.mm:toolsmp')
        handles = driver.window_handles  # 获取当前所有窗口的句柄
        owner_info = ''
        for handle in handles:
            try:
                driver.switch_to.window(handle)
                owner_info = driver.find_element_by_css_selector("body>div.profile_container>div.profile_info.appmsg")
                break
            except Exception as e:
                logging.info("切换窗口：" + format(e))
        # 获取公司主体信息
        # owner_info = driver.find_element_by_css_selector("body>div.profile_container>div.profile_info.appmsg")
        self.biz_info['biz'] = biz
        self.biz_info['nickname'] = owner_info.find_element_by_id("nickname").text
        self.biz_info['icon'] = owner_info.find_element_by_id("icon").get_attribute("src")
        try:
            self.biz_info['operator'] = owner_info.find_element_by_css_selector("#js_verify_info>span").text.split(' ')[
                -1]
        except:
            self.biz_info['operator'] = '个人'
        try:
            self.biz_info['data_url'] = owner_info.find_element_by_css_selector("#js_verify_info>span").get_attribute(
                "data-url")
        except:
            self.biz_info['data_url'] = ''
        self.biz_info['profile_desc'] = owner_info.find_element_by_class_name("profile_desc").text

    def get_article(self, driver, biz):
        time_start = time.time()
        # 获取公众号主体信息
        self.getBizInfo(driver, biz)
        # 滑动到底部
        utils.swipe_up_test(driver)

        logging.info('获取历史文章内容')
        time_start2 = time.time()
        content = driver.page_source
        utils.write_page_soure("data_analysis", content)
        soup = bs4(content, "html.parser")
        basic_soup = soup.find_all(class_="weui_msg_card js_card")
        count = 0
        for i in basic_soup:
            count += 1
            msgid = i.get('msgid')
            loc = 'WXAPPMSG%s' % msgid  # WXIMG图片分享页
            nodes = i.find_all(id=loc)
            if nodes:
                for node in nodes:
                    temp_data = {}
                    temp_data['biz'] = biz
                    temp_data['title'] = node.find(class_="weui_media_title").text.strip()
                    tmp = node.get("hrefs")
                    temp_data['contenturl'] = tmp[0:tmp.find('chksm') - 1]
                    temp_data['ext_info'] = node.find(class_="weui_media_extra_info").text.strip()
                    # logging.info('文章序号：' + str(count) + ' 文章标题:' + temp_data['title'])
                    self.biz_info['article'].append(temp_data)

        total = len(self.biz_info['article'])
        print(str(self.biz_info['article']))
        logging.info('爬取文章数：%s' % total)
        time_end = time.time()
        sum_time = int(time_end - time_start)
        sum_time2 = int(time_end - time_start2)
        logging.info('花费时间: %s s' % sum_time)
        logging.info('花费时间: %s s' % sum_time2)

        # 爬取数量和时间更新到biz表里，
        conn = dbutil.connectdb()
        dbutil.update_bizinfo_total(conn, total, sum_time, biz)
        dbutil.closedb(conn)
        driver.switch_to.context('NATIVE_APP')
        time.sleep(1)
        driver.back()



def writeToDB(art_data):
    conn = dbutil.connectdb()
    biz_param = []
    biz_param.append(art_data.get('biz'))
    biz_param.append(art_data.get('nickname'))
    biz_param.append(art_data.get('operator'))
    biz_param.append(art_data.get('profile_desc'))
    biz_param.append(art_data.get('icon_url'))
    biz_param.append(art_data.get('data_url'))
    # logging.info(biz_param)
    dbutil.insert_bizinfo(conn, biz_param)
    # logging.info(art_data.get('article'))
    dbutil.insert_by_many_content_url(conn, art_data.get('article'))
    dbutil.closedb(conn)


def shard_action(driver, udid):
    logging.info("【开始自动获取公众号所有的历史消息】")
    articldata = Bizinfo()
    # 该历史接口每天能访问200-300次，采集二十个，不能再多
    start_id = 0
    end_id = 0
    task_file = "/Users/liushinan/PycharmProjects/wechatspider/configs/task.csv"
    data = autocontact.read_cofig(CONFIG_FILE)
    for device in data:
        if (device['udid']) == udid:
            start_id = device['start']
            end_id = device['end']
            break
    # 进入对话框
    logging.info('start:'+str(start_id))
    logging.info('end:'+str(end_id))
    utils.enter_talkbox(driver, 'com.tencent.mm:id/b4m')

    with open(task_file, 'r', encoding="utf8", errors="ignore") as f:
        for line in f.readlines()[start_id:end_id]:
            line = line.replace("\n", "").split(",")
            id = line[0]
            biz = line[1]
            logging.info('----------------当前测试序号：' + str(id) + '  当前测试biz：' + str(biz).lstrip('__biz='))
            bizurl = 'https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=' \
                     + biz + '&scene=124#wechat_redirect' + '\n' + id
            # 发送消息
            utils.send_msg(driver, bizurl)
            # 点击链接
            utils.click_last_msg_in_talkbox(driver, 'com.tencent.mm:id/nl')
            # 获取文章url
            articldata.get_article(driver, biz)
            # logging.info('所有数据：'+str(articldata.biz_info))
            # 写入数据库
            writeToDB(articldata.biz_info)

    driver.quit()
    # 更新配置文件
    start_id = end_id
    end_id = end_id + 20
    # 写入 yaml 文件
    autocontact.update_serial(CONFIG_FILE, udid, start_id, end_id)


if __name__ == '__main__':
    # logging.info("【基于url的公众文章提取工具】")
    # devices_list = ['FA6BJ0305835', 'FA7280301336', 'FA69J0308895']
    devices_list = ['FA6BJ0305835', 'FA69J0308895']
    glv._init()
    glv.set('devices', devices_list)
    logging.info('当前设备列表：' + str(devices_list))
    idx = int(sys.argv[1])
    logging.info('选择参数' + str(idx))
    driver = wxdriver.WeChat(idx, 4723 + idx * 2).driver
    articldata = Bizinfo()
    driver.implicitly_wait(10)
    shard_action(driver, devices_list[idx])

