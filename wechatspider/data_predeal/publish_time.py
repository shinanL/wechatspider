import math
import time
import numpy as np


from common import dbutil, pltutil
import matplotlib.pyplot as plt
import collections


"""
微信公众号发布时间异常点检测
"""
conn = dbutil.connectdb_wechatcluster()
START_TIME = 1546272000
END_TIME = 1577808000

"""
只是官方媒体的判断
"""

def publish_time(figurename):
    """
    时间维度，公众号发布时间变化率，可以大致看出发布文章的规律
    :param filename: 图例保存名称
    :return:
    """
    date = []

    sql = "SELECT datetime FROM test where datetime between 1546272000 and 1577808000 GROUP BY datetime ORDER BY datetime"
    result = dbutil.query_with_sql(conn, sql)
    for (datetime,) in result:
        tmp = round((datetime - START_TIME) / 3600, 1)  # 以小时为单位
        date.append(tmp)  # 减去最小值
    print(date)
    delta = []  # 变化率
    for i in range(1, len(date)):
        delta.append(round(date[i] - date[i - 1], 1))

    x = list(range(0, len(delta)))
    y = delta
    print(delta)
    plt.scatter(x, y)  # 这里画散点图比较好，
    plt.legend()
    plt.savefig('%s_delta.png' % figurename)
    plt.close()
    # plt.show()



def publish_daily(biz, nickname):
    """
    时间维度和发文数维度。公众号每日发文折线图，找出发文数量突增的点
    :param filename: 公众号昵称
    :return:
    """
    num_map = collections.OrderedDict()  # key为日期如20190102，value为该日发布的文章数
    sql = "SELECT FROM_UNIXTIME(datetime) as stamp, COUNT(*) as num  FROM content where biz = '%s' group by datetime ORDER BY datetime" % biz

    result = dbutil.query_with_sql(conn, sql)
    for (stamp, num) in result:
        ss = str(stamp)
        day = ss.split(' ')[0]  # split取出日期
        print(day)
        num_map.setdefault(day, 0)
        num_map[day] += num

    x = list(range(1, len(num_map.values()) + 1))
    # x = list(num_map.keys())   # 不能以此为坐标轴，画图太稠密

    y = list(num_map.values())
    print(x)
    print(y)
    title = '%s发文数量统计图' % nickname
    xlabel = '时间/天'
    ylabel = '发文数量'
    path = './%s_punish_daily.png' % nickname

    pltutil.plot_single_figure(x, y, title, xlabel, ylabel, path)


def publish_hour(biz, figurename):
    """
    时间维度 和 发布数维度。公众号每小时发文折线图，找出不在规律内的；误差在正负30分钟之内，进行了四舍五入
    :param figurename: 图例名称
    :return:
    """

    map = {}  # key为小时，取值范围为[0,24)，value为小时数的统计

    sql = "SELECT FROM_UNIXTIME(datetime) as stamp, COUNT(*) as num  FROM content where biz = '%s' group by datetime ORDER BY datetime" % biz
    result = dbutil.query_with_sql(conn, sql)
    total = 0
    for (stamp, num) in result:
        total += num
        ss = str(stamp)
        tmp = ss.split(' ')[1].split(':')  # 取出时分秒
        hour = int(tmp[0])
        if int(tmp[1]) > 30:
            hour += 1
        if hour == 24:
            hour = 0
        map.setdefault(hour, 0)
        map[hour] += num

    # 按照键值排序
    x = []
    y = []

    for i in sorted(map):
        print((i, map[i]), end=" ")
        x.append(i)
        y.append(map[i])

    print('\n--------------')

    # print(sorted(map.items(), key=lambda kv: (kv[1], kv[0])))

    print(x)
    print(y)
    title = '%s发布时间分布图' % nickname
    xlabel = '时间/h'
    ylabel = '发文数量'
    path = './%s_punish_hour.png' % nickname

    pltutil.plot_single_figure(x,y, title,xlabel,ylabel,path)




# def publish_hour(figurename):
#     """
#     时间维度 和 发布数维度。公众号每小时发文折线图，找出不在规律内的；误差在正负30分钟之内，进行了四舍五入
#     :param figurename: 图例名称
#     :return:
#     """
#
#     map = collections.OrderedDict()  # key为小时，取值范围为[0,24)，value为小时数的统计
#
#     # sql = "SELECT datetime, COUNT(*) as num  FROM test where datetime between 1546272000 and 1577808000 GROUP BY datetime ORDER BY datetime"
#     sql = "SELECT datetime, COUNT(*) as num  FROM content where biz = '%s' group by datetime ORDER BY datetime" % biz
#     result = dbutil.query_with_sql(conn, sql)
#     total = 0
#     for (datetime, num) in result:
#         total += num
#         time_local = time.localtime(datetime)
#         time_format = time.strftime('%Y%m%d %H:%M:%S', time_local)
#         tmp = time_format.split(' ')[1].split(':')  # 取出时分秒
#         hour = int(tmp[0])
#         if int(tmp[1]) > 30:
#             hour += 1
#         if hour == 24:
#             hour = 0
#         map.setdefault(hour, 0)
#         map[hour] += num
#     # 按照键值排序
#     x = []
#     y = []
#     seed = 0
#     alfa = 0.95
#     init = round(total * 0.05)
#     count = 0
#     while round(seed / total, 2) < alfa:
#         count += 1
#         init -= 50
#         seed = 0
#         for i in sorted(map):
#             if map[i] > init:  # 阈值
#                 seed += map[i]
#     print('迭代次数：%s 阈值：%s 数据：%s 总数：%s  百分比：%s' % (count, init, seed, total, round(seed / total, 2)))
#
#     for i in sorted(map):
#         print((i, map[i]), end=" ")
#         x.append(i)
#         y.append(map[i])
#
#     print('\n--------------')
#
#     print(sorted(map.items(), key=lambda kv: (kv[1], kv[0])))
#
#     print(x)
#     print(y)
#     plt.plot(x, y, marker='o')
#     # plt.scatter(x, y)
#     plt.legend()
#     plt.savefig('%s_hour.png' % figurename)
#     plt.close()
#     plt.show()


