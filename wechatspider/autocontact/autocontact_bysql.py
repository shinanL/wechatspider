# coding:utf-8
import sys
import time

from common import dbutil, wxdriver, global_variable as glv
from common import utils

"""自动关注模块，支持原生界面和h5界面"""
"""按照列表关注公众号新闻类100 ，日报类100， 头条类100"""

conn = dbutil.connectdb_wechatcluster()


def add_contact(driver, flag=True):
    """
    在历史消息界面定位关注按钮点击自动关注
    :param flag: True表示在h5界面，False表示在原生界面
    :return:
    """
    # 给出页面加载以及请求响应时间
    driver.implicitly_wait(10)
    if flag:
        # h5界面需要切环境和窗口句柄，即web页签
        utils.switch_to_context(driver, 'WEBVIEW_com.tencent.mm:toolsmp')
        handles = driver.window_handles  # 获取当前所有窗口的句柄
        for handle in handles:
            try:
                driver.switch_to.window(handle)
                driver.find_element_by_id('js_btn_add_contact')  # 定位“关注 ”按钮
                break
            except Exception as e:
                print("已关注公众号或者关注异常：" + format(e))
    try:
        driver.find_element_by_id("js_btn_add_contact").click()
        print('关注成功')
        time.sleep(4)  # 等待关注成功
    except Exception as e:
        print("已关注公众号或者关注异常：" + format(e))
    if flag:
        utils.switch_to_context(driver)
    # 返回对话框
    driver.back()
    time.sleep(1)


def shard_action(driver):
    print("【开始执行，每天自动关注分类公众号】")
    sql = 'SELECT id, biz from bizinfo WHERE addcontact=0 and id <= 80'  # 新闻类
    official_accounts = dbutil.query(conn, sql)
    # 进入对话框
    utils.enter_talkbox(driver, 'com.tencent.mm:id/b4m')

    for (id, biz) in official_accounts:
        bizurl = 'https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=' \
                 + str(biz) + '&scene=124#wechat_redirect' + '\n' + str(id)
        # 发送消息
        utils.send_msg(driver, bizurl)
        # 点击链接
        utils.click_last_msg_in_talkbox(driver, 'com.tencent.mm:id/nl')
        # 点击自动关注
        add_contact(driver)
        dbutil.update_bizinfo_addcontact(conn, biz)
    conn.close()

if __name__ == '__main__':
    print("【基于url的公众文章提取工具】")
    devices_list = ['FA6BJ0305835', 'FA7280301336', 'FA69J0308895']  # 设备列表
    glv._init()
    glv.set('devices', devices_list)
    print('当前设备列表：' + str(devices_list))
    idx = int(sys.argv[1])
    print('选择参数' + str(idx))
    driver = wxdriver.WeChat(idx, 4723 + idx * 2).driver
    time.sleep(10)
    shard_action(driver)







