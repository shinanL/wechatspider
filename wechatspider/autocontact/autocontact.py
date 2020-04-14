# coding:utf-8
import sys
import time

from common import dbutil, wxdriver, global_variable as glv
from common import utils
import yaml

"""自动关注模块，支持原生界面和h5界面"""

CONFIG_FILE = '/Users/liushinan/PycharmProjects/wechatspider/autocontact/contact_config.yaml'


def read_cofig(filename):
    # curpath = os.path.dirname(os.path.realpath(__file__))
    # yamlpath = os.path.join(curpath, filename)
    with open(filename, 'r') as file:
        return yaml.load(file)


def update_serial(filename, udid, start, end):
    with open(filename) as f:
        doc = yaml.load(f)

    for device in doc:
        if device['udid'] == udid:
            device['start'] = start
            device['end'] = end

    with open(filename, 'w') as f:
        yaml.dump(doc, f)

# pc = input('请输入测试序列号 ：')


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


def shard_action(driver, udid):
    # 每天关注100个
    print("【开始执行，每天自动关注180个公众号】")
    start_id = 0
    end_id = 0
    data = read_cofig(CONFIG_FILE)
    for device in data:
        if(device['udid']) == udid:
            start_id = device['start']
            end_id = device['end']
            break
    print('开始序列号'+str(start_id))
    print('结束序列号'+str(end_id))
    task_file = "/Users/liushinan/PycharmProjects/wechatspider/configs/task.csv"
    contacts = []  # 已关注的公众号
    utils.enter_talkbox(driver, 'com.tencent.mm:id/b4m')

    with open(task_file, 'r', encoding="utf8", errors="ignore") as f:
        for line in f.readlines()[start_id:end_id]:
            line = line.replace("\n", "").split(",")
            id, biz = line[0], line[1]
            print('----------------当前测试序号：' + id + '  当前测试biz：' + str(biz).lstrip('__biz='))
            bizurl = 'https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=' \
                     + biz + '&scene=124#wechat_redirect' + '\n' + id
            # 发送消息
            utils.send_msg(driver, bizurl)
            # 点击链接
            utils.click_last_msg_in_talkbox(driver, 'com.tencent.mm:id/nl')
            # 点击自动关注
            add_contact(driver)
            contacts.append(biz)

    print('已关注的公众号：' + str(contacts))
    # 更新数据库
    conn = dbutil.connectdb_wechatcluster()
    dbutil.insert_by_many_bizinfo_addcontact(conn, contacts)
    conn.close()
    # 更新配置文件
    start_id = end_id
    end_id = end_id+180
    # 写入 yaml 文件
    update_serial(CONFIG_FILE, udid, start_id,end_id)


if __name__ == '__main__':
    print("【基于url的公众文章提取工具】")
    devices_list = ['FA6BJ0305835', 'FA69J0308895', 'FA7280301336']
    glv._init()
    glv.set('devices', devices_list)
    print('当前设备列表：' + str(devices_list))
    idx = int(sys.argv[1])
    print('选择参数' + str(idx))
    driver = wxdriver.WeChat(idx, 4723 + idx * 2).driver
    time.sleep(10)
    shard_action(driver, devices_list[idx])








