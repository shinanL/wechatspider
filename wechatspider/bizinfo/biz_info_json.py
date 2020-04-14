# coding:utf-8
import json
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


"""h5页面获取历史消息，请求接口响应较慢，且每天只能访问200次，返回json格式数据"""

CONFIG_FILE = '/Users/liushinan/PycharmProjects/wechatspider/bizinfo/bizinfo_config.yaml'

conn = dbutil.connectdb_wechat()


def get_article(driver, biz):
    logging.info('获取历史文章内容')
    time_start = time.time()
    driver.implicitly_wait(15)
    time.sleep(4)
    utils.switch_to_context(driver, 'WEBVIEW_com.tencent.mm:toolsmp')
    handles = driver.window_handles  # 获取当前所有窗口的句柄
    for handle in handles:
        try:
            driver.switch_to.window(handle)
            driver.find_element_by_css_selector("body > pre")
            logging.info('定位成功')
            break
        except Exception as e:
            logging.info("切换窗口：" + format(e))
    content = driver.page_source
    utils.write_page_soure("data_analysis", content)
    soup = bs4(content, "html.parser")
    basic_soup = soup.find('pre').text
    can_continue = parse_article(biz, basic_soup)
    print('能否继续：'+str(can_continue))
    time_end = time.time()
    sum_time = int(time_end - time_start)
    logging.info('花费时间: %s s' % sum_time)

    utils.switch_to_context(driver)
    time.sleep(1)
    driver.keyevent(4)
    return can_continue


def set_article(biz, msg):
    """
    组装article
    :param biz:
    :param msg:
    :return:
    """
    tmp = msg['content_url'].replace("amp;", '')
    contenturl = tmp[0:tmp.find('chksm') - 1]

    article = {
        'biz': biz,
        'title': msg['title'],
        'digest': msg['digest'],
        'sourceurl': msg['source_url'],
        'contenturl': contenturl,
    }
    # logging.info("文章链接：%s" % contenturl)
    return article


def parse_article(biz, json_string):
    """
    解析响应的json格式
    :param biz:
    :param json_string:
    :return:
    """
    text = json.loads(json_string)
    articles = []
    if text['errmsg'] == 'ok':
        general_msg_list = text['general_msg_list']
        general_list = json.loads(general_msg_list)['list']
        for msg_list in general_list:
            if 'app_msg_ext_info' in msg_list.keys():
                msg = msg_list['app_msg_ext_info']
                articles.append(set_article(biz, msg))
                flag = True if msg['is_multi'] == 1 else False
                if flag:
                    multi_app_msg_item_list = msg['multi_app_msg_item_list']
                    for msg2 in multi_app_msg_item_list:
                        articles.append(set_article(biz, msg2))
        logging.info('提取%s篇文章' % len(articles))
        if len(articles) > 0:
            dbutil.insert_by_many_content_url(conn, articles)
        else:
            return False
        return True if text['can_msg_continue'] == 1 else False
    else:
        return False


def shard_action(driver, udid):
    logging.info("【开始自动获取公众号所有的历史消息】")
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

    count = 0  # 接口访问计数

    with open(task_file, 'r', encoding="utf8", errors="ignore") as f:
        for line in f.readlines()[start_id:end_id]:
            line = line.replace("\n", "").split(",")
            id = line[0]
            biz = line[1]
            logging.info('----------------当前测试序号：' + str(id) + '  当前测试biz：' + str(biz).lstrip('__biz='))
            offset = 0
            can_continue = True
            while can_continue and offset <= 130:
                count += 1
                bizurl = 'https://mp.weixin.qq.com/mp/profile_ext?action=getmsg&__biz=' \
                         + biz + '&f=json&offset=' + str(offset) + '&count=10' + '\n' + id                # 发送消息
                utils.send_msg(driver, bizurl)
                # 点击链接
                utils.click_last_msg_in_talkbox(driver, 'com.tencent.mm:id/nl')
                # 获取文章url
                can_continue = get_article(driver, biz)
                offset += 10
                logging.info('下一个偏移量：%s' % offset)
                # 写入数据库

    logging.info('接口总访问量：%s' % count)
    driver.quit()
    # 更新配置文件
    start_id = end_id
    end_id = end_id + 15
    # 写入 yaml 文件
    autocontact.update_serial(CONFIG_FILE, udid, start_id, end_id)


if __name__ == '__main__':
    logging.info("【基于url的公众文章提取工具】")
    # devices_list = ['FA6BJ0305835', 'FA7280301336', 'FA69J0308895']
    devices_list = ['FA6BJ0305835', 'FA69J0308895']
    glv._init()
    glv.set('devices', devices_list)
    logging.info('当前设备列表：' + str(devices_list))
    idx = int(sys.argv[1])
    logging.info('选择参数' + str(idx))
    driver = wxdriver.WeChat(idx, 4723 + idx * 2).driver
    driver.implicitly_wait(8)
    shard_action(driver, devices_list[idx])
    conn.close()