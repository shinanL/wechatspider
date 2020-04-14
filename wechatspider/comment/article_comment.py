# coding:utf-8
import time
import sys
import os
import logging
from urllib.parse import quote

cur_path = os.path.dirname(os.path.abspath(__file__))
# logging.info(str(cur_path))
root_path = os.path.abspath(os.path.dirname(cur_path) + os.path.sep + ".")
sys.path.append(root_path)
# logging.info(str(root_path))
# logging.info(str(sys.path))

from common import dbutil
from common import global_variable as glv
from common import utils
from common import wxdriver
from bs4 import BeautifulSoup as bs4

conn = dbutil.connectdb_wechatcluster()
base = '/Users/liushinan/wechat/artical'


def get_content_and_comment(driver):
    """
    获取文章内容和评论，并写入数据库
    :return:
    """
    # 给出页面加载以及请求响应时间
    driver.implicitly_wait(3)   # 设置为2秒时可能提取不到用户评论
    # time.sleep(3)
    # h5界面需要切环境及窗口句柄（web页签）
    utils.switch_to_context(driver, 'WEBVIEW_com.tencent.mm:toolsmp')
    # handles = driver.window_handles  # 获取当前所有窗口的句柄
    # for handle in handles:
    #     try:
    #         driver.switch_to.window(handle)
    #         driver.find_element_by_css_selector("#js_article")
    #         # driver.find_element_by_id("js_content")
    #         logging.info('定位成功')
    #         break
    #     except Exception as e:
    #         logging.info("切换窗口：" + format(e))
    #         if 'Connection aborted' in str(e):
    #             logging.info('Connection aborted，程序退出')
    #             driver.quit()
    # 决定要不要跳一下
    # utils.swipe_up_with_times(driver, 1)
    html = driver.page_source
    # html = html.encode()
    utils.switch_to_context(driver)  # 需要切环境点击才能生效
    # time.sleep(1)
    # 返回对话框
    driver.keyevent(4)
    # driver.back()
    # logging.info(type(html))
    return html


def parse_html(url, content):
    """
    解析源码，提取文章内容、用户评论、阅读量、点赞数、发布时间
    :param url:
    :param content:
    :return:
    """
    # time_start = time.time()
    soup = bs4(content, "html.parser")
    # 提取公众号昵称
    nick_name = ""
    try:
        nick_name = soup.find('a', id='js_name').text.strip()
        logging.info('公众号昵称：%s' % nick_name)
        # publish_time = soup.find(class_='rich_media_meta rich_media_meta_text').text
        # publish_time = soup.find('em', id='publish_time').text
        # logging.info('文章发表时间：%s' % publish_time)
    except:
        logging.info('未提取到公众号昵称')

    desc = ''
    strong_content = ''
    color_content = ''
    try:
        share = soup.find(class_='share_notice')  # 分享的视频或者图片
        if share:
            desc = share.text.strip()
        else:
            media_content = soup.find(class_='rich_media_content')
            paragraph = media_content.find_all('p')
            strong_content = ''  # 加粗内容
            color_content = ''  # 加颜色内容
            for p in paragraph:
                strongs = p.find_all('strong')
                colors = p.find_all('span')
                for color in colors:
                    if 'style' in color and 'color' in color.attrs['style']:
                        color_content += color.text.strip()
                        color_content += '\n'
                if strongs:
                    for strong in strongs:
                        strong_content += strong.text.strip()
                        strong_content += '\n'

                desc += p.text.strip()
                desc += '\n'

        # logging.info('文章内容：%s ' % desc)
    except:

        logging.info('未提取到文章内容')

    readnum = ''
    likenum = ''
    comments = []
    try:
        # 底部为阅读原文时，没有阅读量和点赞数
        readnum = soup.find('span', id='readNum3').text
        likenum = soup.find('span', id='likeNum3').text
        logging.info('阅读量：%s' % readnum)
        logging.info('在看：%s' % likenum)
    except:
        logging.info('没有阅读量和点赞数')
    try:
        # 也可能没有用户评论
        discuss_list = soup.find(class_='discuss_list').find_all('li')
        for discuss in discuss_list:
            elected = discuss.find(class_='praise_num').text
            if len(elected) == 0:
                elected = 0
            nickname = discuss.find(class_='nickname').text
            avatar = discuss.find(class_='avatar')['src']
            message = discuss.find(class_='discuss_message_content').text.replace('\n', '')
            comment = {
                'nickname': nickname,
                'elected': elected,
                'avatar': avatar,
                'comment': message
            }
            comments.append(comment)
        # logging.info('用户评论：%s' % comments)
    except:
        logging.info('没有用户评论')
    images = soup.find_all('img')
    links = []
    for image in images:
        link = image.get('data-src')
        if link:
            links.append(link)

    # logging.info('链接：%s' % links)

    rich_message = {
        'nickname': nick_name,
        # 'datetime': publish_time,
        'content': desc,
        'strong_content': strong_content,
        'color_content': color_content,
        'readnum': readnum,
        'likenum': likenum,
        'comment': str(comments),
        'links': str(links),
        'spider': 1
    }
    # 表名
    table_name = 'content'
    conditions = {'contenturl': url}  # 更新所需条件
    # 构造update语句
    sentence1 = 'UPDATE %s SET ' % table_name
    sentence2 = ','.join(['%s=%r' % (k, rich_message[k]) for k in rich_message])
    sentence3 = ' WHERE '
    sentence4 = ' AND '.join(['%s=%r' % (k, conditions[k]) for k in conditions])
    sql = sentence1 + sentence2 + sentence3 + sentence4 + ';'
    dbutil.update_comment(conn, sql)
    # dbutil.update_content_spider(conn, url)
    # time_end = time.time()
    # logging.info('总消耗时间：%d' % int(time_end - time_start))


