from common import dbutil
import numpy as np
import matplotlib.pyplot as plt

"""
微信公众号点赞量 随时间变化图 和 统计分布图
"""

START_TIME = 1546272000
END_TIME = 1577808000
conn = dbutil.connectdb_wechatcluster()


def like_var_with_time(figurename):
    """
    点赞量随时间变化图 和 点赞量统计分布图
    :param figurename: 一般为公众号昵称
    :return:
    """
    data = []   # 点赞数据
    count = 0   # 超过均值的点赞量

    sql = "SELECT likenum,contenturl FROM test where datetime between 1546272000 and 1577808000 ORDER BY datetime"
    result, rowcount = dbutil.query_with_sql_rowcount(conn, sql)
    for (likenum, contenturl) in result:
        if likenum == '':
            likenum = 0
        elif '万' in likenum:
            print('点赞量过万的文章：', contenturl)
            likenum = float(likenum.split('万')[0]) * 10000
        data.append(int(likenum))
    mean = sum(data) / len(data)
    print('均值', mean)
    for i in data:
        if i > mean:
            count += 1
    print('超过均值的占比', count / len(data))
    # 开始画图  点赞量随时间变化图
    plt.title('Like Information Analysis')
    x = list(range(0, len(data)))
    y = data
    plt.plot(x, y)
    # plt.scatter(x, y)
    plt.legend()  # 显示图例
    plt.savefig('%s_like_vary.png' % figurename)
    plt.close()

    # 去除top5的数据
    data = sorted(data)
    data = data[:len(data)-10]
    mean = sum(data)/len(data)
    print("去除top5之后的均值", mean)
    index = np.searchsorted(data, mean)
    print('超过均值的占比', index / len(data))

    # 点赞量统计分布图
    map = {}
    for i in data:
        map.setdefault(i, 0)
        map[i] += 1
    # 开始画图
    plt.title('Like Distribute Analysis')
    x = []
    y = []
    for i in sorted(map):
        print((i, map[i]), end=" ")
        x.append(i)
        y.append(map[i])
    # plt.plot(x, y)
    plt.scatter(x, y)
    plt.legend()  # 显示图例
    plt.savefig('%s_like_distribute.png' % figurename)
    plt.show()
    plt.close()


if __name__ == '__main__':
    like_vary_with_time('test')