def publish_minute(figurename):
    """
    时间维度和发文数维度。公众号发布分钟统计图
    :param figurename:
    :return:
    """
    map = collections.OrderedDict()  # key 为分钟[0000,2400)，value 为该分钟发文数

    sql = "SELECT datetime, COUNT(*) as num FROM test where datetime between 1546272000 and 1577808000 GROUP BY datetime ORDER BY datetime"
    result = dbutil.query_with_sql(conn, sql)
    for (datetime, num) in result:
        time_local = time.localtime(datetime)
        time_format = time.strftime('%Y%m%d %H%M', time_local)
        minute = time_format.split(' ')[1]
        map.setdefault(minute, 0)
        map[minute] += num

    # 按照键值排序
    x = []
    y = []
    abnormal = []
    aa = set()
    for i in sorted(map):
        print((i, map[i]), end=" ")
        x.append(i)
        aa.add(map[i])
        y.append(map[i])
        if map[i] < 7:
            abnormal.append(i)

    print('\n')
    print(abnormal)

    print(len(abnormal))
    print(aa)

    print('\n不同的分钟数 %d ' % len(x))
    # print(x)
    # print(y)
    plt.xticks(np.arange(0, 2400, 30))
    plt.plot(x, y)
    # plt.scatter(x, y)
    plt.legend()
    plt.savefig('%s_minute.png' % figurename)
    plt.show()
    plt.close()

def publish_abnormal_data(figurename):
    """
    时间维度，发文数维度。
    1、统计一天内，不同时间发文数量
    2、画出分布图
    3、以一年内每次发文均值作为阈值，小于此阈值判断为发文时间异常点，推测有突发话题
    4、查找数据库，找出文章集合。
    :param figurename:
    :return:
    """
    map = collections.OrderedDict()  # key 为时分[0000,2400)，value 为该分钟发文数

    sql = "SELECT datetime, COUNT(*) as num FROM test where datetime between 1546272000 and 1577808000 GROUP BY datetime ORDER BY datetime"
    result, n = dbutil.query_with_sql_rowcount(conn, sql)
    total = 0
    for (datetime, num) in result:
        time_local = time.localtime(datetime)
        time_format = time.strftime('%Y%m%d %H%M', time_local)
        minute = time_format.split(' ')[1]  # 取出时分
        map.setdefault(minute, 0)
        map[minute] += num
        total += num
    print('一年内发文次数', n)
    # print(len(map))
    mean = total / n  # 平均每次发文数量
    print('每次发布平均值：', mean)

    # 按照键值排序
    x = []
    y = []
    abnormal = []  # 异常时间点
    for i in sorted(map):
        x.append(i)
        y.append(map[i])
        print((i, map[i]), end=" ")
        if map[i] < mean:  # 小于每次发布数量平均值的认为是异常时间点
            abnormal.append(i)
    # print(x)
    # print(y)
    plt.xticks(np.arange(0, 2400, 30))  # 30个数据一个间隔
    plt.plot(x, y)
    # plt.scatter(x, y)
    plt.legend()
    plt.savefig('%s_minute.png' % figurename)
    plt.show()
    plt.close()

    print('\n')
    print('异常时间点数据：', abnormal)
    print('长度：', len(abnormal))

    aa = set(abnormal)  # 检索异常时间点的数据，这里set是多此一举

    sql = "SELECT title, digest, datetime FROM test where datetime between 1546272000 and 1577808000 ORDER BY datetime"
    result, rowcount = dbutil.query_with_sql_rowcount(conn, sql)
    bb = collections.OrderedDict()
    count = 0
    for (title, digest, datetime) in result:
        time_local = time.localtime(datetime)
        time_format = time.strftime('%Y%m%d %H%M', time_local)
        minute = time_format.split(' ')[1]
        if minute in aa:
            bb.setdefault(time_format.split(' ')[0], 0)
            bb[time_format.split(' ')[0]] += 1
            count += 1
            print(time_format)
            print(title)
            print(digest)
    print('异常数据时间序列：', bb.keys())
    print('异常数据长度：', count)
    print('异常数据百分比 ', round(count / rowcount, 2))


if __name__ == '__main__':
    biz = 'MjM5MzI5NTU3MQ=='
    nickname = '澎湃新闻'

    # publish_time(nickname)
    # publish_daily(nickname)
    # biz = 'MjM5MjAxNDM4MA=='
    # nickname = '人民日报'
    publish_daily(biz, nickname)
    # publish_hour(biz, nickname)
    # publish_minute(nickname)
    # publish_abnormal_data(nickname)

    # 发布异常的文章
    # aa = [1, 0, 13, 8, 19]
    # map = {}
    # for i in aa:
    #     map.setdefault(i, [])
    #
    # sql = "SELECT FROM_UNIXTIME(datetime) as stamp,title,digest FROM test"
    # result = dbutil.query_with_sql(conn, sql)
    # total = 0
    # for (stamp, title, digest) in result:
    #     tmp = str(stamp).split(" ")[1].split(":")
    #     hour = int(tmp[0])
    #     minute = int(tmp[1])
    #     if minute > 30:
    #         hour += 1
    #     if hour in aa:
    #         map[hour].append("%s \\n %s\\n" % (title, digest))
    #
    # for i in map:
    #     print(i)
    #     print(map[i])











