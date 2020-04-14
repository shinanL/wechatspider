
import logging
import time
from urllib import request

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
)


def get_driver_props(driver):
    """
    获取 driver 常用属性
    """
    return driver.get_window_size()['width'], driver.get_window_size()['height']


def swipe_down(driver, duration=600):
    """
    下拉手势
    :param driver:
    :param duration:
    :return:
    """
    width, height = get_driver_props(driver)
    driver.swipe(width * 0.5, height * 0.25, width * 0.5, height * 0.75, duration=duration)
    return True


def swipe_up(driver, duration=600):
    """
    上滑手势
    :param driver:
    :param duration:
    :return:
    """
    width, height = get_driver_props(driver)
    driver.swipe(width * 0.5, height * 0.75, width * 0.5, height * 0.25, duration=duration)
    return True


def sleep(t):
    time.sleep(t)


def switch_to_context(driver, context='NATIVE'):
    """
    切换上下文，这里可能有多个，需要匹配
    :param driver:
    :param context: 取值 WEBVIEW 、NATIVE
    :return: 切换成功返回 True
    """
    contexts = driver.contexts
    for cnt in contexts:
        if context in cnt:
            driver.switch_to.context(cnt)
            # logging.info("切换到：%s", cnt)
            return True
    return False


def switch_to_active_wxapp_window(driver):
    """
    一个 webview 会有多个窗口，切换到当前激活的窗口
    :param driver:
    :return: 切换成功返回 True
    """
    windows = driver.window_handles
    for window in windows:
        driver.switch_to.window(window)
        print(driver.title)
        if ':VISIBLE' in driver.title:
            logging.info("切换到窗口：%s", driver.title)
            return True
    return False


def enter_talkbox(driver, id):
    """
    进入第一个对话框
    :param driver:
    :param id:
    :return:
    """
    logging.info('进入对话框')
    els1 = driver.find_elements_by_id(id)  # 定位到消息列表第一位对话框
    els1[0].click()  # 点击进入对话框


def send_msg(driver, message):
    """
    在对话框发送消息
    :param driver:
    :param message: 指定发送的消息
    :return:
    """
    try:
        els1 = driver.find_elements_by_id("com.tencent.mm:id/alm")  # 定位输入框
        els1[0].send_keys(message)  # 输入消息
        els2 = driver.find_elements_by_id("com.tencent.mm:id/als")  # 定位发送按钮
        els2[0].click()  # 点击发送
    except Exception as e:
        logging.info("定位对话框异常：" + format(e))
        if 'list index out of range' in str(e):
            logging.info('重新进入APP')
            driver.start_activity("com.tencent.mm", "com.tencent.mm.ui.LauncherUI")
            enter_talkbox(driver, 'com.tencent.mm:id/b4m')
            send_msg(driver, message)
        # els4 = driver.find_elements_by_id("com.tencent.mm:id/b47")  # 在未关注完毕点击返回键会弹出关注确认对话框，定位该按钮关注，进行异常处理
        # try:
        #     els4 = driver.find_elements_by_id("com.tencent.mm:id/ayb")  # 在未关注完毕点击返回键会弹出关注确认对话框，定位该按钮关注，进行异常处理
        #     els4[0].click()
        # except:
        #     pass
        # time.sleep(3)
        # driver.back()


def click_last_msg_in_talkbox(driver, id):
    """
    点击对话框最后一个消息
    :param driver:
    :return:
    """
    try:
        els1 = driver.find_elements_by_id(id)  # 定位到最后一个消息框，这个链接点击时要正中靶心，否则打不开
        els1[-1].click()
    except:
        driver.back()
    time.sleep(3)


def refresh(driver):
    """
    点击右上角的三个点进行刷新
    :param driver:
    :return:
    """
    time.sleep(1)
    # 点击右上角的三个点
    driver.tap([(963, 160)])
    time.sleep(1)
    # 点击刷新
    driver.find_element_by_xpath("//android.widget.TextView[contains(@text, '刷新')]").click()
    time.sleep(1)
    driver.tap([(232, 517)])
    time.sleep(3)


def swipe_up_in_native(driver):
    """
    滑动直到页面底部，只适用于原生应用
    :param driver:
    :return:
    """
    while True:
        before = driver.page_source
        print("before 页面信息："+before)
        swipe_up(driver)
        time.sleep(5)
        after = driver.page_source
        print("after 页面信息："+before)
        if before == after:
            break


def swipe_up_in_webview(driver):
    """
    h5页面通过js注入滑动，每滑动十次通过page_source判断滑动到底部
    :param driver:
    :return:
    """
    i = 0
    while True:
        print('滑动第{0}次'.format(i))
        i += 1
        if i % 10 == 0:
            before = driver.page_source
            utils.write_page_soure(i, before)
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
            time.sleep(3*1000)
            after = driver.page_source
            utils.write_page_soure(i+1, before)
            if before == after:
                print("到底部了，滑动终止")
                break
        else:
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")


def swipe_up_with_times(driver, count):
    """
    h5页面通过js注入滑动count次
    :param driver:
    :return:
    """
    i = 0
    while i < count:
        i += 1
        driver.execute_script("window.scrollTo(0,document.body.clientHeight);")
        driver.implicitly_wait(6)


def swipe_up_test(driver):
    """
    h5页面通过js注入滑动，每滑动十次通过判断底部标识判断滑动到底部
    问题：实验发现尚未滑动到底部但是包含已无更多
    :param driver:
    :return:
    """
    i = 0
    while True:
        logging.info('滑动第{0}次'.format(i))
        i += 1
        if i % 10 == 0:
            if i == 20:
                logging.info('滑动第{0}次'.format(i))
            source = driver.page_source
            htmlf = open(str(i) + ".html", 'w')
            htmlf.write(driver.page_source)
            bottom = driver.find_element_by_css_selector("#js_nomore>div>span.tips.js_no_more_msg")
            if bottom.text == '已无更多':
                print("----滑动到底部-----")
                break

            if source.find(u'已无更多') != -1:
                print("----源码包含已无更多，到底部了，滑动终止====")
                break
        else:
            # 这里可能抛出异常，需要定位到点击确定按钮，
            # driver.execute_script("window.scrollTo(0,document.body.clientHeight);")  # 操作频繁被封
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")    # 使用这种滑动比较好，滑动同样的次数，第一种获取200条，第二种获取1000条
        driver.implicitly_wait(8)  # 如果页面已经加载这个延时没有作用
        time.sleep(8)


def get_request(url):
    """
    发送请求
    :param url:
    :return:
    """
    header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko'}
    req = request.Request(url, headers=header_dict)
    request.urlopen(req)


def write_page_soure(name, content):
    htmlf = open(name+".html", 'w')
    htmlf.write(content)