def shard_action(driver, udid):
    """
    分布式多机并行处理，数据分片
    1、建立设备udid和索引的映射关系
    2、根据数据库ID和索引分发任务到不同的设备上
    :param driver:
    :param udid:
    :return:
    """
    logging.info("【自动获取文章内容和用户评论】")
    # 建立索引
    devices_list = glv.get('devices')
    idx = {}
    i = 0
    for device in devices_list:
        idx[device] = i
        i = i+1
    # 进入对话框
    utils.enter_talkbox(driver, 'com.tencent.mm:id/b4m')
    result = dbutil.shard_content_url(conn)
    logging.info('返回结果条数' + str(len(result)))

    for (id, url) in result:
        # 数据分片
        if id % len(devices_list) != idx[udid]:
            continue
        # index = url.find('scene')
        # if index != -1:
        #     url = url[0:index - 1]
        logging.info('采集文章: ' + str(id) + " " + url)
        if len(url) == 0:
            logging.info('跳过长度为0的url')
            continue
        # 发送消息
        utils.send_msg(driver, url)
        # 点击链接
        utils.click_last_msg_in_talkbox(driver, 'com.tencent.mm:id/nl')
        # 获取文章内容和评论并写入数据库
        html = get_content_and_comment(driver)
        # 在网络延时下提取源码出错，只有122KB，故不更新放到下次重新提取
        # logging.info('源码长度：%d' % len(html))
        # if html and len(html) > 122000:
        if html:
            parse_html(str(url), html)
            # url_encode = quote(str(url), safe='')  # URL编码
            # name = os.path.join(base, url_encode)
            # utils.write_page_soure(name, html)
            # html = conn.escape_string(html)
            # dbutil.insert_content(conn, html, url)

    driver.quit()
    logging.info('共提取 '+str(len(result)/len(devices_list))+' 篇文章')


if __name__ == '__main__':
    # devices_list = ['FA6BJ0305835', 'FA7280301336', 'FA69J0308895']
    devices_list = ['FA6BJ0305835', 'FA7280301336']
    # devices_list = ['FA6BJ0305835']
    glv._init()
    glv.set('devices', devices_list)
    logging.info('当前设备列表：'+str(devices_list))
    idx = 0
    logging.info('选择参数'+str(idx))
    driver = wxdriver.WeChat(idx, 4723+idx*2).driver
    time.sleep(10)
    udid = devices_list[idx]
    shard_action(driver, udid)











