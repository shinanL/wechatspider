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
from common import global_variable as glv
from bs4 import BeautifulSoup as bs4


"""h5页面获取历史消息，请求接口响应较慢，且每天只能访问200次，返回json格式数据"""


CONFIG_FILE = '/Users/liushinan/PycharmProjects/wechatspider/bizinfo/bizinfo_config.yaml'

conn = dbutil.connectdb_wechatcluster()

"""时间控制，提取半年之内的2019年1月1日"""
ORIGIN_TIME = 1546272000  # 2019/1/1 0:0:0

analysis_total = []
analysis_consume = []


def get_article(driver, biz):
    logging.info('获取历史文章内容')
    time_start = time.time()
    driver.implicitly_wait(10)
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
    soup = bs4(content, "html.parser")
    basic_soup = soup.find('pre').text
    can_continue = parse_article(biz, basic_soup)
    print('能否继续：'+str(can_continue))
    time_end = time.time()
    sum_time = int(time_end - time_start)
    logging.info('花费时间: %s s' % sum_time)
    analysis_consume.append(sum_time)
    utils.switch_to_context(driver)
    time.sleep(1)
    driver.keyevent(4)
    return can_continue


def set_article(biz, datetime, post_type, msg):
    """
    组装article
    :param biz:
    :param msg:
    :return:
    """
    tmp = msg['content_url'].replace("amp;", '')
    content_url = tmp[0:tmp.find('chksm') - 1]
    source_url = msg['source_url'].replace("amp;", '')
    article = {
        'biz': biz,
        'datetime': datetime,
        'type': post_type,
        'title': msg['title'],
        'digest': msg['digest'],
        'fileid': msg['fileid'],
        'sourceurl': source_url,
        'contenturl': content_url,
        "cover": msg['cover'],
        "author": msg['author'],
        "copyright_stat": msg['copyright_stat'],
        "del_flag": msg['del_flag'],
        "item_show_type": msg['item_show_type'],
        "audio_fileid": msg['audio_fileid'],
        "duration": msg['duration'],
        "play_url": msg['play_url'],
        "malicious_title_reason_id": msg['malicious_title_reason_id'],
        "malicious_content_type": msg['malicious_content_type']
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
    datetime = 0
    if text['errmsg'] == 'ok':
        general_msg_list = text['general_msg_list']
        general_list = json.loads(general_msg_list)['list']
        for msg_list in general_list:
            if 'app_msg_ext_info' in msg_list.keys():
                datetime = msg_list['comm_msg_info']['datetime']
                post_type = msg_list['comm_msg_info']['type']
                # print('发布时间：%d' % datetime)
                msg = msg_list['app_msg_ext_info']
                if msg['title']:
                    articles.append(set_article(biz, datetime,post_type, msg))
                flag = True if msg['is_multi'] == 1 else False

                if flag:
                    multi_app_msg_item_list = msg['multi_app_msg_item_list']
                    for msg2 in multi_app_msg_item_list:
                        articles.append(set_article(biz, datetime, post_type, msg2))
        logging.info('提取%s篇文章' % len(articles))
        # logging.info(articles)
        analysis_total.append(len(articles))
        if len(articles) > 0:
            logging.info('提取文章列表：' % articles)
            dbutil.insert_by_many_content_url(conn, articles)
        else:
            return 'cannot_continue'
        if text['can_msg_continue'] == 1 and datetime > ORIGIN_TIME:
            return 'can_continue'
        else:
            return 'cannot_continue'
    else:
        logging.info('错误信息：%s' % text['errmsg'])
        return 'banned'  # 账号被封


def shard_action(driver):
    logging.info("【开始自动获取公众号所有的历史消息】")
    sql = 'SELECT biz,nickname,history_offset from bizinfo WHERE spider=0 and id between 1 and 58'
    official_accounts = dbutil.query(conn, sql)
    # 进入对话框
    utils.enter_talkbox(driver, 'com.tencent.mm:id/b4m')

    count = 0  # 接口访问计数
    logging.info('查询总量：%d' % len(official_accounts))
    outter_break = False
    for (biz, nickname, offset) in official_accounts:
        if outter_break or count > 180:
            logging.info('接口总访问量：%d' % count)
            break
        time_start = time.time()
        logging.info('----------------当前测试biz：' + str(biz))
        logging.info('----------------当前测试nickname：' + str(nickname))
        # 爬取半年之内的
        while count <= 180:
            count += 1
            bizurl = 'https://mp.weixin.qq.com/mp/profile_ext?action=getmsg&__biz=' \
                     + biz + '&f=json&offset=' + str(offset) + '&count=10' + '\n' + str(offset)  # 发送消息
            utils.send_msg(driver, bizurl)
            # 点击链接
            utils.click_last_msg_in_talkbox(driver, 'com.tencent.mm:id/nl')
            # 获取文章url
            can_continue = get_article(driver, biz)
            # 更新偏移量
            offset += 10
            sql = "update bizinfo set history_offset= '{}' where biz= '{}'".format(offset, biz)
            dbutil.exec_sql(conn, sql)
            logging.info('下一个偏移量：%s' % offset)
            if can_continue == 'cannot_continue':
                time_end = time.time()
                sum_time = int(time_end - time_start)
                logging.info('单个公众号采集历史消息花费时间：%s' % str(sum_time))
                dbutil.update_bizinfo_consume(conn, sum_time, biz)
                break
            elif can_continue == 'banned':
                outter_break = True
                break

    driver.quit()


if __name__ == '__main__':
    logging.info("【基于url的公众文章提取工具】")
    devices_list = ['FA6BJ0305835', 'FA7280301336', 'FA69J0308895']
    glv._init()
    glv.set('devices', devices_list)
    logging.info('当前设备列表：' + str(devices_list))
    idx = 0
    logging.info('选择参数' + str(idx))
    driver = wxdriver.WeChat(idx, 4723 + idx * 2).driver
    driver.implicitly_wait(8)
    shard_action(driver)
    conn.close()

