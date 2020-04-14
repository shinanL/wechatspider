import time
from common import dbutil
import numpy as np
import matplotlib.pyplot as plt
import collections

"""
微信公众号阅读量统计分析
"""
START_TIME = 1546272000
END_TIME = 1577808000
conn = dbutil.connectdb_wechatcluster()


def countDays(date):
    """
    给定日期，计算天数
    :param date: 日期，如20190301
    :return:
    """
    month = int(date[4:6])
    day = int(date[6:8])
    days_of_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    total = 0
    for i in range(month-1):
        total += days_of_month[i]
    return total+day


# 均值 37830
# 超过均值的占比 0.32
def read_vary_with_time(figurename):
    """
        阅读量随时间变化图 和 阅读统计分布图
        :param figurename: 一般为公众号昵称
        :return:
    """
    data = []  # 阅读量数据
    count = 0  # 超过均值的阅读量

    sql = "SELECT readnum FROM test where readnum!='' and datetime between 1546272000 and 1577808000 ORDER BY datetime"
    result, rowcount = dbutil.query_with_sql_rowcount(conn, sql)
    for (readnum,) in result:
        if '万' in readnum:
            readnum = float(readnum.split('万')[0]) * 10000
        data.append(int(readnum))
    mean = sum(data) / len(data)
    print('阅读量均值', mean)
    for i in data:
        if i > mean:
            count += 1
    print('超过均值的占比', count / len(data))
    # 开始画图  阅读量随时间变化图
    plt.title('Read Information Analysis')
    x = list(range(0, len(data)))
    y = data
    plt.scatter(x, y)
    plt.legend()  # 显示图例
    plt.savefig('%s_read_vary.png' % figurename)
    plt.close()

    # 阅读量统计分布图
    map = {}
    for i in data:
        map.setdefault(i, 0)
        map[i] += 1
    # 开始画图
    plt.title('Read Distribute Analysis')
    x = []
    y = []
    for i in sorted(map):
        print((i, map[i]), end=" ")
        x.append(i)
        y.append(map[i])
    plt.plot(x, y)
    # plt.scatter(x, y)
    plt.legend()  # 显示图例
    plt.savefig('%s_read_distribute.png' % figurename)
    plt.show()
    plt.close()


def read_daily(figurename):
    num_map = collections.OrderedDict()  # key为日期如20190102，value为该日的阅读量

    sql = "SELECT DISTINCT(datetime) FROM test where datetime between 1546272000 and 1577808000 ORDER BY datetime"
    result, rowcount = dbutil.query_with_sql_rowcount(conn, sql)
    for (datetime,) in result:
        time_local = time.localtime(datetime)
        time_format = time.strftime('%Y%m%d %H:%M:%S', time_local)
        day = time_format.split(' ')[0]  # split取出日期
        num_map.setdefault(day, 0)
        sql2 = "SELECT readnum FROM test WHERE readnum!='' and datetime = %s" % datetime
        result2 = dbutil.query_with_sql(conn, sql2)
        for (readnum,) in result2:
            if '万' in readnum:
                readnum = float(readnum.split('万')[0]) * 10000
            readnum = int(readnum)
            num_map[day] += readnum

    # 开始画图 每日阅读量随时间变化图
    plt.title('Read Daily Information Analysis')
    x = list(num_map.keys())
    y = np.array(list(num_map.values())) / 100000
    plt.xticks(np.arange(0, len(x), 30))
    plt.plot(x, y)
    # plt.scatter(x, y)
    plt.legend()  # 显示图例
    plt.savefig('%s_read_daily.png' % figurename)
    # plt.show()
    plt.close()


if __name__ == '__main__':
    """
    从澎湃新闻的阅读量统计图上可以看出，阅读量基本稳定，10万+的阅读量主要在头条位置，且采样均匀
    """
    read_vary_with_time('test')
    # read_daily('test')








